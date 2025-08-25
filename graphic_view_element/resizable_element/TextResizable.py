from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPointF

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

        self._old_text = None

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
            w = parent.textWidth()
            h = parent.boundingRect().height()
            self._old_text = (pos.x(), pos.y(), w, h)

        event.accept()

    def mouseMoveEvent(self, event):
        new_pos = self._original_pos + (event.scenePos() - self._start_pos)
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.resize_from_handle(self.position, parent.mapFromScene(new_pos))
        event.accept()

    def mouseReleaseEvent(self, event):
        parent = self.parentItem()

        if parent and parent.isSelected() and self._old_text:
            pos = parent.pos()
            w = parent.textWidth()
            h = parent.boundingRect().height()
            new_text = (pos.x(), pos.y(), w, h)

            if self._old_text != new_text:
                cmd = ModifyItemCommand(parent, self._old_text, new_text, "Resize text box")
                self.scene().undo_stack.push(cmd)
        event.accept()


class ResizableTextItem(QGraphicsTextItem):
    HANDLE_POSITIONS = ["tl", "tr", "bl", "br", "l", "r"]

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

        self._old_text = None

    def mousePressEvent(self, event):
        pos = self.pos()
        w = self.textWidth()
        h = self.boundingRect().height()
        self._old_text = (pos.x(), pos.y(), w, h)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        pos = self.pos()
        w = self.textWidth()
        h = self.boundingRect().height()
        new_text = (pos.x(), pos.y(), w, h)

        if self._old_text != new_text:
            cmd = ModifyItemCommand(self, self._old_text, new_text, "move/resize text")
            self.scene().undo_stack.push(cmd)

        self._old_text = None
        super().mouseReleaseEvent(event)

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
        center_y = r.center().y()

        # Coins
        self.handles["tl"].setPos(r.topLeft())
        self.handles["tr"].setPos(r.topRight())
        self.handles["bl"].setPos(r.bottomLeft())
        self.handles["br"].setPos(r.bottomRight())

        # Côtés
        self.handles["l"].setPos(r.left(), center_y)
        self.handles["r"].setPos(r.right(), center_y)

    # ---------- Resize ----------
    def resize_from_handle(self, position: str, new_pos: QPointF):
        if self._is_resizing or not self.isSelected():
            return

        self._is_resizing = True

        rect = self.boundingRect()
        orig_width = rect.width()

        if position in {"r", "tr", "br"}:
            # Redimension depuis la droite
            new_width = max(new_pos.x() - rect.x(), 1.0)
            self.setTextWidth(new_width)

        elif position in {"l", "tl", "bl"}:
            # Redimension depuis la gauche
            diff = new_pos.x() - rect.x()
            new_width = max(orig_width - diff, 1.0)
            self.setTextWidth(new_width)
            self.setPos(self.pos() + QPointF(diff, 0))  # décaler à gauche

        else:
            # Top et bottom → pas d’effet
            self._is_resizing = False
            return

        # Mise à jour des handles
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