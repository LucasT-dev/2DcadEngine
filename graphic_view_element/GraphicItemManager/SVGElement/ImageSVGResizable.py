from PyQt6.QtCore import QRectF, QPointF, QLineF
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
        rect = self.boundingRect()
        if not self.handles:
            return

        self.handles["top_left"].setPos(self._top_left(rect))
        self.handles["top_right"].setPos(self._top_right(rect))
        self.handles["bottom_left"].setPos(self._bottom_left(rect))
        self.handles["bottom_right"].setPos(self._bottom_right(rect))

        self.handles["top"].setPos(self._mid_top(rect))
        self.handles["bottom"].setPos(self._mid_bottom(rect))
        self.handles["left"].setPos(self._mid_left(rect))
        self.handles["right"].setPos(self._mid_right(rect))

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):

        if not self.get_item_is_resizable():
            return

        scene_pos = event.scenePos()
        local_pos = self.mapFromScene(scene_pos)
        rect = self.boundingRect()

        if role in ("top_left", "top_right", "bottom_left", "bottom_right"):
            anchor = {
                "top_left": rect.bottomRight(),
                "top_right": rect.bottomLeft(),
                "bottom_left": rect.topRight(),
                "bottom_right": rect.topLeft(),
            }[role]

            new_width = abs(local_pos.x() - anchor.x())
            new_height = abs(local_pos.y() - anchor.y())

        elif role in ("top", "bottom"):
            # Redimensionnement vertical seul : l'ancrage horizontal ne bouge pas,
            # donc la largeur reste inchangée (scale_x = 1).
            anchor = rect.bottomLeft() if role == "top" else rect.topLeft()

            new_width = rect.width()
            new_height = abs(local_pos.y() - anchor.y())

        elif role in ("left", "right"):
            anchor = rect.topRight() if role == "left" else rect.topLeft()

            new_width = abs(local_pos.x() - anchor.x())
            new_height = rect.height()

        else:
            return

        old_width = rect.width()
        old_height = rect.height()

        if old_width < 1e-6 or old_height < 1e-6:
            return

        scale_x = max(new_width / old_width, 0.01)
        scale_y = max(new_height / old_height, 0.01)

        t = QTransform()
        t.translate(anchor.x(), anchor.y())
        t.scale(scale_x, scale_y)
        t.translate(-anchor.x(), -anchor.y())

        self.setTransform(t, True)

        self.prepareGeometryChange()
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

    def get_line_of_interest(self) -> list[QLineF]:
        rect = self.boundingRect()

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
        self.update_handles_size(self.transform().m11())
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

        points_data = data.get("points_of_interest", [])
        for p in points_data:
            point: QPointF = AdpaterItem.point_from_dict(p["p"])
            item.add_point_of_interest(point)

        return item

    def rect(self):
        return self.rect
