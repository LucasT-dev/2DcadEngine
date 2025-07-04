from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtCore import QRectF, QPointF, Qt
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

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    border_color: QColor, border_with: int,
                                    border_style: Qt.PenStyle, fill_color: QColor,
                                    z_value: int = 0,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        dx = first_point.x() - first_point.x()
        dy = second_point.y() - second_point.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        corner = QPointF(first_point.x() + dx, first_point.y() + dy)
        rect = QRectF(first_point, corner).normalized()

        pen = QPen(border_color)
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        brush = QBrush(fill_color)

        item = QGraphicsRectItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(z_value)

        item.setFlags(flags)

        return item