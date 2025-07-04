from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem
from PyQt6.QtGui import QPen, QColor

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class LineElement(GraphicElementBase):
    def create_graphics_item(self):
        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        item = QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
        item.setPen(pen)
        item.setZValue(0)

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    border_color: QColor, border_with: int,
                                    border_style: Qt.PenStyle,
                                    z_value: int = 0,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        pen = QPen(QColor(border_color))
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        item = QGraphicsLineItem(first_point.x(), first_point.y(), second_point.x(), second_point.y())
        item.setPen(pen)
        item.setZValue(z_value)

        item.setFlags(flags)

        return item