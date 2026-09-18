from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPen, QTransform, QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsSceneMouseEvent, QGraphicsItem, QGraphicsLineItem

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.draw.HistoryManager import ModifyItemCommand
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.HandleStyle import ANCHOR_STYLE, CONTROL_STYLE, \
    GUIDE_LINE_STYLE
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class BezierCubeLineResizable(ResizableGraphicsItem, QGraphicsPathItem):

    def __init__(self, points: list[QPointF], controls: list[list[QPointF]] | None = None):

        QGraphicsPathItem.__init__(self)
        ResizableGraphicsItem.__init__(self)

        self._points: list[QPointF] = list(points)
        self._controls: list[list[QPointF]] = (
            controls if controls is not None else self._compute_initial_controls(self._points)
        )
        self._updating_handles = False
        self._guide_lines: dict[str, QGraphicsLineItem] = {}  # role du handle contrôle -> ligne

        self._rebuild_path()

        # Dans __init__, remplace la boucle d'ajout de handles :
        for index, point in enumerate(self._points):
            self.add_handle(f"point_{index}", point, style=ANCHOR_STYLE)

        for seg_index, (cp1, cp2) in enumerate(self._controls):
            self.add_handle(f"cp1_{seg_index}", cp1, style=CONTROL_STYLE)
            self.add_handle(f"cp2_{seg_index}", cp2, style=CONTROL_STYLE)

            self._create_guide_line(f"cp1_{seg_index}")
            self._create_guide_line(f"cp2_{seg_index}")

    # Génération initiale des points de contrôle (Catmull-Rom -> Bézier)
    @staticmethod
    def _compute_initial_controls(points: list[QPointF]) -> list[list[QPointF]]:
        n = len(points)
        controls = []

        for i in range(n - 1):
            p0 = points[i - 1] if i - 1 >= 0 else points[i]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[i + 2] if i + 2 < n else points[i + 1]

            cp1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0, p1.y() + (p2.y() - p0.y()) / 6.0)
            cp2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0, p2.y() - (p3.y() - p1.y()) / 6.0)

            controls.append([cp1, cp2])

        return controls

    # Parsing des rôles de handle
    @staticmethod
    def _parse_role(role: str) -> tuple[str, int]:
        kind, index_str = role.rsplit("_", 1)
        return kind, int(index_str)

    def _rebuild_path(self):
        path = QPainterPath()
        if not self._points:
            self.setPath(path)
            return

        path.moveTo(self._points[0])
        for i, (cp1, cp2) in enumerate(self._controls):
            path.cubicTo(cp1, cp2, self._points[i + 1])

        self.setPath(path)

    def _create_guide_line(self, control_role: str):
        """Crée la ligne pointillée reliant un handle de contrôle à son ancrage."""
        line = QGraphicsLineItem(self)

        pen = QPen(GUIDE_LINE_STYLE.border_color)
        pen.setWidthF(GUIDE_LINE_STYLE.border_width)
        pen.setStyle(Qt.PenStyle.DashLine)
        line.setPen(pen)

        line.setZValue(GUIDE_LINE_STYLE.z_value if hasattr(GUIDE_LINE_STYLE, "z_value") else 998.0)
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity, True)
        line.setVisible(False)  # même visibilité que les handles, gérée dans select_handle

        self._guide_lines[control_role] = line

    @staticmethod
    def _anchor_index_for_control(kind: str, seg_index: int) -> int:
        """cp1 du segment i est rattaché au point i, cp2 du segment i au point i+1."""
        return seg_index if kind == "cp1" else seg_index + 1

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Mise à jour de la courbe lorsqu'un handle (point ou contrôle) est déplacé."""
        if self._updating_handles:
            return

        kind, index = self._parse_role(role)
        new_pos = self.mapFromScene(event.scenePos())
        scene_pos = event.scenePos()

        if kind == "point":
            fixed_prev = self.mapToScene(self._points[index - 1]) if index > 0 else None
            fixed_next = self.mapToScene(self._points[index + 1]) if index < len(self._points) - 1 else None

            snap_point_other = self._find_snap_point(self.scene(), scene_pos, exclude_item=self)
            snap_result = None

            if snap_point_other:
                snap_result = snap_point_other
            elif fixed_prev is not None and fixed_next is not None:
                corner = self._find_corner_snap(fixed_prev, fixed_next, scene_pos)
                snap_result = corner if corner is not None else self._find_angle_auto([fixed_prev, fixed_next], scene_pos)
            else:
                fixed = fixed_prev if fixed_prev is not None else fixed_next
                snap_result = self._find_angle_auto(fixed, scene_pos) if fixed is not None else None

            if snap_result is not None:
                new_pos = self.mapFromScene(snap_result)

            # Déplace l'ancrage, et translate ses poignées de contrôle adjacentes
            # de la même façon pour préserver la forme locale de la courbe.
            delta = new_pos - self._points[index]
            self._points[index] = new_pos

            if index > 0:
                self._controls[index - 1][1] = self._controls[index - 1][1] + delta  # cp2 du segment précédent
            if index < len(self._points) - 1:
                self._controls[index][0] = self._controls[index][0] + delta  # cp1 du segment suivant

        else:
            # Point de contrôle : pas de snapping, déplacement libre
            seg_index = index
            if kind == "cp1":
                self._controls[seg_index][0] = new_pos
            else:
                self._controls[seg_index][1] = new_pos

        self._rebuild_path()
        self.update_handles_position()

    def get_point_of_interest(self) -> list[QPointF]:
        anchors = self.get_anchor_points_scene()
        points = list(anchors)

        return points

    def get_anchor_points_scene(self) -> list[QPointF]:
        """Points d'ancrage de la courbe (hors points de contrôle Bézier), en coordonnées scène."""
        return [self.mapToScene(p) for p in self._points]

    def update_handles_position(self):
        if self._updating_handles:
            return
        self._updating_handles = True
        try:
            for index, point in enumerate(self._points):
                self.handles[f"point_{index}"].setPos(point)

            for seg_index, (cp1, cp2) in enumerate(self._controls):
                self.handles[f"cp1_{seg_index}"].setPos(cp1)
                self.handles[f"cp2_{seg_index}"].setPos(cp2)

            for control_role, line in self._guide_lines.items():
                kind, seg_index = self._parse_role(control_role)
                anchor_index = self._anchor_index_for_control(kind, seg_index)

                anchor_pos = self._points[anchor_index]
                control_pos = self.handles[control_role].pos()

                line.setLine(anchor_pos.x(), anchor_pos.y(), control_pos.x(), control_pos.y())
        finally:
            self._updating_handles = False

    def handle_press(self, role: str, event: QGraphicsSceneMouseEvent):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.save_item_geometry()

    def handle_released(self, role: str, event: QGraphicsSceneMouseEvent):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.save_history_geometry()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if self.flags().__contains__(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            self.setSelected(True)
            self.select_handle(True)
            self.update_handles_size(self.transform().m11())
            self.begin_move_tracking()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(event)
        self.end_move_tracking()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.select_handle(bool(value))
        return super().itemChange(change, value)

    def select_handle(self, visible: bool):
        for handle in self.handles.values():
            handle.setVisible(visible)
        for line in self._guide_lines.values():
            line.setVisible(visible)

    def save_item_geometry(self):
        self._old_geometry = self.get_item_geometry

    def save_history_geometry(self):
        new_geometry = self.get_item_geometry
        if self._old_geometry != new_geometry:
            cmd = ModifyItemCommand(self, self._old_geometry, new_geometry, "resize/move pathline")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        points = tuple((p.x(), p.y()) for p in self._points)
        controls = tuple(((c[0].x(), c[0].y()), (c[1].x(), c[1].y())) for c in self._controls)
        return pos.x(), pos.y(), points, controls

    def set_item_geometry(self, geometry):
        pos_x, pos_y, points, controls = geometry
        self.setPos(pos_x, pos_y)
        self._points = [QPointF(x, y) for x, y in points]
        self._controls = [[QPointF(*c[0]), QPointF(*c[1])] for c in controls]
        self._rebuild_path()
        self.update_handles_position()

    def to_dict(self) -> dict:
        return {
            "type": "pathline",
            "data": AdpaterItem.get_data(self),
            "geometry": {
                "points": [{"x": p.x(), "y": p.y()} for p in self._points],
                "controls": [
                    {"cp1": {"x": c[0].x(), "y": c[0].y()}, "cp2": {"x": c[1].x(), "y": c[1].y()}}
                    for c in self._controls
                ],
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
        flags = AdpaterItem.deserialize_flags(data.get("flags", []))

        geometry = data["geometry"]
        points = [QPointF(p["x"], p["y"]) for p in geometry["points"]]
        controls = [
            [QPointF(c["cp1"]["x"], c["cp1"]["y"]), QPointF(c["cp2"]["x"], c["cp2"]["y"])]
            for c in geometry["controls"]
        ]

        item = PathLineElement.create_custom_graphics_item(
            points=points,
            controls=controls,
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