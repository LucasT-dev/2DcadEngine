from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QGraphicsSceneMouseEvent

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.draw.HistoryManager import ModifyItemCommand
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class PixmapResizable(QGraphicsPixmapItem, ResizableGraphicsItem):

    def __init__(self, pixmap: QPixmap, parent=None):

        QGraphicsPixmapItem.__init__(self, pixmap, parent)
        ResizableGraphicsItem.__init__(self)

        self._create_handles()

        self._original_pixmap = pixmap

        self.rect = QRectF(0, 0, pixmap.width(), pixmap.height())

    @staticmethod
    def _top_left(rect: QRectF) -> QPointF:
        return rect.topLeft()

    @staticmethod
    def _top_right(rect: QRectF) -> QPointF:
        return rect.topRight()

    @staticmethod
    def _bottom_left(rect: QRectF) -> QPointF:
        return rect.bottomLeft()

    @staticmethod
    def _bottom_right(rect: QRectF) -> QPointF:
        return rect.bottomRight()

    @staticmethod
    def _mid_top(rect: QRectF) -> QPointF:
        return QPointF((rect.left() + rect.right()) / 2, rect.top())

    @staticmethod
    def _mid_bottom(rect: QRectF) -> QPointF:
        return QPointF((rect.left() + rect.right()) / 2, rect.bottom())

    @staticmethod
    def _mid_left(rect: QRectF) -> QPointF:
        return QPointF(rect.left(), (rect.top() + rect.bottom()) / 2)

    @staticmethod
    def _mid_right(rect: QRectF) -> QPointF:
        return QPointF(rect.right(), (rect.top() + rect.bottom()) / 2)

    def _create_handles(self):
        """Crée les 4 Handles de redimensionnement."""
        rect = self.boundingRect()
        self.add_handle("top_left", self._top_left(rect))
        self.add_handle("top_right", self._top_right(rect))
        self.add_handle("bottom_left", self._bottom_left(rect))
        self.add_handle("bottom_right", self._bottom_right(rect))

        self.add_handle("top", self._mid_top(rect))
        self.add_handle("bottom", self._mid_bottom(rect))
        self.add_handle("left", self._mid_left(rect))
        self.add_handle("right", self._mid_right(rect))

        self.update_handles_position()

    def update_handles_position(self):
        """Met à jour la position de tous les Handles."""
        if not self.handles: return
        rect = self.boundingRect()

        self.handles["top_left"].setPos(self._top_left(rect))
        self.handles["top_right"].setPos(self._top_right(rect))
        self.handles["bottom_left"].setPos(self._bottom_left(rect))
        self.handles["bottom_right"].setPos(self._bottom_right(rect))

        self.handles["top"].setPos(self._mid_top(rect))
        self.handles["bottom"].setPos(self._mid_bottom(rect))
        self.handles["left"].setPos(self._mid_left(rect))
        self.handles["right"].setPos(self._mid_right(rect))

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Appelé quand un handle est déplacé."""

        if not self.get_item_is_resizable(): return  # The item is not resizable.

        # Convertit la position de la scène vers le repère local
        scene_pos = event.scenePos()
        local_pos = self.mapFromScene(scene_pos)
        rect = QRectF(self.rect)

        snap_point_other_q_graphics_item = self._find_snap_point(self.scene(), scene_pos, item_moved=self)

        if snap_point_other_q_graphics_item:
            local_pos = self.mapFromScene(snap_point_other_q_graphics_item)

        if role == "top_left":
            rect.setTopLeft(local_pos)
        elif role == "top_right":
            rect.setTopRight(local_pos)
        elif role == "bottom_left":
            rect.setBottomLeft(local_pos)
        elif role == "bottom_right":
            rect.setBottomRight(local_pos)

        elif role == "top":
            rect.setTop(local_pos.y())
        elif role == "bottom":
            rect.setBottom(local_pos.y())
        elif role == "left":
            rect.setLeft(local_pos.x())
        elif role == "right":
            rect.setRight(local_pos.x())

        rect = rect.normalized()
        self.rect = rect

        # Met à jour le pixmap redimensionné
        scaled_pixmap = self._original_pixmap.scaled(
            int(rect.width()), int(rect.height()),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)
        self.setOffset(QPointF(rect.x(), rect.y()))
        self.update_handles_position()

    def _calcul_point_of_interest(self):
        rect = self.boundingRect()

        tl = rect.topLeft()
        tr = rect.topRight()
        br = rect.bottomRight()
        bl = rect.bottomLeft()
        c = rect.center()

        tm = (QPointF((tl.x() + tr.x()) / 2, (tl.y() + tr.y()) / 2))
        bm = (QPointF((br.x() + bl.x()) / 2, (br.y() + bl.y()) / 2))
        lm = (QPointF((tl.x() + bl.x()) / 2, (tl.y() + bl.y()) / 2))
        rm = (QPointF((tr.x() + br.x()) / 2, (tr.y() + br.y()) / 2))

        return [tl, tr, br, bl, c, tm, bm, lm, rm]

    def _add_point_of_interest(self):

        for p in self._calcul_point_of_interest() :
            self.add_point_of_interest(p)

        return self._custom_points_of_interest

    def _update_point_of_interest(self):

        for index, p in enumerate(self._calcul_point_of_interest()) :
            self.replace_point_of_interest(p, index)

    def get_point_of_interest(self) -> list[QPointF]:

        points: list[QPointF] = []
        for point in self._custom_points_of_interest:
            points.append(self.mapToScene(point))

        return points

    def handle_press(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.save_item_geometry()
        self._begin_resize(self)

    def handle_released(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement d'un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.save_history_geometry()
        self._update_point_of_interest()
        self._end_resize()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur le pixmap."""

        if self.flags().__contains__(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            self.setSelected(True)
            self.select_handle(True)

            self.update_handles_size(self.transform().m11())

            self.begin_move_tracking()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement de le pixmap."""
        self.end_move_tracking()

        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Gestion des changements d'état du pixmap."""
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

        from libs.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapElement import PixmapElement

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

        points_data = data.get("points_of_interest", [])
        for p in points_data:
            point: QPointF = AdpaterItem.point_from_dict(p["p"])
            item.add_point_of_interest(point)

        return item

    def rect(self):
        return self.rect

    def resize_pixmap(self, w, h):
        if w < 1: w = 1
        if h < 1: h = 1

        scaled = self._original_pixmap.scaled(
            int(w), int(h),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)