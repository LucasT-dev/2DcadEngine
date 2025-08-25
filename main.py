from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QUndoStack
from PyQt6.QtWidgets import QMainWindow

from scene.GraphicScene import GraphicScene
from scene.GraphicView import GraphicViewContainer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # --- Pile d'historique ---
        self.undo_stack = QUndoStack(self)

        # --- Crée la scène avec Undo intégré ---
        self._scene = GraphicScene(self.undo_stack)

        # Vue avec règles en bas et à droite
        self._graphic_view = GraphicViewContainer(
            self._scene,
            show_ruler=True,
            ruler_positions={"horizontal": "bottom", "vertical": "left"}
        )

        # --- Configuration fenêtre ---
        self.setWindowTitle("Moteur de dessin 2D")
        self.setCentralWidget(self._graphic_view)
        self.resize(800, 600)

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

    def g_init_engine(self):
        """
        Méthode appelée à la fin de l'init pour que l'utilisateur
        puisse surcharger s’il veut configurer son moteur.
        """
        pass