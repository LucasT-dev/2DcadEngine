import uuid

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsItem

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element.resizable_element.LineResizable import ResizableLineItem
from graphic_view_element.resizable_element.RightLineResizable import ResizableRightLineItem


class RightLineElement(GraphicElementBase):

    def create_graphics_item(self):
        # Snap de la fin de ligne*
        snapped_end = snap_to_axis(self.start, self.end)

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        item = ResizableRightLineItem(
            self.start.x(), self.start.y(),
            snapped_end.x(), snapped_end.y(),
            scene=None
        )

        item.setPen(pen)
        item.setZValue(self.style.get_z_value())

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
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):
        # Snap sur axe horizontal ou vertical
        snapped_end = snap_to_axis(first_point, second_point)

        pen = QPen(QColor(border_color))
        pen.setWidth(border_with)
        pen.setStyle(border_style)

        item = ResizableRightLineItem(first_point.x(), first_point.y(),
                                 snapped_end.x(), snapped_end.y())
        item.setPen(pen)
        item.setZValue(z_value)
        item.setFlags(flags)
        item.setData(key, value)

        return item

def snap_to_axis(p1: QPointF, p2: QPointF) -> QPointF:
    """
    Retourne un nouveau p2 aligné horizontalement ou verticalement
    par rapport à p1, selon l'axe le plus proche.
    """
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()

    if abs(dx) > abs(dy):
        # Plus horizontal
        return QPointF(p2.x(), p1.y())
    else:
        # Plus vertical
        return QPointF(p1.x(), p2.y())