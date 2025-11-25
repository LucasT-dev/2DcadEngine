from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QUndoCommand, QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsTextItem, \
    QGraphicsLineItem, QGraphicsItem

from graphic_view_element.GraphicItemManager.GroupElement.GroupElement import GroupElement
from graphic_view_element.GraphicItemManager.GroupElement.GroupResizable import GroupResizable


class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item, description="add element"):
        super().__init__(description)
        self.scene = scene
        self.item = item

    def undo(self):
        self.scene.removeItem(self.item)

    def redo(self):
        self.scene.addItem(self.item)


class RemoveItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__(f"delete item {item.__class__.__name__}" )
        self.scene = scene
        self.item = item
        self.was_in_scene = True

        # 🔹 On stocke tous les enfants pour éviter le crash

        self.children = item.childItems() if item else []

        # 🔹 Forcer leur détachement pour éviter destruction auto par Qt
        for child in self.children:
            child.setParentItem(None)

    def undo(self):

        if not self.was_in_scene:
            # 🔄 Re-parent les enfants
            for child in self.children:
                self.scene().addItem(child)
                child.setParentItem(self.item)

            self.scene().addItem(self.item)
            self.was_in_scene = True

    def redo(self):

        if self.was_in_scene:

            for child in self.children:
                self.scene().removeItem(child)

            self.scene().removeItem(self.item)
            self.was_in_scene = False


class ModifyItemCommand(QUndoCommand):
    def __init__(self, item, old_geometry, new_geometry, description="modify item"):
        super().__init__(description)
        self.item = item
        self.old_geometry = old_geometry
        self.new_geometry = new_geometry

    def undo(self):
        self.apply_geometry(self.old_geometry)
        self.item.update_handles_position()

    def redo(self):
        self.apply_geometry(self.new_geometry)
        self.item.update_handles_position()

    def apply_geometry(self, geometry):
        """
        geometry :
        - LineItem : (pos_x, pos_y, x1, y1, x2, y2)
        - Rect/Ellipse : (pos_x, pos_y, rect_x, rect_y, rect_w, rect_h)
        - Pixmap : (pos_x, pos_y, width, height)
        - Text : (pos_x, pos_y, width, height)
        """

        if isinstance(self.item, QGraphicsLineItem):
            x, y, x1, y1, x2, y2 = geometry
            self.item.setPos(x, y)
            self.item.setLine(x1, y1, x2, y2)

        elif isinstance(self.item, (QGraphicsRectItem, QGraphicsEllipseItem)):
            pos_x, pos_y, rx, ry, rw, rh = geometry
            self.item.setPos(pos_x, pos_y)
            self.item.setRect(rx, ry, rw, rh)

        elif isinstance(self.item, QGraphicsPixmapItem):
            pos_x, pos_y, width, height = geometry
            self.item.setPos(pos_x, pos_y)
            # Redimensionner le pixmap
            pixmap = self.item.pixmap()
            if not pixmap.isNull():
                self.item.setPixmap(pixmap.scaled(width, height))

        elif isinstance(self.item, QGraphicsTextItem):
            pos_x, pos_y, width, height = geometry
            self.item.setPos(pos_x, pos_y)
            self.item.setTextWidth(max(width, 1.0))

    def details(self):
        """Retourne une chaîne décrivant l’état avant/après pour l’historique"""
        return f"{self.text()} | Avant: {self.old_geometry} -> Après: {self.new_geometry}"


def capture_item_properties(item: QGraphicsItem):
    """Capture toutes les propriétés actuelles d'un item dans un dict."""
    props = {}

    # Bordure
    if hasattr(item, "pen"):
        pen = item.pen()
        props["border_color"] = pen.color()
        props["border_width"] = pen.width()
        props["border_style"] = pen.style()

    # Remplissage
    if hasattr(item, "brush"):
        brush = item.brush()
        props["fill_color"] = brush.color()

    # Z-value
    props["z_value"] = item.zValue()

    # Texte (si c'est un QGraphicsTextItem ou équivalent)
    if hasattr(item, "toPlainText"):
        props["text"] = item.toPlainText()
        props["text_color"] = item.defaultTextColor()
        props["font"] = item.font()
        props["text_width"] = item.textWidth()

    return props


