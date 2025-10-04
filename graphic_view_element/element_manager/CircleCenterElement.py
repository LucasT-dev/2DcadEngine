import uuid

from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPen, QColor, QBrush

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element.resizable_element.CircleResizable import ResizableCircleItem


class CircleCenterElement(GraphicElementBase):

    def __init__(self, center, edge, start, end, style, border_color=QColor(0, 0, 0), border_with=1,
                 border_style=Qt.PenStyle.SolidLine, fill_color=QColor(255, 255, 255), z_value=0, key=0, value=""):
        super().__init__(start, end, style)
        self.center = center
        self.edge = edge
        self.border_color = border_color
        self.border_with = border_with
        self.border_style = border_style
        self.fill_color = fill_color
        self.z_value = z_value
        self.key = key
        self.value = value

    def create_graphics_item(self):
        circle = self._make_circle_rect_from_center(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = ResizableCircleItem(circle) # QGraphicsEllipseItem(circle)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(self.style.get_z_value())

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.style.get_key(), self.style.get_value())

        item.setAcceptHoverEvents(True)

        return item

    @staticmethod
    def create_custom_graphics_item(center: QPointF, edge: QPointF,
                                    border_color: QColor,
                                    border_with: int,
                                    border_style: Qt.PenStyle,
                                    fill_color: QColor,
                                    z_value: int=0,
                                    key: int=0,
                                    value: str= uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        circle = CircleCenterElement._make_circle_rect_from_center(center, edge)

        pen = QPen(border_color)
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        brush = QBrush(fill_color)

        item = ResizableCircleItem(circle) #QGraphicsEllipseItem(circle)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(z_value)

        item.setFlags(flags)

        item.setData(key, value)

        return item

    @staticmethod
    def _make_circle_rect_from_center(center: QPointF, edge: QPointF) -> QRectF:
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        radius = max(dx, dy)
        return QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)