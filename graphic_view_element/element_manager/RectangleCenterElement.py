import uuid

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element.resizable_element.RectangleResize import ResizableRectangleItem


class RectangleCenterElement(GraphicElementBase):
    def create_graphics_item(self):
        rect = self._make_rect_from_center(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = ResizableRectangleItem(rect) #QGraphicsRectItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
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
                                    border_style: Qt.PenStyle, fill_color: QColor,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        rect = RectangleCenterElement._make_rect_from_center(first_point, second_point)

        pen = QPen(border_color)
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        brush = QBrush(fill_color)

        item = ResizableRectangleItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(z_value)

        item.setFlags(flags)

        item.setData(key, value)

        item.setAcceptHoverEvents(True)

        return item

    @staticmethod
    def _make_rect_from_center(center: QPointF, edge: QPointF) -> QRectF:
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        return QRectF(center.x() - dx, center.y() - dy, 2 * dx, 2 * dy)