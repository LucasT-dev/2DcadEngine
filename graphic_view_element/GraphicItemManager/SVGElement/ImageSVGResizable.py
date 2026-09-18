from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QTransform
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.draw.HistoryManager import ModifyItemCommand
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class ImageSVGResizable(ResizableGraphicsItem, QGraphicsSvgItem):

    def __init__(self, svg_file_path: str, parent=None):

        QGraphicsSvgItem.__init__(self, svg_file_path, parent)
        ResizableGraphicsItem.__init__(self)

        self._create_handles()

        self.rect = QRectF(self.boundingRect())

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

        # Position souris en coordonnées scène
        scene_pos = event.scenePos()

        # Rectangle courant (local)
        rect = self.boundingRect()

        # Point d’ancrage opposé

        if role == "top_left":
            anchor = rect.bottomRight()
        if role == "top_right":
            anchor = rect.bottomLeft()
        if role == "bottom_left":
            anchor = rect.topRight()
        if role == "bottom_right":
            anchor = rect.topLeft()

        # Position de la souris convertie en local
        local_pos = self.mapFromScene(scene_pos)

        # Tailles actuelles
        old_width = rect.width()
        old_height = rect.height()

        new_width = abs(local_pos.x() - anchor.x())
        new_height = abs(local_pos.y() - anchor.y())

        if old_width == 0 or old_height == 0:
            return

        scale_x = new_width / old_width
        scale_y = new_height / old_height

        # Éviter l’inversion
        scale_x = max(scale_x, 0.01)
        scale_y = max(scale_y, 0.01)

        # Appliquer l’échelle autour de l’ancrage
        t = QTransform()
        t.translate(anchor.x(), anchor.y())
        t.scale(scale_x, scale_y)
        t.translate(-anchor.x(), -anchor.y())

        self.setTransform(t, True)

        self.prepareGeometryChange()

        self.update_handles_position()

    def get_point_of_interest(self) -> list[QPointF]:
        rect = self.boundingRect()

        tl = self.mapToScene(rect.topLeft())
        tr = self.mapToScene(rect.topRight())
        br = self.mapToScene(rect.bottomRight())
        bl = self.mapToScene(rect.bottomLeft())
        c = self.mapToScene(rect.center())

        tm = (QPointF((tl.x() + tr.x()) / 2, (tl.y() + tr.y()) / 2))
        bm = (QPointF((br.x() + bl.x()) / 2, (br.y() + bl.y()) / 2))
        lm = (QPointF((tl.x() + bl.x()) / 2, (tl.y() + bl.y()) / 2))
        rm = (QPointF((tr.x() + br.x()) / 2, (tr.y() + br.y()) / 2))

        return [tl, tr, br, bl, c, tm, bm, lm, rm]

    def handle_press(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.update_handles_size(self.transform().m11())
        self.save_item_geometry()

    def handle_released(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement d'un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.save_history_geometry()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur le pixmap."""
        if self.flags().__contains__(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            self.setSelected(True)
            self.select_handle(True)

            self.update_handles_size(self.transform().m11())

            self.begin_move_tracking()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement du svg."""
        self.end_move_tracking()

        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Gestion des changements d'état du svg."""
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
        new_geometry = self.get_item_geometry

        if self._old_geometry != new_geometry:
            cmd = ModifyItemCommand(self, self._old_geometry, new_geometry, "resize/move svg image")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        t = self.transform()
        return pos.x(), pos.y(), t.m11(), t.m22(), t.dx(), t.dy()


    def to_dict(self) -> dict:

        svg_bytes = self.renderer().toXml().toUtf8()
        t = self.transform()

        return {
            "type": "pixmap",

            "data": AdpaterItem.get_data(self),
            "source": self.renderer().objectName() if self.renderer() else None,

            "geometry": {
                "x": self.pos().x(),
                "y": self.pos().y(),
                "m11": t.m11(),
                "m22": t.m22(),
                "dx": t.dx(),
                "dy": t.dy(),
            },
            "svg_content": svg_bytes.data().decode('utf-8'),
            "flags": AdpaterItem.serialize_flags(self)
        }

    @classmethod
    def from_dict(cls, data: dict):

        from libs.cadengine.graphic_view_element.GraphicItemManager.SVGElement.ImageSVGElement import ImageSVGElement

        item_data = data["data"]
        transform = AdpaterItem.dict_to_transform(data=item_data["transform"])

        geometry = data["geometry"]
        x, y = geometry["x"], geometry["y"]
        w, h = geometry["w"], geometry["h"]

        flags_data = data.get("flags", [])
        flags = AdpaterItem.deserialize_flags(flags_data)

        pixmap = AdpaterItem.pixmap_from_base64(data["image"])

        item = ImageSVGElement.create_custom_graphics_item(
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

    def rect(self):
        return self.rect
