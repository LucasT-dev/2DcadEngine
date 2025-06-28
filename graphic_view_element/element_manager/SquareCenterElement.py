from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QColor, QBrush

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class SquareCenterElement(GraphicElementBase):
    def create_graphics_item(self):
        square = self._make_square_from_center(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = QGraphicsRectItem(square)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(0)
        return item

    def _make_square_from_center(self, center: QPointF, edge: QPointF) -> QRectF:
        dx = edge.x() - center.x()
        dy = edge.y() - center.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        return QRectF(center.x() - dx, center.y() - dy, 2 * dx, 2 * dy).normalized()