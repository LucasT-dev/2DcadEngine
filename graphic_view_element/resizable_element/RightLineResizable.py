from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem

from draw.HistoryManager import ModifyItemCommand
from graphic_view_element.style.HandleStyle import HandleStyle


class Handle(QGraphicsEllipseItem):
    SIZE = 8

    def __init__(self, parent, endpoint: str):
        super().__init__(-4, -4, self.SIZE, self.SIZE)

        self.setParentItem(parent)
        self.endpoint = endpoint  # "start" ou "end"
        self.setBrush(QBrush(QColor(HandleStyle.FILL_COLOR)))
        self.setPen(QPen(QColor(HandleStyle.BORDER_COLOR)))
        self.setZValue(1000)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        self.setVisible(False)  # invisible par défaut

        self._start_pos = None
        self._original_pos = None

        self._old_line = None

    def mousePressEvent(self, event):
        self._start_pos = event.scenePos()
        self._original_pos = self.scenePos()

        parent = self.parentItem()
        if parent:
            line = parent.line()
            pos = parent.pos()
            self._old_line = (pos.x(), pos.y(), line.x1(), line.y1(), line.x2(), line.y2())
        event.accept()

    def mouseMoveEvent(self, event):
        new_pos = self._original_pos + (event.scenePos() - self._start_pos)

        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.update_line_from_handle(self.endpoint, parent.mapFromScene(new_pos))
        event.accept()

    def mouseReleaseEvent(self, event):

        parent = self.parentItem()
        if parent and parent.isSelected():
            line = parent.line()
            pos = parent.pos()
            new_line = (pos.x(), pos.y(), line.x1(), line.y1(), line.x2(), line.y2())

            if self._old_line != new_line:
                cmd = ModifyItemCommand(parent, self._old_line, new_line, "resize line")
                self.scene().undo_stack.push(cmd)
        event.accept()


class ResizableRightLineItem(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, scene=None):
        super().__init__(x1, y1, x2, y2)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        # Ligne de guidage horizontale/verticale
        self.guide_line = QGraphicsLineItem()
        guide_pen = QPen(Qt.PenStyle.DashLine)
        guide_pen.setColor(QColor("blue"))
        self.guide_line.setPen(guide_pen)
        self.guide_line.setZValue(999)
        self.guide_line.setVisible(False)

        # Ligne de guidage rattachée à l’item
        self.guide_line = QGraphicsLineItem(self)
        guide_pen = QPen(Qt.PenStyle.DashLine)
        guide_pen.setColor(QColor("white"))
        guide_pen.setWidth(0)
        self.guide_line.setPen(guide_pen)
        self.guide_line.setZValue(999)
        self.guide_line.setVisible(False)

        self.handles = {
            "start": Handle(self, "start"),
            "end": Handle(self, "end")
        }

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        self.orientation = "horizontal" if dx >= dy else "vertical"

        self._update_handle_positions()

        for handle in self.handles.values():
            handle.setVisible(False)

        self._update_handle_positions()

        self._old_line = None

    def mousePressEvent(self, event):
        line = self.line()
        pos = self.pos()
        self._old_line = (pos.x(), pos.y(), line.x1(), line.y1(), line.x2(), line.y2())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        line = self.line()
        pos = self.pos()
        new_line = (pos.x(), pos.y(), line.x1(), line.y1(), line.x2(), line.y2())

        if self._old_line != new_line:
            cmd = ModifyItemCommand(self, self._old_line, new_line, "move/resize line")
            self.scene().undo_stack.push(cmd)

        self._old_line = None
        super().mouseReleaseEvent(event)

    def _update_handle_positions(self):
        line = self.line()
        self.handles["start"].setPos(line.p1())
        self.handles["end"].setPos(line.p2())

    def update_line_from_handle(self, endpoint: str, new_pos: QPointF):
        line = self.line()
        fixed = line.p2() if endpoint == "start" else line.p1()

        dx = new_pos.x() - fixed.x()
        dy = new_pos.y() - fixed.y()

        # Déterminer l’orientation dominante
        if abs(dx) > abs(dy):
            # Snap horizontal
            new_pos.setY(fixed.y())
        else:
            # Snap vertical
            new_pos.setX(fixed.x())

        # Mettre à jour la ligne
        if endpoint == "start":
            line.setP1(new_pos)
        else:
            line.setP2(new_pos)

        self.setLine(line)
        self._update_handle_positions()
        self._show_guide(fixed, new_pos)

    def _show_guide(self, fixed_point: QPointF, moving_point: QPointF):
        if not self.scene():
            return

        dx = moving_point.x() - fixed_point.x()
        dy = moving_point.y() - fixed_point.y()
        scene_rect = self.scene().sceneRect()

        if abs(dx) > abs(dy):
            # Ligne horizontale
            y = fixed_point.y()
            self.guide_line.setLine(scene_rect.left(), y, scene_rect.right(), y)
            self.guide_line.setVisible(True)
        else:
            # Ligne verticale
            x = fixed_point.x()
            self.guide_line.setLine(x, scene_rect.top(), x, scene_rect.bottom())
            self.guide_line.setVisible(True)

    def clear_guide_line(self):
        self.guide_line.setVisible(False)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            selected = bool(value)
            for handle in self.handles.values():
                handle.setVisible(selected)

            if not selected:
                self.clear_guide_line()

        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self._update_handle_positions()