from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QUndoStack
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from libs.cadengine.scene.GraphicScene import GraphicScene
from libs.cadengine.scene.GraphicView import GraphicViewContainer


class MainCad(QWidget):

    def __init__(self, configurator=None, show_ruler=True):
        super().__init__()

        # --- Pile d'historique ---
        self._configurator = configurator
        self.undo_stack = QUndoStack(self)

        # --- Crée la scène avec Undo intégré ---
        self._scene = GraphicScene(self.undo_stack)

        # Vue avec règles en bas et à droite
        self._graphic_view = GraphicViewContainer(
            self._scene,
            show_ruler=show_ruler,
            ruler_positions={"horizontal": "bottom", "vertical": "left"}
        )

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._graphic_view)

        # Appeler initEngine APRES construction complète
        QTimer.singleShot(0, self.g_init_engine)


    # --- API pour accéder à la vue ou la scène ---
    @property
    def g_get_view(self):
        return self._graphic_view.view

    @property
    def g_get_graphic_view(self):
        return self._graphic_view

    @property
    def g_get_scene(self):
        return self._scene

    @property
    def g_get_history(self):
        return self.undo_stack

    @property
    def g_get_configurator(self):
        return self._configurator

    def g_init_engine(self):
        """Appel la configuration si un configurateur est passé"""
        if self._configurator is not None:
            self._configurator.init(self)