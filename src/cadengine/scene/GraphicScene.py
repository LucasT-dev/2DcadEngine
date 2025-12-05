from PyQt6.QtWidgets import QGraphicsScene

class GraphicScene(QGraphicsScene):
    def __init__(self, undo_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.undo_stack = undo_stack