from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QPointF, QRectF

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
        self.setVisible(False)

        self._start_pos = None
        self._original_pos = None
        self._old_geometry = None  # (x, y, w, h)

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
            rect = parent.boundingRect()
            self._old_geometry = (rect.x(), rect.y(), rect.width(), rect.height())

        event.accept()

    def mouseMoveEvent(self, event):
        new_pos = self._original_pos + (event.scenePos() - self._start_pos)
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.resize_from_handle(self.position, parent.mapFromScene(new_pos))
        event.accept()

    def mouseReleaseEvent(self, event):
        parent = self.parentItem()

        if parent and parent.isSelected() and self._old_geometry:
            pos = parent.pos()
            rect = parent.boundingRect()
            new_geometry = (pos.x(), pos.y(), rect.width(), rect.height())

            if self._old_geometry != new_geometry:
                cmd = ModifyItemCommand(parent, self._old_geometry, new_geometry, "Resize text box")
                self.scene().undo_stack.push(cmd)
        event.accept()


class ResizableTextItem(QGraphicsTextItem):
    HANDLE_POSITIONS = ["tl", "tr", "bl", "br", "t", "b", "l", "r"]

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsFocusable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setDefaultTextColor(QColor("black"))

        #self.setFocusProxy(Qt.FocusPolicy.StrongFocus)

        # textWidth initial pour activer le wrapping
        self.setTextWidth(150)

        self.handles = {}
        self._is_resizing = False
        self._init_handles()

    def mouseDoubleClickEvent(self, event):
        # Active l'édition
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        # Quitte l'édition
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        # ✅ Échap pour quitter l'édition
        if event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            return
        super().keyPressEvent(event)

    # ---------- Handles ----------
    def _init_handles(self):
        for pos in self.HANDLE_POSITIONS:
            self.handles[pos] = Handle(self, pos)
        self._update_handle_positions()

    def _update_handle_positions(self):
        if self._is_resizing:
            return

        r = self.boundingRect()
        center_x = r.center().x()
        center_y = r.center().y()

        self.handles["tl"].setPos(r.topRight())
        self.handles["tr"].setPos(r.topLeft())
        self.handles["bl"].setPos(r.bottomRight())
        self.handles["br"].setPos(r.bottomLeft())
        self.handles["t"].setPos(center_x, r.top())
        self.handles["b"].setPos(center_x, r.bottom())
        self.handles["l"].setPos(r.left(), center_y)
        self.handles["r"].setPos(r.right(), center_y)

    # ---------- Resize ----------
    def resize_from_handle(self, position: str, new_pos: QPointF):
        if self._is_resizing or not self.isSelected():
            return

        self._is_resizing = True

        print("resize_from_handle")

        rect = self.boundingRect()
        orig_width = rect.width()
        orig_height = rect.height()

        print(rect)
        print(orig_width)
        print(orig_height)

        # On calcule la nouvelle largeur selon le handle
        if position in {"r", "tr", "br"}:
            new_width = max(new_pos.x() - rect.x(), 1.0)
        elif position in {"l", "tl", "bl"}:
            new_width = max(rect.right() - new_pos.x(), 1.0)
        else:
            # Pour top/bottom, on garde la largeur actuelle
            new_width = orig_width

        # ✅ On applique uniquement la largeur
        self.setTextWidth(new_width)

        # On rafraîchit les handles
        self._update_handle_positions()
        self._is_resizing = False

    # ---------- Selection & Paint ----------
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
        self._update_handle_positions()