import uuid

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPen, QColor

from graphic_view_element.GraphicItemManager.GraphicElementObject import ElementObject
from graphic_view_element.GraphicItemManager.LineElement.LineResizable import LineResizable


class LineElement(ElementObject):

    def create_graphics_item(self, first_point: QPointF, second_point: QPointF):

        pen = QPen(QColor(self.get_style().get_border_color()))
        pen.setWidth(self.get_style().get_border_width())
        pen.setStyle(self.get_style().get_border_style())

        item = LineResizable(first_point.x(), first_point.y(), second_point.x(), second_point.y()) # QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
        item.setPen(pen)
        item.setZValue(self.get_style().get_z_value())

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.get_style().get_key(), self.get_style().get_value())

        return item

    def create_custom_graphics_item(self, first_point: QPointF, second_point: QPointF,
                                    border_color: QColor, border_width: int,
                                    border_style: Qt.PenStyle,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        pen = QPen(QColor(border_color))
        pen.setWidth(border_width)
        pen.setStyle(border_style)

        item = LineResizable(first_point.x(), first_point.y(), second_point.x(), second_point.y())
        item.setPen(pen)
        item.setZValue(z_value)

        item.setFlags(flags)

        item.setData(key, value)

        return item