import uuid

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPen, QColor, QTransform

from libs.cadengine.graphic_view_element.GraphicItemManager.BezierCubiqueLineElement.BezierCubeLineResizable import \
    BezierCubeLineResizable
from libs.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import ElementObject
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.HandleStyle import HandleStyle, DEFAULT_STYLE


class BezierCubeLineElement(ElementObject):

    def create_graphics_item(self, points: list[QPointF]):

        pen = QPen(QColor(self.get_style().get_border_color()))
        pen.setWidth(self.get_style().get_border_width())
        pen.setStyle(self.get_style().get_border_style())

        item = BezierCubeLineResizable(points)
        item.setPen(pen)
        item.setZValue(self.get_style().get_z_value())

        item.set_snap_enable(True)

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.get_style().get_key(), self.get_style().get_value())

        return item

    @staticmethod
    def create_custom_graphics_item(points: list[QPointF],
                                    border_color: QColor,
                                    controls: list[list[QPointF]] | None = None,
                                    border_style: Qt.PenStyle = Qt.PenStyle.SolidLine,
                                    border_width: int = 0,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    transform: QTransform = QTransform(),
                                    visibility: bool = True,
                                    scale: float = 1.0,
                                    handle_style: HandleStyle = DEFAULT_STYLE,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        pen = QPen(QColor(border_color))
        pen.setWidth(border_width)
        pen.setStyle(border_style)

        item = BezierCubeLineResizable(points, controls)
        item.setPen(pen)
        item.setZValue(z_value)

        item.set_handle_style(handle_style)

        item.setFlags(flags)

        item.setData(key, value)

        return item