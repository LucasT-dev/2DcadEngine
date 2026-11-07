import logging

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QUndoStack
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from scene.GraphicScene import GraphicScene
from scene.GraphicView import GraphicViewContainer

log = logging.getLogger(__name__)

class MainCad(QWidget):

    def __init__(self, configurator=None, show_ruler=True, parent=None):
        print("maincad")
        super().__init__(parent)


        self._configurator = configurator
        self._initialized = False
        self._disposed = False

        # Pile d'historique
        self.undo_stack = QUndoStack(self)
        self._scene = GraphicScene(self.undo_stack, self)

        # Vue avec règles en bas et à droite
        self._graphic_view = GraphicViewContainer(
            self._scene,
            show_ruler=show_ruler,
            ruler_positions={"horizontal": "bottom", "vertical": "left"},
            parent=self  # <-- AJOUTEZ CECI
        )

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._graphic_view)

        # Timer enfant de self : détruit avec le widget, donc jamais de callback orphelin
        self._init_timer = QTimer(self)
        self._init_timer.setSingleShot(True)
        self._init_timer.timeout.connect(self._run_configurator)

    # Initialisation différée au premier affichage (taille réelle connue)
    def showEvent(self, event):
        super().showEvent(event)
        if not self._initialized:
            self._initialized = True
            self._init_timer.start(0)

    def _run_configurator(self):
        if self._disposed:
            return
        self.g_init_engine()

    def g_init_engine(self):
        """Appelle la configuration si un configurateur est passé."""
        if self._configurator is not None:
            try:
                self._configurator.init(self)
            except Exception:
                log.exception("Erreur dans le configurateur graphique")

    # Nettoyage
    def dispose(self):
        if self._disposed:
            return
        self._disposed = True
        self._init_timer.stop()
        self._graphic_view.dispose()
        self._scene.clear()
        self.undo_stack.clear()

    # --- API ---
    @property
    def g_get_view(self):            return self._graphic_view.view
    @property
    def g_get_graphic_view(self):    return self._graphic_view
    @property
    def g_get_scene(self):           return self._scene
    @property
    def g_get_history(self):         return self.undo_stack
    @property
    def g_get_configurator(self):    return self._configurator

