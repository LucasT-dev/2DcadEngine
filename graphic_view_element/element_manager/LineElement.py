import uuid

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPen, QColor

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element.resizable_element.LineResizable import ResizableLineItem


class LineElement(GraphicElementBase):

    def create_graphics_item(self):

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        item = ResizableLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y(), scene=None) # QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
        item.setPen(pen)
        item.setZValue(self.style.get_z_value())

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.style.get_key(), self.style.get_value())

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    border_color: QColor, border_with: int,
                                    border_style: Qt.PenStyle,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        pen = QPen(QColor(border_color))
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        item = ResizableLineItem(first_point.x(), first_point.y(), second_point.x(), second_point.y())
        item.setPen(pen)
        item.setZValue(z_value)

        item.setFlags(flags)

        item.setData(key, value)

        return item