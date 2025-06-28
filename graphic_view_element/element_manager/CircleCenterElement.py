from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui import QPen, QColor, QBrush

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class CircleCenterElement(GraphicElementBase):
    def create_graphics_item(self):
        rect = self._make_circle_rect_from_center(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = QGraphicsEllipseItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(0)
        return item

    def _make_circle_rect_from_center(self, center: QPointF, edge: QPointF) -> QRectF:
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        radius = max(dx, dy)
        return QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)