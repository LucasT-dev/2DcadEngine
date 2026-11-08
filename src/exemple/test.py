"""
Banc de test pour MainCad / GraphicViewContainer / GraphicView.

Usage manuel :   python -X faulthandler test_maincad_tabs.py
Usage pytest :   pytest -v test_maincad_tabs.py        (nécessite pytest-qt)

"""
import faulthandler
import gc
import sys
import time
import traceback
import weakref

from PyQt6.QtCore import QEvent, QTimer
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
    QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from exemple.graphic_window_test import GraphicWindow

from scene.MainCad import MainCad


faulthandler.enable()


def flush_deferred_deletes():
    """Force le traitement des deleteLater() puis le GC Python."""
    app = QApplication.instance()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    gc.collect()


class TabTestWindow(QMainWindow):
    """Fenêtre de test : création / fermeture d'onglets MainCad, y compris en rafale."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test MainCad - onglets")
        self.resize(1100, 750)

        self._refs: list[weakref.ref] = []      # pour détecter les fuites
        self._counter = 0
        self._stress_running = False

        # --- Onglets ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_cad_tab)

        # --- Barre de contrôle ---
        self.btn_add = QPushButton("Nouvel onglet")
        self.btn_add.clicked.connect(lambda: self.add_cad_tab())

        self.btn_close = QPushButton("Fermer l'onglet courant")
        self.btn_close.clicked.connect(
            lambda: self.close_cad_tab(self.tabs.currentIndex()))

        self.btn_rulers = QPushButton("Changer position règles")
        self.btn_rulers.clicked.connect(self.toggle_rulers)

        self.spin_cycles = QSpinBox()
        self.spin_cycles.setRange(1, 500)
        self.spin_cycles.setValue(30)

        self.chk_immediate = QCheckBox("Fermer immédiatement (teste la course avec le timer)")
        self.chk_immediate.setChecked(True)

        self.chk_real_cfg = QCheckBox("Configurateur réel")
        self.chk_real_cfg.setChecked(True)

        self.btn_stress = QPushButton("Stress test")
        self.btn_stress.clicked.connect(self.run_stress_test)

        self.btn_leaks = QPushButton("Vérifier les fuites")
        self.btn_leaks.clicked.connect(self.check_leaks)

        bar = QHBoxLayout()
        for w in (self.btn_add, self.btn_close, self.btn_rulers,
                  QLabel("Cycles :"), self.spin_cycles,
                  self.chk_immediate, self.chk_real_cfg,
                  self.btn_stress, self.btn_leaks):
            bar.addWidget(w)
        bar.addStretch(1)

        # --- Journal ---
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(170)

        central = QWidget()
        lay = QVBoxLayout(central)
        lay.addLayout(bar)
        lay.addWidget(self.tabs, 1)
        lay.addWidget(self.log_view)
        self.setCentralWidget(central)

    # ------------------------------------------------------------------ utils
    def log(self, msg: str):
        stamp = time.strftime("%H:%M:%S")
        self.log_view.appendPlainText(f"[{stamp}] {msg}")
        print(msg, flush=True)

    def _make_configurator(self):
        if self.chk_real_cfg.isChecked():
            return GraphicWindow()
        return None

    # --------------------------------------------------------------- onglets
    def add_cad_tab(self, title: str | None = None) -> MainCad | None:
        self._counter += 1
        title = title or f"Vue 2D #{self._counter}"
        try:
            cad = MainCad(configurator=self._make_configurator(), show_ruler=True)
            self._refs.append(weakref.ref(cad))
            idx = self.tabs.addTab(cad, title)
            self.tabs.setCurrentIndex(idx)
            self.log(f"+ onglet '{title}' créé (total : {self.tabs.count()})")
            return cad
        except Exception:
            self.log("ERREUR création onglet :\n" + traceback.format_exc())
            return None

    def close_cad_tab(self, index: int):
        if index < 0 or index >= self.tabs.count():
            return
        cad = self.tabs.widget(index)
        title = self.tabs.tabText(index)
        try:
            self.tabs.removeTab(index)
            if hasattr(cad, "dispose"):
                cad.dispose()
            cad.deleteLater()
            self.log(f"- onglet '{title}' fermé (total : {self.tabs.count()})")
        except Exception:
            self.log("ERREUR fermeture onglet :\n" + traceback.format_exc())

    def toggle_rulers(self):
        cad = self.tabs.currentWidget()
        if cad is None:
            return
        container = cad.g_get_graphic_view
        pos = container.ruler_positions
        h = "top" if pos["horizontal"] == "bottom" else "bottom"
        v = "right" if pos["vertical"] == "left" else "left"
        container.set_ruler_position(horizontal=h, vertical=v)
        self.log(f"règles -> horizontal={h}, vertical={v}")

    # ----------------------------------------------------------- stress test
    def run_stress_test(self):
        if self._stress_running:
            return
        self._stress_running = True
        self.btn_stress.setEnabled(False)

        total = self.spin_cycles.value()
        immediate = self.chk_immediate.isChecked()
        state = {"i": 0}
        self.log(f"=== Stress test : {total} cycles "
                 f"({'fermeture immédiate' if immediate else 'fermeture après 50 ms'}) ===")

        def step():
            if state["i"] >= total:
                finish()
                return
            state["i"] += 1
            cad = self.add_cad_tab(f"stress {state['i']}")
            if cad is None:
                finish()
                return
            idx = self.tabs.indexOf(cad)
            if immediate:
                # Ferme AVANT que le timer d'init ait pu s'exécuter
                self.close_cad_tab(idx)
                QTimer.singleShot(0, step)
            else:
                QTimer.singleShot(50, lambda: (self.close_cad_tab(self.tabs.indexOf(cad)),
                                               QTimer.singleShot(0, step)))

        def finish():
            self._stress_running = False
            self.btn_stress.setEnabled(True)
            self.log("=== Stress test terminé sans crash ===")
            QTimer.singleShot(200, self.check_leaks)

        step()

    # ---------------------------------------------------------------- fuites
    def check_leaks(self):
        flush_deferred_deletes()
        alive = [r for r in self._refs if r() is not None]
        open_tabs = self.tabs.count()
        leaked = len(alive) - open_tabs
        if leaked > 0:
            self.log(f"FUITE possible : {leaked} MainCad encore en mémoire "
                     f"({len(alive)} vivants pour {open_tabs} onglets ouverts)")
        else:
            self.log(f"OK : aucune fuite ({len(alive)} vivants = {open_tabs} onglets ouverts)")


# ---------------------------------------------------------------------------
# Tests automatiques (pytest-qt)
# ---------------------------------------------------------------------------
def _make(qtbot, configurator=None, show_ruler=True):
    cad = MainCad(configurator=configurator, show_ruler=show_ruler)
    qtbot.addWidget(cad)
    return cad


def test_creation_sans_configurateur(qtbot):
    cad = _make(qtbot)
    assert cad.g_get_view is not None
    assert cad.g_get_scene is cad.g_get_view.scene()


def test_creation_sans_regles(qtbot):
    cad = _make(qtbot, show_ruler=False)
    assert cad.g_get_graphic_view.h_ruler is None


def test_configurateur_execute_apres_affichage(qtbot):
    calls = []

    class Cfg:
        def init(self, maincad):
            calls.append(maincad.g_get_view.width())

    cad = _make(qtbot, configurator=Cfg())
    assert calls == []                       # pas avant le show
    cad.show()
    qtbot.waitUntil(lambda: len(calls) == 1, timeout=2000)
    assert calls[0] > 0                      # taille réelle connue


def test_configurateur_execute_une_seule_fois(qtbot):
    calls = []

    class Cfg:
        def init(self, maincad):
            calls.append(1)

    cad = _make(qtbot, configurator=Cfg())
    cad.show(); cad.hide(); cad.show()
    qtbot.wait(100)
    assert len(calls) == 1


def test_exception_configurateur_ne_plante_pas(qtbot):
    class Cfg:
        def init(self, maincad):
            raise RuntimeError("boom")

    cad = _make(qtbot, configurator=Cfg())
    cad.show()
    qtbot.wait(100)                          # ne doit pas lever


def test_fermeture_avant_init(qtbot):
    """Le cas qui plantait : fermeture avant l'exécution du timer."""
    cad = MainCad(configurator=GraphicWindow())
    cad.show()
    cad.dispose()
    cad.deleteLater()
    flush_deferred_deletes()
    qtbot.wait(50)                           # le timer ne doit rien déclencher


