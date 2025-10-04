from PyQt6.QtCore import QCoreApplication, QPointF
from PyQt6.QtGui import QUndoCommand, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsTextItem, \
    QGraphicsLineItem, QGraphicsItem, QGraphicsScene

from graphic_view_element.resizable_element.GroupeResize_3 import GroupResize_3


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
    def __init__(self, item, old_geometry, new_geometry, description="Modifier élément"):
        super().__init__(description)
        self.item = item
        self.old_geometry = old_geometry
        self.new_geometry = new_geometry

    def undo(self):
        self.apply_geometry(self.old_geometry)

    def redo(self):
        self.apply_geometry(self.new_geometry)

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

        # Stocke les positions originales
        for item in self.selected_items:
            self._original_positions[item] = item.scenePos()

        # Calcule le centre des items sélectionnés
        center = QPointF()
        for item in self.selected_items:
            center += item.scenePos()
        center /= len(self.selected_items)

        # Crée le groupe
        self._group = GroupResize_3()
        self._group.setPos(center)
        self.scene().addItem(self._group)

        # Ajoute les items au groupe
        for item in self.selected_items:
            self._group.addToGroup(item)

        # Sélectionne le groupe
        self._group.setSelected(True)
        self.scene().update()

    def undo(self):
        if not self._group:
            return

        # Dissout le groupe
        for item in self._group._items:
            item.setParentItem(None)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            if item in self._original_positions:
                item.setPos(self._original_positions[item])
            self.scene().addItem(item)

        # Supprime le groupe
        self.scene().removeItem(self._group)
        self.scene().update()


class UngroupItemsCommand(QUndoCommand):
    def __init__(self, scene, group, description="Ungroup items"):
        super().__init__(description)
        self.scene = scene
        self._group = group
        self._children = list(group.childItems())  # on mémorise les enfants pour pouvoir refaire le regroupement

        print(self._group)

    def redo(self):
        """Dissocie le groupe"""
        if not self._group:
            return

        # Désactiver sélection/déplacement du groupe
        self._group.setSelected(False)
        self._group.setFlags(QGraphicsItem.GraphicsItemFlag(0))

        # Dissocier le groupe
        self.scene().destroyItemGroup(self._group)

        # Réactiver la sélection et handles des enfants
        for it in self._children:
            it.setSelected(True)
            it.setVisible(True)
            it.update()

        self._group = None

        # Rafraîchissement
        self.scene().invalidate(self.scene().sceneRect(), QGraphicsScene.SceneLayer.AllLayers)
        self.scene().update()
        for v in self.scene().views():
            v.viewport().update()

    def undo(self):
        """Recrée le groupe avec les enfants d'origine"""
        if not self._children:
            return

        # Masquer la sélection/handles des enfants
        for it in self._children:
            it.setSelected(False)
            it.setVisible(False)
            it.update()

        # Recréer le groupe
        self._group = None #GroupResize(self._children)
        self._group.setFlags(
            self._group.flags()
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self._group.setSelected(True)

        # Rafraîchissement
        self.scene().invalidate(self.scene().sceneRect(), QGraphicsScene.SceneLayer.AllLayers)
        self.scene().update()
        for v in self.scene().views():
            v.viewport().update()



def flash_dummy(scene, pos):

    print("dummy 2")

    dummy = QGraphicsRectItem(0, 0, 1, 1)
    print("dummy 3")
    dummy.setBrush(QBrush(QColor(0,0,0,0)))
    print("dummy 4")
    #dummy.setPos(pos)

    print("add dummmy")

    scene.addItem(dummy)

    print("delete dummmy")
    scene.removeItem(dummy)

    print("ok dummmy")
    # nettoyage
    try:
        del dummy
    except Exception:
        pass
    scene.update()
    for v in scene.views():
        v.viewport().update()
    QCoreApplication.processEvents()

