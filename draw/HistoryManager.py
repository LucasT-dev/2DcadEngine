from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QUndoCommand, QTransform
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsTextItem, \
    QGraphicsLineItem, QGraphicsItem, QGraphicsItemGroup


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
        print("apply geometry")
        print(self.item)
        print(type(self.item))
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



        elif isinstance(self.item, QGraphicsItemGroup):

            print("UNDO/REDO group")

            x, y, w, h = geometry

            target = QRectF(x, y, w, h)

            self.set_group_scene_rect(self.item, target)



    def set_group_scene_rect(self, group: QGraphicsItemGroup, target: QRectF):
        """
        Applique une transform absolue au groupe telle que son rect englobant (en scène)
        devienne exactement `target`.
        """
        rL = group.childrenBoundingRect()
        if rL.isEmpty():
            return

        sx = target.width() / rL.width() if rL.width() > 0 else 1.0
        sy = target.height() / rL.height() if rL.height() > 0 else 1.0

        # Transform voulue en scène
        S = QTransform()
        S.translate(target.x(), target.y())
        S.scale(sx, sy)
        S.translate(-rL.x(), -rL.y())

        # Si le groupe a un parent, il faut compenser son transform
        parent = group.parentItem()
        P = parent.sceneTransform() if parent else QTransform()
        ok, P_inv = P.inverted()
        if not ok:
            P_inv = QTransform()

        T_local = P_inv * S
        group.setTransform(T_local, False)  # False = remplace la transform


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
    def __init__(self, scene, items, description="Group items"):
        super().__init__(description)
        self.scene = scene
        self.items = items
        self.group = None

    def redo(self):
        if not self.items:
            return

        # Créer le groupe si pas déjà fait
        if self.group is None:
            self.group = self.scene.createItemGroup(self.items)

            self.group.setFlags(
                QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            )

        else:
            # re-grouper après undo
            self.group = self.scene.createItemGroup(self.items)

        self.group.setSelected(True)

        # masquer handles individuels
        for item in self.items:
            if hasattr(item, "handles"):
                for h in item.handles.values():
                    h.setVisible(False)

        self.scene.invalidate(self.scene.sceneRect())
        self.scene.update()

    def undo(self):
        if not self.group:
            return

        self.group.setSelected(False)

        items = list(self.group.childItems())
        self.scene.destroyItemGroup(self.group)

        for item in items:
            item.setSelected(True)

            item.update()

        self.scene.invalidate(self.scene.sceneRect())
        self.scene.update()


