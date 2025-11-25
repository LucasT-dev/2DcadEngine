from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent, QGraphicsItem

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
        self._create_handles()

        for item in items:
            self.add_to_group(item)


    def _create_handles(self):
        """Crée les 4 Handles de redimensionnement."""
        rect = self.rect()
        self.add_handle("top_left", rect.topLeft())
        self.add_handle("top_right", rect.topRight())
        self.add_handle("bottom_left", rect.bottomLeft())
        self.add_handle("bottom_right", rect.bottomRight())
        self.update_handles_position()
        print("test 21")


    def update_handles_position(self):
        """Met à jour la position de tous les Handles."""
        rect = self.rect()
        if not self.handles:
            return
        self.handles["top_left"].setPos(rect.topLeft())
        self.handles["top_right"].setPos(rect.topRight())
        self.handles["bottom_left"].setPos(rect.bottomLeft())
        self.handles["bottom_right"].setPos(rect.bottomRight())

    def handle_moved(self, role: str, new_pos: QPointF):
        pass

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

        print(self.brush().color().red())
        print(self.brush().color().green())
        print(self.brush().color().blue())
        print(self.brush().color().alpha()) # Alpha a 255 = erreur quelque part
        print("------------")
        print(self.pen().color().red())
        print(self.pen().color().green())
        print(self.pen().color().blue())
        print(self.pen().color().alpha())


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