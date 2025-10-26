from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF

from draw.HistoryManager import ModifyItemCommand
from graphic_view_element.style.HandleStyle import HandleStyle
from serialisation.SerializableGraphicsItem import SerializableGraphicsItem


class ResizeHandle(QGraphicsEllipseItem):
    SIZE = 8

    def __init__(self, parent, position: str):
        super().__init__(-4, -4, self.SIZE, self.SIZE)
        self.setParentItem(parent)
        self.position = position
        self.setBrush(QBrush(QColor(HandleStyle.FILL_COLOR)))
        self.setPen(QPen(QColor(HandleStyle.BORDER_COLOR)))
        self.setZValue(1000)
        self.setCursor(self._cursor_for_position(position))
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        self.setVisible(False)  # invisible par défaut

        self._start_pos = None
        self._original_pos = None

        self._old_ellipse = None

    def _cursor_for_position(self, pos):
        return {
            "tl": Qt.CursorShape.SizeBDiagCursor,
            "tr": Qt.CursorShape.SizeFDiagCursor,
            "bl": Qt.CursorShape.SizeFDiagCursor,
            "br": Qt.CursorShape.SizeBDiagCursor,
            "t": Qt.CursorShape.SizeVerCursor,
            "b": Qt.CursorShape.SizeVerCursor,
            "l": Qt.CursorShape.SizeHorCursor,
            "r": Qt.CursorShape.SizeHorCursor,
        }.get(pos, Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        self._start_pos = event.scenePos()
        self._original_pos = self.scenePos()

        parent = self.parentItem()
        if parent:
            pos = parent.pos()
            r = parent.rect()
            self._old_ellipse = (pos.x(), pos.y(), r.x(), r.y(), r.width(), r.height())
        event.accept()

    def mouseMoveEvent(self, event):
        new_pos = self._original_pos + (event.scenePos() - self._start_pos)
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.resize_from_handle(self.position, parent.mapFromScene(new_pos))
        event.accept()

    def mouseReleaseEvent(self, event):

        parent = self.parentItem()
        if parent and parent.isSelected():
            pos = parent.pos()
            r = parent.rect()
            new_circle = (pos.x(), pos.y(), r.x(), r.y(), r.width(), r.height())

            if self._old_ellipse != new_circle:
                cmd = ModifyItemCommand(parent, self._old_ellipse, new_circle, "resize ellipse")
                self.scene().undo_stack.push(cmd)
        event.accept()


class ResizableEllipseItem(QGraphicsEllipseItem, SerializableGraphicsItem):
    HANDLE_POSITIONS = ["tl", "tr", "bl", "br", "t", "b", "l", "r"]

    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        self.handles = {}
        self._is_resizing = False
        self._init_handles()

        self._old_ellipse = None

    def mousePressEvent(self, event):
        # on mémorise l'état *dans la scène* avant toute action utilisateur
        pos = self.pos()
        r = self.rect()
        self._old_ellipse = (pos.x(), pos.y(), r.x(), r.y(), r.width(), r.height())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        pos = self.pos()
        r = self.rect()
        new_circle = (pos.x(), pos.y(), r.x(), r.y(), r.width(), r.height())
        if self._old_ellipse != new_circle:
            cmd = ModifyItemCommand(self, self._old_ellipse, new_circle, "move ellipse")
            self.scene().undo_stack.push(cmd)
        self._old_ellipse = None
        super().mouseReleaseEvent(event)

    def _init_handles(self):
        for pos in self.HANDLE_POSITIONS:
            handle = ResizeHandle(self, pos)
            handle.setVisible(False)
            self.handles[pos] = handle
        self._update_handle_positions()

    def _update_handle_positions(self):
        if self._is_resizing:
            return

        r = self.rect()
        cx, cy = r.center().x(), r.center().y()

        self.handles["tl"].setPos(r.topLeft())
        self.handles["tr"].setPos(r.topRight())
        self.handles["bl"].setPos(r.bottomLeft())
        self.handles["br"].setPos(r.bottomRight())
        self.handles["t"].setPos(cx, r.top())
        self.handles["b"].setPos(cx, r.bottom())
        self.handles["l"].setPos(r.left(), cy)
        self.handles["r"].setPos(r.right(), cy)

    def resize_from_handle(self, position: str, new_pos: QPointF):
        if self._is_resizing or not self.isSelected():
            return

        self._is_resizing = True
        r = self.rect()

        if position == "br":
            r.setBottomRight(new_pos)
        elif position == "bl":
            r.setBottomLeft(new_pos)
        elif position == "tr":
            r.setTopRight(new_pos)
        elif position == "tl":
            r.setTopLeft(new_pos)
        elif position == "t":
            r.setTop(new_pos.y())
        elif position == "b":
            r.setBottom(new_pos.y())
        elif position == "l":
            r.setLeft(new_pos.x())
        elif position == "r":
            r.setRight(new_pos.x())

        self.setRect(r.normalized())
        self._update_handle_positions()
        self._is_resizing = False

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            for h in self.handles.values():
                h.setVisible(self.isSelected())
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self._update_handle_positions()