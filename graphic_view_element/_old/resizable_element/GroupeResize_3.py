from PyQt6.QtCore import QRectF, Qt, QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtGui import QPen, QColor, QBrush, QCursor

from graphic_view_element.style.HandleStyle import HandleStyle
from graphic_view_element._old.serialisation.SerializableGraphicsItem import SerializableGraphicsItem

class Handle(QGraphicsEllipseItem):

    """Classe pour les poignées de redimensionnement"""
    def __init__(self, parent, position):
        super().__init__(-4, -4, HandleStyle.SIZE, HandleStyle.SIZE)
        self._original_pos = None
        self._start_pos = None
        self._initial_rect = None
        self._drag_start = None
        self.setParentItem(parent)
        self.setBrush(QBrush(QColor(HandleStyle.FILL_COLOR)))
        self.setPen(QPen(QColor(HandleStyle.BORDER_COLOR)))
        self.setZValue(1000)
        #self.setCursor(self._cursor_for_position(position))
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)
        self.position = position

    def mousePressEvent(self, event):
        print("Start event press handle")
        self.setBrush(QBrush(QColor(0, 120, 215)))  # Bleu quand cliqué
        self._initial_rect = self.parentItem().boundingRect()
        self._start_pos = event.scenePos()
        self._original_pos = self.scenePos()
        event.accept()

    def mouseMoveEvent(self, event):
        print("Start event move handle")

        new_pos = self._original_pos + (event.scenePos() - self._start_pos)
        parent = self.parentItem()
        parent.resize(self.position, parent.mapFromScene(new_pos))

        event.accept()

    def mouseReleaseEvent(self, event):
        print("Start event release handle")
        self.setBrush(QBrush(QColor(255, 255, 255, 0)))  # Reviens en blanc
        self._drag_start = None
        self._initial_rect = None
        event.accept()

    def hoverEnterEvent(self, event):

        # Change le curseur selon la position du handle
        if self.position in ["tr", "bl"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        elif self.position in ["tl", "br"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        elif self.position in ["t", "b"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        elif self.position in ["l", "r"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))

        super().hoverEnterEvent(event)


class GroupResize_3(QGraphicsRectItem, SerializableGraphicsItem):
    HANDLE_POSITIONS = ["tl", "tr", "bl", "br", "t", "b", "l", "r"]  # Positions des Handles

    def __init__(self, items=None):
        super().__init__(0, 0, 0, 0)  # Rect minimal initial

        print("Start init")

        self.setPen(QColor(0, 0, 0, 0))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(500)

        self._old_pos = None
        self._items = []  # Liste pour suivre les items
        self._old_geometry = None
        self._is_resizing = False
        self._selection_pen = QPen(QColor(0, 0, 0), 1, Qt.PenStyle.SolidLine)

        # Initialise les Handles (mais ne les affiche pas encore)
        self.handles = {}
        self._init_handles()

        if items:
            for item in items:
                self.addToGroup(item)

    def _init_handles(self):
        """Initialise les 8 Handles de redimensionnement"""
        for pos in self.HANDLE_POSITIONS:
            self.handles[pos] = Handle(self, pos)
            self.handles[pos].setVisible(False)  # Masqués par défaut

    def update_handles(self):
        """Met à jour la position des Handles"""
        if not self.scene():
            return

        rect = self.boundingRect()
        if rect.isEmpty():
            return

        # Coins
        self.handles["tl"].setPos(rect.topLeft())
        self.handles["tr"].setPos(rect.topRight())
        self.handles["bl"].setPos(rect.bottomLeft())
        self.handles["br"].setPos(rect.bottomRight())

        # Milieux
        center = rect.center()
        self.handles["t"].setPos(center.x(), rect.top())
        self.handles["b"].setPos(center.x(), rect.bottom())
        self.handles["l"].setPos(rect.left(), center.y())
        self.handles["r"].setPos(rect.right(), center.y())

    def show_handles(self, visible=True):
        """Affiche/masque tous les Handles"""
        for handle in self.handles.values():
            handle.setVisible(visible)

    def addToGroup(self, item):
        """Ajoute un item au groupe en conservant sa position visuelle"""
        # Stocke la position scène originale
        original_scene_pos = item.scenePos()

        # Ajoute l'item au groupe
        item.setParentItem(self)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        # Ajuste la position pour conserver l'emplacement visuel
        new_pos = item.mapFromScene(original_scene_pos)
        item.setPos(new_pos)

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
        self.update_handles()
        self.update()

    def boundingRect(self):
        """Retourne le rect du groupe"""
        return self.rect()

    def paint(self, painter, option, widget=None):
        """Dessine le contour quand sélectionné"""
        # Dessine d'abord les enfants normalement
        super().paint(painter, option, widget)

        # Puis dessine le contour si sélectionné
        if self.isSelected():
            painter.setPen(self._selection_pen)
            # Dessine un rect légèrement plus grand pour bien voir le contour
            contour_rect = self.boundingRect().adjusted(-1, -1, 1, 1)
            painter.drawRect(contour_rect)


    def itemChange(self, change, value):
        """Gère les changements d'état (sélection, etc.)"""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.show_handles(value)  # Affiche les Handles quand sélectionné
            self.update_handles()
        self.update()  # Force un rafraîchissement quand la sélection change
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        print("Groupe -> Press event")
        self._old_pos = self.pos()
        rect = self.rect()
        self._old_geometry = (self.pos().x(), self.pos().y(), rect.x(), rect.y(), self.rect().width(), self.rect().height())
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.updateGeometry()

    def mouseReleaseEvent(self, event):
        print("Groupe -> Release event")

        if self.pos() != self._old_pos:
            new_pos = self.pos()
            rect = self.rect()
            new_geometry = (new_pos.x(), new_pos.y(), rect.x(), rect.y(), rect.width(), rect.height())

            # Crée une commande pour l'historique
            from draw.HistoryManager import ModifyItemCommand
            cmd = ModifyItemCommand(
                self,
                self._old_geometry,  # Ancienne géométrie
                new_geometry,  # Nouvelle géométrie
                "move group"
            )
            self.scene().undo_stack.push(cmd)

        self._old_pos = None
        self._old_geometry = None
        super().mouseReleaseEvent(event)

    def resize(self, position: str, new_pos: QPointF):
        old_rect = self.rect()
        r = QRectF(old_rect)

        # Applique le redimensionnement du rectangle parent
        if position == "br":
            r.setBottomRight(new_pos)
        elif position == "bl":
            r.setBottomLeft(new_pos)
        elif position == "tr":
            r.setTopRight(new_pos)
        elif position == "tl":
            r.setTopLeft(new_pos)
        elif position == "t":
            r.setTop(new_pos.y())
        elif position == "b":
            r.setBottom(new_pos.y())
        elif position == "l":
            r.setLeft(new_pos.x())
        elif position == "r":
            r.setRight(new_pos.x())

        self.setRect(r.normalized())

        # Détermine le point fixe
        fixed_point = {
            "tl": old_rect.bottomRight(),
            "tr": old_rect.bottomLeft(),
            "bl": old_rect.topRight(),
            "br": old_rect.topLeft(),
            "t": QPointF(old_rect.center().x(), old_rect.bottom()),
            "b": QPointF(old_rect.center().x(), old_rect.top()),
            "l": QPointF(old_rect.right(), old_rect.center().y()),
            "r": QPointF(old_rect.left(), old_rect.center().y()),
        }.get(position, old_rect.center())

        # Facteurs d’échelle
        scale_x = r.width() / old_rect.width() if old_rect.width() > 0 else 1
        scale_y = r.height() / old_rect.height() if old_rect.height() > 0 else 1

        # Redimensionne les enfants
        for item in self._items:
            if isinstance(item, QGraphicsLineItem):
                # Recalcule les extrémités de la ligne
                line = item.line()
                new_line = QLineF(
                    (line.x1() - fixed_point.x()) * scale_x + fixed_point.x(),
                    (line.y1() - fixed_point.y()) * scale_y + fixed_point.y(),
                    (line.x2() - fixed_point.x()) * scale_x + fixed_point.x(),
                    (line.y2() - fixed_point.y()) * scale_y + fixed_point.y()
                )
                item.setLine(new_line)

            elif hasattr(item, "setRect") and hasattr(item, "rect"):  # Rectangle/Ellipse

                original_rect = item.rect()  # ✅ la vraie taille de l'item
                new_width = original_rect.width() * scale_x
                new_height = original_rect.height() * scale_y

                new_x = original_rect.x() * scale_x
                new_y = original_rect.y() * scale_y

                # On garde le coin (0,0) en repère local
                item.setRect(new_x, new_y, new_width, new_height)

                # Repositionne par rapport au point fixe
                pos = item.pos()
                new_x = (pos.x() - fixed_point.x()) * scale_x + fixed_point.x()
                new_y = (pos.y() - fixed_point.y()) * scale_y + fixed_point.y()
                item.setPos(new_x, new_y)

        self.update_handles()
        self._is_resizing = False