class ModifyItemPropertiesCommand(QUndoCommand):

    def __init__(self, old_item: QGraphicsItem, new_item: QGraphicsItem, description="modify item properties"):
        super().__init__(description)
        self.item = old_item
        self.old_props = capture_item_properties(old_item)
        self.new_props = capture_item_properties(new_item)

    def undo(self):
        self.apply_properties(self.old_props)

    def redo(self):
        self.apply_properties(self.new_props)

    def apply_properties(self, props: dict):
        """Applique toutes les propriétés sauvegardées à l'item."""
        # --- Bordure ---
        if "border_color" in props:
            pen = self.item.pen()
            pen.setColor(props["border_color"])
            self.item.setPen(pen)

        if "border_width" in props:
            pen = self.item.pen()
            pen.setWidth(props["border_width"])
            self.item.setPen(pen)

        if "border_style" in props:
            pen = self.item.pen()
            pen.setStyle(props["border_style"])
            self.item.setPen(pen)

        # --- Remplissage ---
        if "fill_color" in props:
            brush = self.item.brush()
            brush.setColor(props["fill_color"])
            self.item.setBrush(brush)

        # --- Z-value ---
        if "z_value" in props:
            self.item.setZValue(props["z_value"])

        # --- Texte (si applicable) ---
        if hasattr(self.item, "setPlainText"):
            if "text" in props:
                self.item.setPlainText(props["text"])

            if "text_color" in props:
                self.item.setDefaultTextColor(props["text_color"])

            if "font" in props:
                self.item.setFont(props["font"])

            if "text_width" in props:
                self.item.setTextWidth(props["text_width"])




class GroupItemsCommand(QUndoCommand):

    def __init__(self, scene, description="Group items", selected_items = None):
        super().__init__(description)
        self.scene = scene
        self._group = None
        self.selected_items = selected_items or []
        self._original_positions = {}

    def redo(self):
        if not self.selected_items:
            return

        print("test 8")

        # Stocke les positions originales
        for item in self.selected_items:
            self._original_positions[item] = item.scenePos()

        print("test 9")

        # Calcule le centre des items sélectionnés
        center = QPointF()
        for item in self.selected_items:
            center += item.scenePos()
        center /= len(self.selected_items)

        print("test 10")

        # Crée le groupe
        self._group = GroupElement.create_custom_graphics_item(first_point=QPointF(0,0), second_point=QPointF(0,0),
                                                               border_color=QColor(0,0,0,255), border_style=Qt.PenStyle.SolidLine,
                                                               border_width=1, fill_color=QColor(0,0,0,0)) # GroupResizable(QRectF(0,0,0,0))
        self.scene().addItem(self._group)
        print("test 11")
        self._group.setPos(center)
        print("test 12")

        print("test 13")

        # Ajoute les items au groupe
        for item in self.selected_items:
            self._group.add_to_group(item)

        print("test 14")

        # Sélectionne le groupe
        self._group.setSelected(True)
        print("test 15")
        self.scene().update()

    def undo(self):
        if not self._group:
            return

        group_items = self._group.childItems.copy()

        # Supprime le groupe
        self.scene().removeItem(self._group)

        # Restaure les items à leur position d'origine (dans la scène)
        for item in group_items:
            self.scene().addItem(item)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            item.setSelected(True)

        self.scene().update()


class UngroupItemsCommand(QUndoCommand):
    def __init__(self, scene, group_item, description="Ungroup items"):
        """
        :param scene: la QGraphicsScene sur laquelle on agit
        :param group_item: l'objet groupe à décomposer
        """
        super().__init__(description)
        self.scene = scene
        self._group = group_item
        self._items = []
        self._original_positions = {}

    def redo(self):
        """Dégroupe les items du groupe et les remet dans la scène"""
        if not self._group:
            return

        # Sauvegarde des items et de leur position dans le groupe
        self._items = list(self._group.childItems())
        self._original_positions.clear()
        self._group.setSelected(False)

        for item in self._items:
            # Position absolue dans la scène
            scene_pos = self._group.mapToScene(item.pos())
            self._original_positions[item] = scene_pos

        # Retire le groupe de la scène
        self.scene().removeItem(self._group)

        # Réajoute les items indépendamment
        for item in self._items:
            item.setParentItem(None)
            item.setPos(self._original_positions[item])
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            item.setSelected(True)
            self.scene().addItem(item)

        self.scene().update()

    def undo(self):
        """Rétablit le groupe et remet les items dedans"""
        if not self._items:
            return

        # Recrée un groupe à la position initiale
        new_group = type(self._group)()  # suppose que ton GroupResize_3() est la classe du groupe
        new_group.setPos(self._group.scenePos())
        self.scene().addItem(new_group)

        # Réintègre les items
        for item in self._items:
            new_group.add_to_group(item)

        # Restaure l'état
        new_group.setSelected(True)
        self._group = new_group
        self.scene().update()


