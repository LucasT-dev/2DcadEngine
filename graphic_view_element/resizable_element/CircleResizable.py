from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem

from draw.HistoryManager import ModifyItemCommand
from graphic_view_element.style.HandleStyle import HandleStyle


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

        self._old_circle = None

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
            self._old_circle = (
                parent.rect().x(), parent.rect().y(),
                parent.rect().width(), parent.rect().height()
            )
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
            new_circle = (
                parent.rect().x(), parent.rect().y(),
                parent.rect().width(), parent.rect().height()
            )
            if self._old_circle != new_circle:
                cmd = ModifyItemCommand(parent, self._old_circle, new_circle, "resize circle")
                self.scene().undo_stack.push(cmd)
        event.accept()


class ResizableCircleItem(QGraphicsEllipseItem):
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

        if position in {"br", "bl", "tr", "tl"}:
            fixed = {
                "br": r.topLeft(),
                "bl": r.topRight(),
                "tr": r.bottomLeft(),
                "tl": r.bottomRight(),
            }[position]

            dx = new_pos.x() - fixed.x()
            dy = new_pos.y() - fixed.y()
            size = max(abs(dx), abs(dy))
            dx = size if dx >= 0 else -size
            dy = size if dy >= 0 else -size
            rect = QRectF(fixed, QPointF(fixed.x() + dx, fixed.y() + dy)).normalized()

        elif position in {"t", "b", "l", "r"}:
            center = r.center()
            dx = abs(new_pos.x() - center.x())
            dy = abs(new_pos.y() - center.y())
            size = max(dx, dy)
            rect = QRectF(center.x() - size, center.y() - size, 2 * size, 2 * size)
        else:
            rect = r

        self.setRect(rect.normalized())
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