from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent, QGraphicsItem, QGraphicsEllipseItem, \
    QGraphicsLineItem, QGraphicsTextItem

from adapter import AdpaterItem
from graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem


class GroupResizable(ResizableGraphicsItem, QGraphicsRectItem):

    def __init__(self, rect: QRectF, items=None):

        ResizableGraphicsItem.__init__(self)
        QGraphicsRectItem.__init__(self, rect, None)

        if items is None:
            items = []
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)

        self._items = []  # Liste pour suivre les items

        # Création des 4 Handles de redimensionnement
        self.create_handles()

        for item in items:
            self.add_to_group(item)


    def create_handles(self):
        """Crée les 4 Handles de redimensionnement."""
        rect = self.rect()
        self.add_handle("top_left", rect.topLeft())
        self.add_handle("top_right", rect.topRight())
        self.add_handle("bottom_left", rect.bottomLeft())
        self.add_handle("bottom_right", rect.bottomRight())
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

    def handle_moved(self, role: str, event: QGraphicsSceneMouseEvent):

        from graphic_view_element.GraphicItemManager.SquareElement.SquareResizable import SquareResizable
        from graphic_view_element.GraphicItemManager.CircleElement.CircleResizable import CircleResizable
        from graphic_view_element.GraphicItemManager.PixmapElement.PixmapResizable import PixmapResizable

        local_pos = self.mapFromScene(event.scenePos())
        rect = QRectF(self.rect())
        dec_x = 0
        dec_y = 0

        if role == "top_left":
            dec_x = rect.topLeft().x() - local_pos.x()
            dec_y = rect.topLeft().y() - local_pos.y()
            rect.setTopLeft(local_pos)

        elif role == "top_right":
            dec_x = rect.topRight().x() - local_pos.x()
            dec_y = rect.topRight().y() - local_pos.y()
            rect.setTopRight(local_pos)

        elif role == "bottom_left":
            dec_x = rect.bottomLeft().x() - local_pos.x()
            dec_y = rect.bottomLeft().y() - local_pos.y()
            rect.setBottomLeft(local_pos)

        elif role == "bottom_right":
            dec_x = rect.bottomRight().x() - local_pos.x()
            dec_y = rect.bottomRight().y() - local_pos.y()
            rect.setBottomRight(local_pos)

        rect = rect.normalized()
        self.setRect(rect)
        self.update_handles_position()

        print(dec_x)
        print(dec_y)

        for item in self._items:
            print(item)

            if isinstance(item, SquareResizable) or isinstance(item, CircleResizable) :

                rect = QRectF(item.rect())
                dec_y_temp = dec_y
                dec_x_temp = dec_x

                if dec_x < dec_y:
                    dec_y_temp = dec_x
                else :
                    dec_x_temp = dec_y

                if role == "top_left":
                    rect.setTopLeft(QPointF(rect.topLeft().x() - dec_x_temp, rect.topLeft().y() - dec_y_temp))
                elif role == "top_right":
                    rect.setTopRight(QPointF(rect.topRight().x() - dec_x_temp, rect.topRight().y() - dec_y_temp))
                elif role == "bottom_left":
                    rect.setBottomLeft(QPointF(rect.bottomLeft().x() - dec_x_temp, rect.bottomLeft().y() - dec_y_temp))
                elif role == "bottom_right":
                    rect.setBottomRight(QPointF(rect.bottomRight().x() - dec_x_temp, rect.bottomRight().y() - dec_y_temp))

                rect = rect.normalized()
                item.setRect(rect)

            elif isinstance(item, QGraphicsRectItem) or isinstance(item, QGraphicsEllipseItem) :
                rect = item.mapToParent(item.rect()).boundingRect()

                print(rect.topLeft().x())
                print(rect.topLeft().y())

                if role == "top_left":
                    rect.setTopLeft(QPointF(rect.topLeft().x() - dec_x, rect.topLeft().y() - dec_y))
                elif role == "top_right":
                    rect.setTopRight(QPointF(rect.topRight().x() - dec_x, rect.topRight().y() - dec_y))
                elif role == "bottom_left":
                    rect.setBottomLeft(QPointF(rect.bottomLeft().x() - dec_x, rect.bottomLeft().y() - dec_y))
                elif role == "bottom_right":
                    rect.setBottomRight(QPointF(rect.bottomRight().x() - dec_x, rect.bottomRight().y() - dec_y))

                rect = rect.normalized()

                rect = self.clamp_rect_to_group(rect)

                item.setPos(rect.topLeft())
                item.setRect(0, 0, rect.width(), rect.height())

            elif isinstance(item, PixmapResizable):

                pixmap_rect = QRectF(item.pos(), item.boundingRect().size())

                if role == "top_left":
                    pixmap_rect.setTopLeft(QPointF(pixmap_rect.topLeft().x() - dec_x, pixmap_rect.topLeft().y() - dec_y))
                elif role == "top_right":
                    pixmap_rect.setTopRight(QPointF(pixmap_rect.topRight().x() - dec_x, pixmap_rect.topRight().y() - dec_y))
                elif role == "bottom_left":
                    pixmap_rect.setBottomLeft(QPointF(pixmap_rect.bottomLeft().x() - dec_x, pixmap_rect.bottomLeft().y() - dec_y))
                elif role == "bottom_right":
                    pixmap_rect.setBottomRight(QPointF(pixmap_rect.bottomRight().x() - dec_x, pixmap_rect.bottomRight().y() - dec_y))

                pixmap_rect = pixmap_rect.normalized()

                pixmap_rect = self.clamp_rect_to_group(pixmap_rect)

                item.setPos(pixmap_rect.topLeft())

                item.resize_pixmap(pixmap_rect.width(), pixmap_rect.height())

            elif isinstance(item, QGraphicsLineItem):

                line = item.line()

                # 1. Points globaux SANS normalisation
                p1 = item.mapToParent(line.p1())
                p2 = item.mapToParent(line.p2())

                # 2. Créer un rect brut SANS normalisation
                x1, y1 = p1.x(), p1.y()
                x2, y2 = p2.x(), p2.y()

                rect = QRectF(x1, y1, x2 - x1, y2 - y1)

                # 3. Déplacement des coins selon le handle
                if role == "top_left":
                    rect.setTopLeft(QPointF(rect.topLeft().x() - dec_x, rect.topLeft().y() - dec_y))
                elif role == "top_right":
                    rect.setTopRight(QPointF(rect.topRight().x() - dec_x, rect.topRight().y() - dec_y))
                elif role == "bottom_left":
                    rect.setBottomLeft(QPointF(rect.bottomLeft().x() - dec_x, rect.bottomLeft().y() - dec_y))
                elif role == "bottom_right":
                    rect.setBottomRight(QPointF(rect.bottomRight().x() - dec_x, rect.bottomRight().y() - dec_y))

                # 4. Clamp dans le groupe
                rect = self.clamp_rect_to_group(rect)

                # 5. Mise à jour de la ligne en coordonnées locales
                item.setPos(rect.topLeft())

                new_p1 = QPointF(0, 0)
                new_p2 = QPointF(rect.width(), rect.height())

                item.setLine(new_p1.x(), new_p1.y(), new_p2.x(), new_p2.y())

            elif isinstance(item, QGraphicsTextItem):

                text_rect = QRectF(item.pos(), item.boundingRect().size())

                if role == "top_left":
                    text_rect.setTopLeft(QPointF(text_rect.topLeft().x() - dec_x, text_rect.topLeft().y() - dec_y))
                elif role == "top_right":
                    text_rect.setTopRight(QPointF(text_rect.topRight().x() - dec_x, text_rect.topRight().y() - dec_y))
                elif role == "bottom_left":
                    text_rect.setBottomLeft(QPointF(text_rect.bottomLeft().x() - dec_x, text_rect.bottomLeft().y() - dec_y))
                elif role == "bottom_right":
                    text_rect.setBottomRight(QPointF(text_rect.bottomRight().x() - dec_x, text_rect.bottomRight().y() - dec_y))

                text_rect = text_rect.normalized()

                text_rect = self.clamp_rect_to_group(text_rect)

                item.setPos(text_rect.topLeft())

                item.setTextWidth(text_rect.width())

                item.update()

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

        for i in self._items:
            i.select_handle(False)

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
        from draw.HistoryManager import ModifyItemCommand
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

        from graphic_view_element.GraphicItemManager.GroupElement.GroupElement import GroupElement

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
            
            items=reconstructed_children,  # <- enfants inclus ici
        )

        group.setTransform(transform)

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