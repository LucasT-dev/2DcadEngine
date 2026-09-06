from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPen, QTransform, QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsSceneMouseEvent, QGraphicsItem

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.draw.HistoryManager import ModifyItemCommand
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


def build_smooth_path(points: list[QPointF]) -> QPainterPath:
    """Construit une courbe lissée passant par 'points' (Catmull-Rom -> Bézier cubique)."""
    path = QPainterPath()

    if not points:
        return path

    path.moveTo(points[0])

    n = len(points)
    if n == 1:
        return path
    if n == 2:
        path.lineTo(points[1])
        return path

    for i in range(n - 1):
        p0 = points[i - 1] if i - 1 >= 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else points[i + 1]

        cp1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0, p1.y() + (p2.y() - p0.y()) / 6.0)
        cp2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0, p2.y() - (p3.y() - p1.y()) / 6.0)

        path.cubicTo(cp1, cp2, p2)

    return path

class CurveLineResizable(ResizableGraphicsItem, QGraphicsPathItem):

    def __init__(self, points: list[QPointF]):

        QGraphicsPathItem.__init__(self)
        ResizableGraphicsItem.__init__(self)

        self._points: list[QPointF] = list(points)
        self._rebuild_path()

        # Ajoute un handle par sommet de la polyligne
        for index, point in enumerate(self._points):
            self.add_handle(self._role(index), point)

    @staticmethod
    def _role(index: int) -> str:
        return f"point_{index}"

    @staticmethod
    def _index_from_role(role: str) -> int:
        return int(role.split("_")[1])

    def _rebuild_path(self):
        self.setPath(build_smooth_path(self._points))

    def get_anchor_points_scene(self) -> list[QPointF]:
        """Points d'ancrage de la courbe (hors points de contrôle Bézier), en coordonnées scène."""
        return [self.mapToScene(p) for p in self._points]

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Mise à jour de la polyligne lorsqu'un handle est déplacé."""
        index = self._index_from_role(role)
        new_pos = self.mapFromScene(event.scenePos())
        scene_pos = event.scenePos()

        fixed_prev = self.mapToScene(self._points[index - 1]) if index > 0 else None
        fixed_next = self.mapToScene(self._points[index + 1]) if index < len(self._points) - 1 else None

        snap_point_other_q_graphics_item = self._find_snap_point(self.scene(), scene_pos, exclude_item=self)

        snap_result = None

        if snap_point_other_q_graphics_item:
            snap_result = snap_point_other_q_graphics_item

        elif fixed_prev is not None and fixed_next is not None:
            # Sommet intermédiaire : tente d'abord le snap de coin (angle droit exact)
            corner = self._find_corner_snap(fixed_prev, fixed_next, scene_pos)
            if corner is not None:
                snap_result = corner
            else:
                pass
                # Sinon, retombe sur un snap simple (un seul des deux voisins)
                #snap_result = self._find_angle_auto([fixed_prev, fixed_next], scene_pos)

        else:
            # Premier ou dernier sommet : un seul voisin possible
            fixed = fixed_prev if fixed_prev is not None else fixed_next
            snap_result = self._find_angle_auto(fixed, scene_pos) if fixed is not None else None

        if snap_result is not None:
            new_pos = self.mapFromScene(snap_result)

        self._points[index] = new_pos

        self._rebuild_path()
        self.update_handles_position()

    def update_handles_position(self):
        for index, point in enumerate(self._points):
            self.handles[self._role(index)].setPos(point)

    def handle_press(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.save_item_geometry()

    def handle_released(self, role: str, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement d'un handle."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.save_history_geometry()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion de l'appui sur la polyligne."""
        if self.flags().__contains__(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            self.setSelected(True)
            self.select_handle(True)
            self.update_handles_size(self.transform().m11())
            self.begin_move_tracking()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement de la polyligne."""
        super().mouseReleaseEvent(event)
        self.end_move_tracking()

    def itemChange(self, change, value):
        """Gestion des changements d'état de la polyligne."""
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
            cmd = ModifyItemCommand(self, self._old_geometry, new_geometry, "resize/move multiline")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        points = tuple((p.x(), p.y()) for p in self._points)
        return pos.x(), pos.y(), points

    def set_item_geometry(self, geometry):
        """Restaure une géométrie donnée (utile pour undo/redo)."""
        pos_x, pos_y, points = geometry
        self.setPos(pos_x, pos_y)
        self._points = [QPointF(x, y) for x, y in points]
        self._rebuild_path()
        self.update_handles_position()

    def to_dict(self) -> dict:
        return {
            "type": "multiline",
            "data": AdpaterItem.get_data(self),
            "geometry": {
                "points": [{"x": p.x(), "y": p.y()} for p in self._points],
            },
            "pen": AdpaterItem.get_pen(self),
            "flags": AdpaterItem.serialize_flags(self)
        }

    @classmethod
    def from_dict(cls, data: dict):
        from libs.cadengine.graphic_view_element.GraphicItemManager.PathLineElement.PathLineElement import PathLineElement

        pen: QPen = AdpaterItem.dict_to_pen(data=data["pen"])
        item_data = data["data"]

        transform = AdpaterItem.dict_to_transform(item_data["transform"])

        flags_data = data.get("flags", [])
        flags = AdpaterItem.deserialize_flags(flags_data)

        points = [QPointF(p["x"], p["y"]) for p in data["geometry"]["points"]]

        item = PathLineElement.create_custom_graphics_item(
            points=points,
            border_color=pen.color(),
            border_width=pen.width(),
            border_style=pen.style(),
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