def test_dispose_idempotent(qtbot):
    cad = _make(qtbot)
    cad.dispose()
    cad.dispose()


def test_changement_position_regles(qtbot):
    cad = _make(qtbot)
    cad.show()
    container = cad.g_get_graphic_view
    view_before = container.view
    h_before = container.h_ruler

    for h in ("top", "bottom", "top"):
        for v in ("left", "right", "left"):
            container.set_ruler_position(horizontal=h, vertical=v)

    assert container.view is view_before       # la vue n'est pas recréée
    assert container.h_ruler is h_before       # les règles non plus
    assert container.view.parent() is container


def test_plusieurs_instances_independantes(qtbot):
    a, b = _make(qtbot), _make(qtbot)
    assert a.g_get_scene is not b.g_get_scene
    assert a.g_get_history is not b.g_get_history


def test_creation_fermeture_en_rafale(qtbot):
    for _ in range(25):
        cad = MainCad(configurator=GraphicWindow())
        cad.show()
        cad.dispose()
        cad.deleteLater()
    flush_deferred_deletes()
    qtbot.wait(50)


def test_pas_de_fuite(qtbot):
    cad = MainCad(configurator=None)
    ref = weakref.ref(cad)
    cad.show()
    cad.dispose()
    cad.deleteLater()
    del cad
    flush_deferred_deletes()
    assert ref() is None, "MainCad est encore référencé quelque part"


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TabTestWindow()
    win.show()
    win.add_cad_tab()
    sys.exit(app.exec())