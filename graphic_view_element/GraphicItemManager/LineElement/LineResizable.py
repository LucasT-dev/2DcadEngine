from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsSceneMouseEvent, QGraphicsItem

from draw.HistoryManager import ModifyItemCommand
from graphic_view_element.GraphicItemManager.Handles.HandleObject import ResizableGraphicsItem


class LineResizable(ResizableGraphicsItem, QGraphicsLineItem):

    def __init__(self, x1: float, y1: float, x2: float, y2: float):

        QGraphicsLineItem.__init__(self, x1, y1, x2, y2)
        ResizableGraphicsItem.__init__(self)

        # Ajoute les Handles
        self.add_handle("start", self.line().p1())
        self.add_handle("end", self.line().p2())

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Mise à jour de la ligne lorsque le handle est déplacé."""
        new_pos = self.mapFromScene(event.scenePos())
        line = self.line()

        if role == "start":
            line.setP1(new_pos)
        elif role == "end":
            line.setP2(new_pos)

        # Applique la nouvelle ligne
        self.setLine(line)
        # Met à jour la position des Handles
        self.handles["start"].setPos(line.p1())
        self.handles["end"].setPos(line.p2())

    def update_handles_position(self):
        print("update handle")

    def handle_press(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

        # Systeme de sauvegarde de l'item
        self.save_item_geometry()

    def handle_released(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement d'un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

        self.save_history_geometry()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur l'ellipse."""

        self.setSelected(True)
        self.select_handle(True)

        self.save_item_geometry()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement de l'ellipse."""
        super().mouseReleaseEvent(event)

        self.save_history_geometry()

    def itemChange(self, change, value):
        """Gestion des changements d'état de l'ellipse."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            selected = bool(value)
            self.select_handle(selected)

        print(change)

        return super().itemChange(change, value)

    def select_handle(self, visible: bool):
        """Affiche ou masque les Handles."""
        for handle in self.handles.values():
            handle.setVisible(visible)

    def save_item_geometry(self):
        self._old_geometry = self.get_item_geometry

    def save_history_geometry(self):
        new_line = self.get_item_geometry

        if self._old_geometry != new_line:
            cmd = ModifyItemCommand(self, self._old_geometry, new_line, "resize/move line")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        line = self.line()
        pos = self.pos()
        return pos.x(), pos.y(), line.x1(), line.y1(), line.x2(), line.y2()
