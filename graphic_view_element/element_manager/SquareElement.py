from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPen, QColor, QBrush

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class SquareElement(GraphicElementBase):
    def create_graphics_item(self):
        dx = self.end.x() - self.start.x()
        dy = self.end.y() - self.start.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        corner = QPointF(self.start.x() + dx, self.start.y() + dy)
        rect = QRectF(self.start, corner).normalized()

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = QGraphicsRectItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(0)
        return item