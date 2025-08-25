import uuid

from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPen, QColor, QBrush

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element.resizable_element.SquareResize import ResizableSquareItem


class SquareCenterElement(GraphicElementBase):

    def create_graphics_item(self):
        square = self._make_square_from_center(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = ResizableSquareItem(square)
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


        square = SquareCenterElement._make_square_from_center(first_point, second_point)

        pen = QPen(border_color)
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        brush = QBrush(fill_color)

        item = ResizableSquareItem(square)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(z_value)

        item.setFlags(flags)

        item.setData(key, value)

        return item

    @staticmethod
    def _make_square_from_center(center: QPointF, edge: QPointF) -> QRectF:
        dx = edge.x() - center.x()
        dy = edge.y() - center.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        return QRectF(center.x() - dx, center.y() - dy, 2 * dx, 2 * dy).normalized()