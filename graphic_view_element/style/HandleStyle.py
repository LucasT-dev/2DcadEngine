from PyQt6.QtGui import QColor, QPen, QBrush


class HandleStyle:
    SIZE = 8
    FILL_COLOR = QColor(255, 255, 255, 0)
    BORDER_COLOR = QColor(0, 255, 0, 255)
    HOVER_COLOR = QColor(0, 150, 255)
    BORDER_WIDTH = 1
    _instances = []

    @classmethod
    def register(cls, handle):
        cls._instances.append(handle)

    @classmethod
    def apply_style(cls, painter, hover=False):
        color = cls.HOVER_COLOR if hover else cls.FILL_COLOR
        brush = QBrush(color)
        pen = QPen(cls.BORDER_COLOR)
        pen.setWidth(cls.BORDER_WIDTH)
        painter.setBrush(brush)
        painter.setPen(pen)

    @classmethod
    def refresh_all(cls):
        for h in cls._instances:
            h.update()

    @classmethod
    def refresh_one(cls, handle):
        handle.update()