from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QBrush, QPen, QTransform
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsSceneMouseEvent, QGraphicsItem

from src.cadengine.adapter import AdpaterItem
from src.cadengine.draw.HistoryManager import ModifyItemCommand
from src.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class EllipseResizable(ResizableGraphicsItem, QGraphicsEllipseItem):

    def __init__(self, ellipse: QRectF, parent=None):

        QGraphicsEllipseItem.__init__(self, ellipse, parent)
        ResizableGraphicsItem.__init__(self)

        # Création des 4 Handles de redimensionnement
        self._create_handles()

    def _create_handles(self):
        """Crée les 4 Handles de redimensionnement."""
        rect = self.rect()
        self.add_handle("top_left", rect.topLeft())
        self.add_handle("top_right", rect.topRight())
        self.add_handle("bottom_left", rect.bottomLeft())
        self.add_handle("bottom_right", rect.bottomRight())
        self.update_handles_position()

    def update_handles_position(self):
        """Met à jour la position de tous les Handles."""
        rect = self.rect()
        if not self.handles:
            return
        self.handles["top_left"].setPos(rect.topLeft())
        self.handles["top_right"].setPos(rect.topRight())
        self.handles["bottom_left"].setPos(rect.bottomLeft())
        self.handles["bottom_right"].setPos(rect.bottomRight())

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Appelé quand un handle est déplacé (par Handle)."""
        # Convertit la position de la scène vers le repère local
        local_pos = self.mapFromScene(event.scenePos())
        rect = QRectF(self.rect())

        if role == "top_left":
            rect.setTopLeft(local_pos)
        elif role == "top_right":
            rect.setTopRight(local_pos)
        elif role == "bottom_left":
            rect.setBottomLeft(local_pos)
        elif role == "bottom_right":
            rect.setBottomRight(local_pos)

        rect = rect.normalized()
        self.setRect(rect)
        self.update_handles_position()

    def handle_press(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

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
        self.save_history_geometry()

        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Gestion des changements d'état de l'ellipse."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            selected = bool(value)
            self.select_handle(selected)
        return super().itemChange(change, value)

    def select_handle(self, visible: bool):
        """Affiche ou masque les Handles."""
        for handle in self.handles.values():
            handle.setVisible(visible)

    def save_item_geometry(self):
        self._old_geometry = self.get_item_geometry

    def save_history_geometry(self):
        new_ellipse = self.get_item_geometry

        if self._old_geometry != new_ellipse:
            cmd = ModifyItemCommand(self, self._old_geometry, new_ellipse, "resize/move ellipse")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        r = self.rect()
        return pos.x(), pos.y(), r.x(), r.y(), r.width(), r.height()


    def to_dict(self) -> dict:
        r: QRectF = self.rect()

        return {
            "type": "ellipse",
            "data": AdpaterItem.get_data(self),

            "geometry": {
                "x": r.x(),
                "y": r.y(),
                "w": r.width(),
                "h": r.height(),
            },
            "pen": AdpaterItem.get_pen(self),
            "brush": AdpaterItem.get_brush(self),
            "flags": AdpaterItem.serialize_flags(self)
        }

    @classmethod
    def from_dict(cls, data: dict):

        from graphic_view_element.GraphicItemManager.EllipseElement.EllipseElement import EllipseElement

        geometry = data["geometry"]
        pen: QPen = AdpaterItem.dict_to_pen(data=data["pen"])
        brush: QBrush = AdpaterItem.dict_to_brush(data=data["brush"])
        item_data = data["data"]
        transform = AdpaterItem.dict_to_transform(data=item_data["transform"])
        flags_data = data.get("flags", [])

        x, y, w, h = geometry["x"], geometry["y"], geometry["w"], geometry["h"]

        flags = AdpaterItem.deserialize_flags(flags_data)

        item = EllipseElement.create_custom_graphics_item(
            first_point=QPointF(x, y),
            second_point=QPointF(x + w, y + h),
            border_color=pen.color(),
            border_width=pen.width(),
            border_style=pen.style(),
            fill_color=brush.color(),
            z_value=item_data["z_value"],
            key=int(list(item_data["data"].keys())[0]) if item_data["data"] else 0,
            value=list(item_data["data"].values())[0] if item_data["data"] else "",
            transform=QTransform(),
            visibility=item_data["visibility"],
            scale=item_data["scale"],
            flags=flags
        )
        item.setTransform(transform)

        return item