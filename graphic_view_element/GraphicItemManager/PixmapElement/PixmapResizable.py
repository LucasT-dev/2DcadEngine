from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QGraphicsSceneMouseEvent

from adapter import AdpaterItem
from draw.HistoryManager import ModifyItemCommand
from graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class PixmapResizable(ResizableGraphicsItem, QGraphicsPixmapItem):

    def __init__(self, pixmap: QPixmap, parent=None):

        QGraphicsPixmapItem.__init__(self, pixmap, parent)
        ResizableGraphicsItem.__init__(self)

        self._create_handles()

        self._original_pixmap = pixmap

        self._rect = QRectF(0, 0, pixmap.width(), pixmap.height())

        self.update_handles_position()

    def _create_handles(self):
        """Crée les 4 Handles de redimensionnement."""
        rect = self.boundingRect()
        self.add_handle("top_left", rect.topLeft())
        self.add_handle("top_right", rect.topRight())
        self.add_handle("bottom_left", rect.bottomLeft())
        self.add_handle("bottom_right", rect.bottomRight())
        self.update_handles_position()

    def update_handles_position(self):
        """Met à jour la position de tous les Handles."""
        rect = self.boundingRect()
        if not self.handles:
            return

        self.handles["top_left"].setPos(rect.topLeft())
        self.handles["top_right"].setPos(rect.topRight())
        self.handles["bottom_left"].setPos(rect.bottomLeft())
        self.handles["bottom_right"].setPos(rect.bottomRight())

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Appelé quand un handle est déplacé."""

        # Convertit la position de la scène vers le repère local
        local_pos = self.mapFromScene(event.scenePos())
        rect = QRectF(self._rect)

        if role == "top_left":
            rect.setTopLeft(local_pos)
        elif role == "top_right":
            rect.setTopRight(local_pos)
        elif role == "bottom_left":
            rect.setBottomLeft(local_pos)
        elif role == "bottom_right":
            rect.setBottomRight(local_pos)

        rect = rect.normalized()
        self._rect = rect

        # Met à jour le pixmap redimensionné
        scaled_pixmap = self._original_pixmap.scaled(
            int(rect.width()), int(rect.height()),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)
        self.setOffset(QPointF(rect.x(), rect.y()))
        self.update_handles_position()

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
        new_pixmap = self.get_item_geometry

        if self._old_geometry != new_pixmap:
            cmd = ModifyItemCommand(self, self._old_geometry, new_pixmap, "resize/move image")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        pixmap = self.pixmap()
        return pos.x(), pos.y(), pixmap.width(), pixmap.height()


    def to_dict(self) -> dict:
        pos = self.pos()
        offset = self.offset()

        pixmap = self.pixmap()

        return {
            "type": "pixmap",

            "data": AdpaterItem.get_data(self),

            "geometry": {
                "x": pos.x(),
                "y": pos.y(),
                "w": pixmap.width(),
                "h": pixmap.height(),
            },
            "image": AdpaterItem.pixmap_to_base64(self.pixmap()),
            "flags": AdpaterItem.serialize_flags(self)
        }

    @classmethod
    def from_dict(cls, data: dict):

        from graphic_view_element.GraphicItemManager.PixmapElement.PixmapElement import PixmapElement

        item_data = data["data"]
        transform = AdpaterItem.dict_to_transform(data=item_data["transform"])

        geometry = data["geometry"]
        x, y = geometry["x"], geometry["y"]
        w, h = geometry["w"], geometry["h"]

        flags_data = data.get("flags", [])
        flags = AdpaterItem.deserialize_flags(flags_data)

        pixmap = AdpaterItem.pixmap_from_base64(data["image"])

        item = PixmapElement.create_custom_graphics_item(
            first_point=QPointF(x, y),
            second_point=QPointF(x + w, y + h),
            image_source=pixmap,  # ignoré car on n'utilise pas path
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