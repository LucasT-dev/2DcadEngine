from PyQt6.QtWidgets import QGraphicsScene


class GraphicScene(QGraphicsScene):
    def __init__(self, undo_stack, parent=None):
        super().__init__(parent)          # parent => Qt gère la durée de vie
        self.undo_stack = undo_stack