from typing import List

from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
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

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        return item

    @staticmethod
    def create_custom_graphics_item(center: QPointF, edge: QPointF,
                                    border_color: QColor,
                                    border_with: int,
                                    border_style: Qt.PenStyle,
                                    fill_color: QColor,
                                    z_value: int=0,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        circle = CircleCenterElement._make_circle_rect_from_center(center, edge)

        pen = QPen(border_color)
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        brush = QBrush(fill_color)

        item = QGraphicsEllipseItem(circle)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(z_value)

        item.setFlags(flags)

        return item

    @staticmethod
    def _make_circle_rect_from_center(center: QPointF, edge: QPointF) -> QRectF:
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        radius = max(dx, dy)
        return QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)