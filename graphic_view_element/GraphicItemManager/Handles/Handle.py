from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.HandleStyle import HandleStyle, DEFAULT_STYLE


class Handle(QGraphicsItem):

    def __init__(self, parent: QGraphicsItem, position: QPointF, role: str,
                 style: HandleStyle = None):
        super().__init__(parent)

        self.role = role
        self.style: HandleStyle = style if style is not None else DEFAULT_STYLE
        self._half = self.style.base_size / 2.0
        self._pen_width = self.style.border_width

        self.setZValue(self.style.z_value)
        self.setCursor(self.style.cursor)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity, True)
        self.setPos(position)
        self.setVisible(False)

    # Rendu
    def boundingRect(self) -> QRectF:
        margin = 1.0  # marge pour l'épaisseur du trait
        return QRectF(-self._half - margin, -self._half - margin,
                      (self._half + margin) * 2, (self._half + margin) * 2)

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setPen(QPen(self.style.border_color, self._pen_width))
        painter.setBrush(QBrush(self.style.fill_color))

        rect = QRectF(-self._half, -self._half, self._half * 2, self._half * 2)

        if self.style.shape == "rect":
            painter.drawRect(rect)
        else:
            painter.drawEllipse(rect)

    # Personnalisation à la volée
    def set_style(self, style: HandleStyle):
        self.style = style
        self.setZValue(style.z_value)
        self.setCursor(style.cursor)
        self.update()


    def mousePressEvent(self, event):
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.handle_press(self.role, event)
        event.accept()
        #super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.handle_moved(self.role, event)
        event.accept()
        #super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.handle_released(self.role, event)
        event.accept()
        #super().mouseReleaseEvent(event)

    # Zoom
    def update_size(self, zoom_level: float):
        if zoom_level <= 0:
            return

        self.prepareGeometryChange()
        self._half = max((self.style.base_size / zoom_level) / 1.5, self.style.min_size)
        self._pen_width = max(self.style.border_width / zoom_level, 1.0)
        self.update()