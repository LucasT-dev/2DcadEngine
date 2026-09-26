from PyQt6.QtCore import QRectF, QPointF, QTimer, QLineF
from PyQt6.QtGui import QPen, QBrush, QTransform
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent, QGraphicsItem

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.draw.HistoryManager import ModifyItemCommand
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class SquareResizable(ResizableGraphicsItem, QGraphicsRectItem):

    def __init__(self, rect: QRectF, parent=None):

        QGraphicsRectItem.__init__(self, rect, parent)
        ResizableGraphicsItem.__init__(self)

        # Création des 4 Handles de redimensionnement
        self._create_handles()

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
        rect = self.rect()

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
        rect = self.rect()
        if not self.handles:
            return
        self.handles["top_left"].setPos(rect.topLeft())
        self.handles["top_right"].setPos(rect.topRight())
        self.handles["bottom_left"].setPos(rect.bottomLeft())
        self.handles["bottom_right"].setPos(rect.bottomRight())

        self.handles["top"].setPos(self._mid_top(rect))
        self.handles["bottom"].setPos(self._mid_bottom(rect))
        self.handles["left"].setPos(self._mid_left(rect))
        self.handles["right"].setPos(self._mid_right(rect))

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):
        """Appelé quand un handle est déplacé (par Handle)."""

        if not self.get_item_is_resizable(): return  # The item is not resizable.

        # Convertit la position de la scène vers le repère local
        scene_pos = event.scenePos()
        local_pos = self.mapFromScene(scene_pos)
        rect = QRectF(self.rect())

        snap_point_other_q_graphics_item = self._find_snap_point(self.scene(), scene_pos, item_moved=self)
        if snap_point_other_q_graphics_item:
            local_pos = self.mapFromScene(snap_point_other_q_graphics_item)

        if role in ("top_left", "top_right", "bottom_left", "bottom_right"):
            fixed = {
                "bottom_right": rect.topLeft(),
                "bottom_left": rect.topRight(),
                "top_right": rect.bottomLeft(),
                "top_left": rect.bottomRight(),
            }[role]

            dx = local_pos.x() - fixed.x()
            dy = local_pos.y() - fixed.y()

            size = max(abs(dx), abs(dy))
            dx = size if dx >= 0 else -size
            dy = size if dy >= 0 else -size

            rect = QRectF(fixed, QPointF(fixed.x() + dx, fixed.y() + dy))

        elif role in ("top", "bottom", "left", "right"):
            center = rect.center()
            if role in ("top", "bottom"):
                new_radius = abs(local_pos.y() - center.y())
            else:
                new_radius = abs(local_pos.x() - center.x())
            rect = QRectF(
                center.x() - new_radius, center.y() - new_radius,
                new_radius * 2, new_radius * 2
            )

        rect = rect.normalized()
        self.setRect(rect)
        QTimer.singleShot(0, self.update_handles_position)

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

    def get_line_of_interest(self) -> list[QLineF]:
        rect = self.rect()

        tl = self.mapToScene(rect.topLeft())
        tr = self.mapToScene(rect.topRight())
        br = self.mapToScene(rect.bottomRight())
        bl = self.mapToScene(rect.bottomLeft())

        return [
            QLineF(tl, tr),  # côté haut
            QLineF(tr, br),  # côté droit
            QLineF(br, bl),  # côté bas
            QLineF(bl, tl),  # côté gauche
        ]


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
        """Gestion de l'appui sur l'ellipse."""

        if self.flags().__contains__(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            self.setSelected(True)
            self.select_handle(True)

        self.begin_move_tracking()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement de l'ellipse."""
        self.end_move_tracking()

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
        new_square = self.get_item_geometry

        if self._old_geometry != new_square:
            cmd = ModifyItemCommand(self, self._old_geometry, new_square, "resize/move square")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        r = self.rect()
        return pos.x(), pos.y(), r.x(), r.y(), r.width(), r.height()


    def to_dict(self) -> dict:
        r: QRectF = self.rect()

        return {
            "type": "square",
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

        from libs.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquareElement import SquareElement

        geometry = data["geometry"]
        pen: QPen = AdpaterItem.dict_to_pen(data=data["pen"])
        brush: QBrush = AdpaterItem.dict_to_brush(data=data["brush"])
        item_data = data["data"]
        transform = AdpaterItem.dict_to_transform(data=item_data["transform"])
        flags_data = data.get("flags", [])

        x, y, w, h = geometry["x"], geometry["y"], geometry["w"], geometry["h"]

        flags = AdpaterItem.deserialize_flags(flags_data)

        item = SquareElement.create_custom_graphics_item(
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

        points_data = data.get("points_of_interest", [])
        for p in points_data:
            point: QPointF = AdpaterItem.point_from_dict(p["p"])
            item.add_point_of_interest(point)

        return item