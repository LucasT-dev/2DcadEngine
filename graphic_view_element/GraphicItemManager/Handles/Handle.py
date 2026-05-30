from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem

class Handle(QGraphicsEllipseItem):

    BASE_SIZE = 8  # taille de base en pixels écran

    def __init__(self, parent: QGraphicsItem, position: QPointF, role: str):
        super().__init__(-4, -4, 8, 8)  # Taille fixe pour le handle

        self.setParentItem(parent)
        self.role = role  # Ex: "top-left", "bottom-rigt" etc.
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setPen(QPen(QColor(0, 204, 204, 255)))
        self.setZValue(1000)  # Toujours au-dessus
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)
        self.setPos(position)  # Position initiale
        self.setVisible(False)  # Invisible par défaut



    def mousePressEvent(self, event):
        parent = self.parentItem()

        if parent and parent.isSelected():
            parent.handle_press(self.role, event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Calcule la nouvelle position en coordonnées locales de l'item parent
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.handle_moved(self.role, event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        parent = self.parentItem()
        if parent and parent.isSelected():
            parent.handle_released(self.role, event)
        super().mouseReleaseEvent(event)


    def update_size(self, zoom_level: float):
        """Redimensionne le handle selon le zoom de la vue."""
        if zoom_level <= 0:
            return

        MIN_HALF = 3.0  # taille minimum en pixels scène

        half = max((self.BASE_SIZE / zoom_level) / 1.5 , MIN_HALF)
        self.setRect(-half, -half, half * 2, half * 2)

        pen = self.pen()
        pen.setWidthF(max(3 / zoom_level, 1.0))  # épaisseur minimum à 1.0
        self.setPen(pen)
