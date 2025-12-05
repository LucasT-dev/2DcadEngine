import os
import uuid
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtWidgets import QGraphicsItem

from src.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import ElementObject
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapResizable import PixmapResizable


class PixmapElement(ElementObject):

    def create_graphics_item(self, first_point: QPointF, second_point: QPointF):

        image_path = "C:\Bureau\\free-nature-images.jpg"
        if not os.path.exists(image_path):
            print("⚠ Image par défaut introuvable, utilisez un chemin valide.")
            return

        pixmap = QPixmap(image_path)

        # Taille de base = taille définie par start/end
        target_rect = QRectF(first_point, second_point).normalized()

        pixmap = pixmap.transformed(QTransform().scale(1, -1))
        pixmap = pixmap.scaled(target_rect.size().toSize(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

        item = PixmapResizable(pixmap)

        item.setPos(target_rect.topLeft())
        item.setZValue(self.get_style().get_z_value())

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        item.setData(self.get_style().get_key(), self.get_style().get_value())

        item.setAcceptHoverEvents(True)

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    image_source,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    transform: QTransform = QTransform(),
                                    visibility: bool = True,
                                    scale: float = 1.0,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        pixmap = QPixmap(image_source)

        target_rect = QRectF(first_point, second_point).normalized()

        pixmap = pixmap.transformed(transform)
        pixmap = pixmap.scaled(target_rect.size().toSize(), Qt.AspectRatioMode.IgnoreAspectRatio)

        item = PixmapResizable(pixmap)
        item.setPos(target_rect.topLeft())
        item.setZValue(z_value)

        item.setFlags(flags)
        item.setData(key, value)

        return item