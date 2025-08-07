from PyQt6.QtGui import QUndoCommand


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
        Applique une géométrie selon le type d'item :
        - QGraphicsLineItem: tuple(x1, y1, x2, y2)
        - QGraphicsRectItem / QGraphicsEllipseItem: QRectF
        - QGraphicsTextItem: QPointF (position)
        """
        from PyQt6.QtWidgets import (
            QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
        )

        if isinstance(self.item, QGraphicsLineItem):
            self.item.setLine(*geometry)

        elif isinstance(self.item, (QGraphicsRectItem, QGraphicsEllipseItem)):
            self.item.setRect(*geometry)


        elif isinstance(self.item, QGraphicsTextItem):

            # geometry = (x, y, w, h)

            x, y, w, _ = geometry

            self.item.setPos(x, y)  # ✅ garde la position absolue

            self.item.setTextWidth(max(w, 1.0))  # ✅ met à jour la largeur

    def details(self):
        """Retourne une chaîne décrivant l’état avant/après pour l’historique"""
        return f"{self.text()} | Avant: {self.old_geometry} -> Après: {self.new_geometry}"