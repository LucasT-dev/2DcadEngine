from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QPixmap, QColor, QBrush, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsEllipseItem

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

        self._old_pixmap = None

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
            pos = parent.pos()
            pixmap = parent.pixmap()
            self._old_pixmap = (pos.x(), pos.y(), pixmap.width(), pixmap.height())

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
            pixmap = parent.pixmap()
            new_pixmap = (pos.x(), pos.y(), pixmap.width(), pixmap.height())

            if self._old_pixmap != new_pixmap:
                cmd = ModifyItemCommand(parent, self._old_pixmap, new_pixmap, "resize pixmap")
                self.scene().undo_stack.push(cmd)

        event.accept()


class ResizablePixmapItem(QGraphicsPixmapItem):
    HANDLE_POSITIONS = ["tl", "tr", "bl", "br", "t", "b", "l", "r"]

    def __init__(self, pixmap: QPixmap):
        super().__init__(pixmap)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        self._original_pixmap = pixmap
        self._is_resizing = False
        self.handles = {}
        self._init_handles()

        self._old_pixmap = None

    def mousePressEvent(self, event):
        pos = self.pos()
        pixmap = self.pixmap()
        self._old_pixmap = (pos.x(), pos.y(), pixmap.width(), pixmap.height())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        pos = self.pos()
        pixmap = self.pixmap()
        new_pixmap = (pos.x(), pos.y(), pixmap.width(), pixmap.height())

        if self._old_pixmap != new_pixmap:
            cmd = ModifyItemCommand(self, self._old_pixmap, new_pixmap, "move/resize pixmap")
            self.scene().undo_stack.push(cmd)

        self._old_pixmap = None
        super().mouseReleaseEvent(event)

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

        # ⬅ Bloquer itemChange pendant la mise à jour

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

        r = self.boundingRect()
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

        r = r.normalized()

        scaled_pixmap = self._original_pixmap.scaled(
            int(r.width()), int(r.height()),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

        # Ajuster l'offset uniquement si on tire sur gauche/haut
        offset_x = self.offset().x()
        offset_y = self.offset().y()
        if position in ("tl", "l", "bl"):
            offset_x = r.left()
        if position in ("tl", "t", "tr"):
            offset_y = r.top()
        self.setOffset(offset_x, offset_y)

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
        self._update_handle_positions()