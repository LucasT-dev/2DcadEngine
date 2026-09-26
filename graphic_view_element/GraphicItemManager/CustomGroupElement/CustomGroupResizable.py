from PyQt6.QtCore import QPointF, QRectF, QLineF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent, QGraphicsItem, QGraphicsEllipseItem, \
    QGraphicsLineItem, QGraphicsTextItem

from libs.cadengine.adapter import AdpaterItem
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class CustomGroupResizable(ResizableGraphicsItem, QGraphicsRectItem):

    def __init__(self, rect: QRectF, items=None):

        QGraphicsRectItem.__init__(self, rect, None)
        ResizableGraphicsItem.__init__(self)

        if items is None:
            items = []
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)

        self._items = []  # Liste pour suivre les items

        # Création des 4 Handles de redimensionnement
        self._create_handles()

        for item in items:
            self.add_to_group(item)

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

    def delete_handle(self):
        for handle in self.handles:
            self.scene().removeItem(handle)

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

        if not self.get_item_is_resizable():
            return

        local_pos = self.mapFromScene(event.scenePos())
        rect = QRectF(self.rect())

        anchor = {
            "top_left": rect.bottomRight(),
            "top_right": rect.bottomLeft(),
            "bottom_left": rect.topRight(),
            "bottom_right": rect.topLeft(),
        }.get(role)

        if anchor is None:
            return

        old_width = rect.width()
        old_height = rect.height()

        if old_width < 1e-6 or old_height < 1e-6:
            return

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

        scale_x = max(rect.width() / old_width, 0.01)
        scale_y = max(rect.height() / old_height, 0.01)

        self.setRect(rect)
        self.update_handles_position()

        self._scale_items(anchor, scale_x, scale_y)

    def _scale_items(self, anchor: QPointF, scale_x: float, scale_y: float):
        """
        Redimensionne chaque item du groupe proportionnellement, en gardant
        ses positions et proportions relatives au reste du groupe. 'anchor'
        est exprimé dans le même repère que rect() du groupe (coordonnées
        locales, donc identique au repère parent des items enfants).
        """
        from libs.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquareResizable import SquareResizable
        from libs.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CircleResizable import CircleResizable
        from libs.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapResizable import PixmapResizable

        def scaled_point(p: QPointF) -> QPointF:
            return QPointF(
                anchor.x() + (p.x() - anchor.x()) * scale_x,
                anchor.y() + (p.y() - anchor.y()) * scale_y,
            )

        for item in self._items:

            if isinstance(item, (SquareResizable, CircleResizable)):
                rect = QRectF(item.rect())
                top_left = item.mapToParent(rect.topLeft())
                bottom_right = item.mapToParent(rect.bottomRight())

                new_rect = QRectF(scaled_point(top_left), scaled_point(bottom_right)).normalized()
                item.setPos(new_rect.topLeft())
                item.setRect(0, 0, new_rect.width(), new_rect.height())

            elif isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
                rect = QRectF(item.pos(), item.rect().size())
                new_rect = QRectF(scaled_point(rect.topLeft()), scaled_point(rect.bottomRight())).normalized()

                item.setPos(new_rect.topLeft())
                item.setRect(0, 0, new_rect.width(), new_rect.height())

            elif isinstance(item, PixmapResizable):
                rect = QRectF(item.pos(), item.boundingRect().size())
                new_rect = QRectF(scaled_point(rect.topLeft()), scaled_point(rect.bottomRight())).normalized()

                item.setPos(new_rect.topLeft())
                item.resize_pixmap(new_rect.width(), new_rect.height())

            elif isinstance(item, QGraphicsLineItem):
                line = item.line()

                p1 = scaled_point(item.mapToParent(line.p1()))
                p2 = scaled_point(item.mapToParent(line.p2()))

                item.setPos(0, 0)
                item.setLine(p1.x(), p1.y(), p2.x(), p2.y())

            elif isinstance(item, QGraphicsTextItem):
                rect = QRectF(item.pos(), item.boundingRect().size())
                new_rect = QRectF(scaled_point(rect.topLeft()), scaled_point(rect.bottomRight())).normalized()

                item.setPos(new_rect.topLeft())
                item.setTextWidth(max(new_rect.width(), 1.0))

    def _calcul_point_of_interest(self):
        """L'utilisateur est libre de mettre les points d'interet"""
        return []

    def _add_point_of_interest(self):

        for p in self._calcul_point_of_interest():
            self.add_point_of_interest(p)

        return self._custom_points_of_interest

    def _update_point_of_interest(self):

        for index, p in enumerate(self._calcul_point_of_interest()):
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
        """Gestion de l'appui sur un group."""
        self.setSelected(True)
        self.select_handle(True)

        for i in self._items:
            i.select_handle(False)

        self.begin_move_tracking()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Gestion du relâchement sur un group."""
        self.end_move_tracking()

        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Gestion des changements d'état du group."""
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
        from libs.cadengine.draw.HistoryManager import ModifyItemCommand
        new_group = self.get_item_geometry

        if self._old_geometry != new_group:
            cmd = ModifyItemCommand(self, self._old_geometry, new_group, "resize/move group")
            self.scene().undo_stack.push(cmd)

    @property
    def get_item_geometry(self):
        rect = self.rect()
        return self.pos().x(), self.pos().y(), rect.x(), rect.y(), self.rect().width(), self.rect().height()

    def add_to_group(self, item):
        """Ajoute un item au groupe en conservant sa position visuelle"""
        # Stocke la position scène originale
        original_scene_pos = item.scenePos()

        # Ajoute l'item au groupe
        item.setParentItem(self)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        item.select_handle(False)

        # Ajuste la position pour conserver l'emplacement visuel
        item.setPos(self.mapFromScene(original_scene_pos))

        # Ajoute à la liste
        self._items.append(item)
        self.updateGeometry()

    def updateGeometry(self):
        """Met à jour la géométrie du groupe"""
        self.prepareGeometryChange()

        # Calcule le boundingRect englobant tous les enfants
        rect = QRectF()
        for item in self._items:
            child_rect = item.boundingRect()
            mapped_rect = item.mapRectToParent(child_rect)
            rect = rect.united(mapped_rect)

        # Force une taille minimale
        if rect.isEmpty():
            rect = QRectF(0, 0, 10, 10)

        self.setRect(rect)
        self.update_handles_position()
        self.update()


    def to_dict(self) -> dict:
        r: QRectF = self.rect()

        # Sérialisation des enfants : forçage via to_dict() si dispo
        items_data = []
        for child in self.childItems():

            # ignore handles, helpers, etc (optionnel)
            if not hasattr(child, "to_dict"):
                continue

            items_data.append(child.to_dict())

        return {
            "type" : "group",
            "data" : AdpaterItem.get_data(self),

            "geometry" : {
                "x": r.x(),
                "y": r.y(),
                "w": r.width(),
                "h": r.height(),
            },
            "pen" : AdpaterItem.get_pen(self),
            "brush" : AdpaterItem.get_brush(self),
            "flags": AdpaterItem.serialize_flags(self),

            "items": items_data
        }

    @classmethod
    def from_dict(cls, data: dict):

        from libs.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupElement import GroupElement

        item_data = data["data"]
        transform = AdpaterItem.dict_to_transform(data=item_data["transform"])

        geometry = data["geometry"]
        x, y, w, h = geometry["x"], geometry["y"], geometry["w"], geometry["h"]

        flags_data = data.get("flags", [])
        flags = AdpaterItem.deserialize_flags(flags_data)

        pen = AdpaterItem.dict_to_pen(data["pen"])
        brush = AdpaterItem.dict_to_brush(data["brush"])

        # --- RECONSTRUCTION DES ENFANTS ---
        children_data = data.get("items", [])
        reconstructed_children = []

        for child_dict in children_data:
            # Récupération du chemin de classe (déjà présent dans "data")
            class_path = child_dict.get("data", {}).get("class", None)

            if class_path is None:
                print("[WARN] Enfant sans 'class' :", child_dict)
                continue

            # Résolution dynamique
            child_class = AdpaterItem.resolve_class_from_path(class_path)

            if child_class is None:
                print("[ERROR] Impossible de résoudre :", class_path)
                continue

            # Vérifier que la classe a bien from_dict
            if not hasattr(child_class, "from_dict"):
                print("[ERROR] Classe sans from_dict :", child_class)
                continue

            # Appeler from_dict
            child_item = child_class.from_dict(child_dict)
            reconstructed_children.append(child_item)

        group = GroupElement.create_custom_graphics_item(
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
            flags=flags,
            
            items=reconstructed_children,  # enfants inclus ici
        )

        group.setTransform(transform)

        points_data = data.get("points_of_interest", [])
        for p in points_data:
            point: QPointF = AdpaterItem.point_from_dict(p["p"])
            group.add_point_of_interest(point)

        return group

    def clamp_rect_to_group(self, child_rect: QRectF) -> QRectF:
        """Contraint un QRectF enfant à rester dans les limites du groupe."""
        group_rect = self.rect()
        clamped = QRectF(child_rect)

        # Corrige la position X
        if clamped.left() < group_rect.left():
            dx = group_rect.left() - clamped.left()
            clamped.translate(dx, 0)
        if clamped.right() > group_rect.right():
            dx = group_rect.right() - clamped.right()
            clamped.translate(dx, 0)

        # Corrige la position Y
        if clamped.top() < group_rect.top():
            dy = group_rect.top() - clamped.top()
            clamped.translate(0, dy)
        if clamped.bottom() > group_rect.bottom():
            dy = group_rect.bottom() - clamped.bottom()
            clamped.translate(0, dy)

        return clamped