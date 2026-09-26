from PyQt6.QtCore import QPointF, Qt, QTimer, QLineF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsItem, QGraphicsSceneMouseEvent

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.draw.HistoryManager import ModifyItemCommand
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class TextResizable(ResizableGraphicsItem, QGraphicsTextItem):

    def __init__(self):

        QGraphicsTextItem.__init__(self)
        ResizableGraphicsItem.__init__(self)

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._create_handles()


    def _create_handles(self):

        rect = self.boundingRect()

        self.add_handle("top_left", rect.topLeft())
        self.add_handle("top_right", rect.topRight())
        self.add_handle("bottom_left", rect.bottomLeft())
        self.add_handle("bottom_right", rect.bottomRight())

        self.update_handles_position()

    def update_handles_position(self):

        r = self.boundingRect()

        self.handles["top_left"].setPos(r.topLeft())
        self.handles["top_right"].setPos(r.topRight())
        self.handles["bottom_left"].setPos(r.bottomLeft())
        self.handles["bottom_right"].setPos(r.bottomRight())

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):

        if not self.get_item_is_resizable(): return  # The item is not resizable.

        rect = self.boundingRect()
        new_pos = self.mapFromScene(event.scenePos())

        if role in {"top_right", "bottom_right"}:
            # Redimension depuis la droite
            new_width = max(new_pos.x() - rect.x(), 1.0)
            self.setTextWidth(new_width)

        elif role in {"top_left", "bottom_left"}:
            # Redimension depuis la gauche
            diff = new_pos.x() - rect.x()
            new_width = max(rect.width() - diff, 1.0)
            self.setTextWidth(new_width)
            self.setPos(self.pos() + QPointF(diff, 0))  # décaler à gauche

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
            self.update_handles_position()

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


    def mouseDoubleClickEvent(self, event):
        # Active l'édition
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        # Quitte l'édition
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        super().focusOutEvent(event)

    def save_item_geometry(self):
        self._old_geometry = self.get_item_geometry

    def save_history_geometry(self):
        new_text = self.get_item_geometry

        if self._old_geometry != new_text:
            cmd = ModifyItemCommand(self, self._old_geometry, new_text, "resize/move square")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        pos = self.pos()
        w = self.textWidth()
        h = self.boundingRect().height()
        return pos.x(), pos.y(), w, h

    def to_dict(self) -> dict:

        return {
            "type": "text",
            "data": AdpaterItem.get_data(self),

            "geometry": {
                "x": self.pos().x(),
                "y": self.pos().y(),
            },
            "text": self.toPlainText(),
            "text_width": self.textWidth(),
            "font": AdpaterItem.font_to_dict(self.font()),
            "default_text_color": AdpaterItem.rgba_to_hex(self.defaultTextColor()),
            "flags": AdpaterItem.serialize_flags(self)
        }

    @classmethod
    def from_dict(cls, data: dict):

        from libs.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextElement import TextElement

        font = AdpaterItem.font_from_dict(data["font"])
        text_color = AdpaterItem.hex_to_rgba(data["default_text_color"])

        item_data = data["data"]

        transform = AdpaterItem.dict_to_transform(item_data["transform"])
        visibility = item_data["visibility"]
        scale = item_data["scale"]

        geometry = data["geometry"]
        x, y = geometry["x"], geometry["y"]

        flags_data = data.get("flags", [])
        flags = AdpaterItem.deserialize_flags(flags_data)

        item = TextElement.create_custom_graphics_item(
            first_point=QPointF(x, y),
            second_point=QPointF(x + 1, y + 1),
            text=data["text"],
            text_color=text_color,
            font=font,
            text_width=data["text_width"],
            z_value=item_data["z_value"],
            key=int(list(item_data["data"].keys())[0]) if item_data["data"] else 0,
            value=list(item_data["data"].values())[0] if item_data["data"] else "",
            transform=QTransform(),
            visibility=visibility,
            scale=scale,
            flags=flags
        )

        item.setTransform(transform)

        points_data = data.get("points_of_interest", [])
        for p in points_data:
            point: QPointF = AdpaterItem.point_from_dict(p["p"])
            item.add_point_of_interest(point)

        return item