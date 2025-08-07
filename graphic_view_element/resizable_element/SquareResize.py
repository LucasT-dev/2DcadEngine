from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsEllipseItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF

from draw.HistoryManager import ModifyItemCommand
from graphic_view_element.style.HandleStyle import HandleStyle


class Handle(QGraphicsEllipseItem):
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

        self._old_rect = None

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

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            parent = self.parentItem()
            if parent and parent.isSelected():
                parent.resize_from_handle(self.position, value)
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self._start_pos = event.scenePos()
        self._original_pos = self.scenePos()

        parent = self.parentItem()
        if parent:
            self._old_rect = (
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
            new_square = (
                parent.rect().x(), parent.rect().y(),
                parent.rect().width(), parent.rect().height()
            )
            if self._old_rect != new_square:
                cmd = ModifyItemCommand(parent, self._old_rect, new_square, "resize square")
                self.scene().undo_stack.push(cmd)
        event.accept()


class ResizableSquareItem(QGraphicsRectItem):
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
            self.handles[pos] = Handle(self, pos)
        self._update_handle_positions()

    def _update_handle_positions(self):
        if self._is_resizing:
            return

        r = self.rect()
        center_x = r.center().x()
        center_y = r.center().y()

        self.handles["tl"].setPos(r.topLeft())
        self.handles["tr"].setPos(r.topRight())
        self.handles["bl"].setPos(r.bottomLeft())
        self.handles["br"].setPos(r.bottomRight())
        self.handles["t"].setPos(center_x, r.top())
        self.handles["b"].setPos(center_x, r.bottom())
        self.handles["l"].setPos(r.left(), center_y)
        self.handles["r"].setPos(r.right(), center_y)

    def resize_from_handle(self, position: str, new_pos: QPointF):
        if self._is_resizing or not self.isSelected():
            return

        self._is_resizing = True

        rect = self.rect()
        orig = rect.getRect()  # x, y, w, h

        if position in {"br", "bl", "tr", "tl"}:
            # On part toujours d'un coin opposé
            fixed = {
                "br": rect.topLeft(),
                "bl": rect.topRight(),
                "tr": rect.bottomLeft(),
                "tl": rect.bottomRight(),
            }[position]

            # Calcule dx/dy vers le coin actif
            dx = new_pos.x() - fixed.x()
            dy = new_pos.y() - fixed.y()

            size = max(abs(dx), abs(dy))
            dx = size if dx >= 0 else -size
            dy = size if dy >= 0 else -size

            rect = QRectF(fixed, QPointF(fixed.x() + dx, fixed.y() + dy)).normalized()

        elif position in {"t", "b", "l", "r"}:
            # Pour les bords : fixe le centre
            center = rect.center()
            dx = abs(new_pos.x() - center.x())
            dy = abs(new_pos.y() - center.y())
            size = max(dx, dy)

            rect = QRectF(center.x() - size, center.y() - size,
                          2 * size, 2 * size)

        self.setRect(rect.normalized())
        self._update_handle_positions()
        self._is_resizing = False

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            selected = self.isSelected()
            for handle in self.handles.values():
                handle.setVisible(selected)
                if not selected:
                    handle.unsetCursor()
            if not selected:
                self.unsetCursor()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self._update_handle_positions()  # 🛠 toujours à jour visuellement