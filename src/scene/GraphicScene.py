from PyQt6.QtWidgets import QGraphicsScene

__all__ = ["GraphicView", "GraphicScene"]
__version__ = "0.1.0"

class GraphicScene(QGraphicsScene):
    def __init__(self, undo_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.undo_stack = undo_stack