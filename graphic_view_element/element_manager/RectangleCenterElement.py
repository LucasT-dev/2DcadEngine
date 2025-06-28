from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsRectItem

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class RectangleCenterElement(GraphicElementBase):
    def create_graphics_item(self):
        rect = self._make_rect_from_center(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = QGraphicsRectItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(0)
        return item

    def _make_rect_from_center(self, center: QPointF, edge: QPointF) -> QRectF:
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        return QRectF(center.x() - dx, center.y() - dy, 2 * dx, 2 * dy)