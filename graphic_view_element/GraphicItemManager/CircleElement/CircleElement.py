import uuid

from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPen, QColor, QBrush, QTransform

from graphic_view_element.GraphicItemManager.CircleElement.CircleResizable import CircleResizable
from graphic_view_element.GraphicItemManager.GraphicElementObject import ElementObject


class CircleElement(ElementObject):

    def create_graphics_item(self, first_point: QPointF, second_point: QPointF):

        dx = second_point.x() - first_point.x()
        dy = second_point.y() - first_point.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        corner = QPointF(first_point.x() + dx, first_point.y() + dy)
        circle = QRectF(first_point, corner).normalized()

        pen = QPen(QColor(self.get_style().get_border_color()))
        pen.setWidth(self.get_style().get_border_width())
        pen.setStyle(self.get_style().get_border_style())

        brush = QBrush(QColor(self.get_style().get_fill_color()))

        item = CircleResizable(circle)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(self.get_style().get_z_value())

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable

        )
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        item.setData(self.get_style().get_key(), self.get_style().get_value())

        item.setAcceptHoverEvents(True)

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    border_color: QColor, border_width: int,
                                    border_style: Qt.PenStyle, fill_color: QColor,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    transform: QTransform = QTransform(),
                                    visibility: bool = True,
                                    scale: float = 1.0,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        dx = second_point.x() - first_point.x()
        dy = second_point.y() - first_point.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        corner = QPointF(first_point.x() + dx, first_point.y() + dy)

        print(f"FIRST POINT : {first_point}")
        print(f"CORNER POINT : {corner}")

        circle = QRectF(first_point, corner).normalized()

        pen = QPen(border_color)
        pen.setWidth(border_width)
        pen.setStyle(border_style)

        brush = QBrush(fill_color)

        item = CircleResizable(circle)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(z_value)
        item.setTransform(transform)
        item.setVisible(visibility)
        item.setScale(scale)

        item.setFlags(flags)

        item.setData(key, value)

        return item
