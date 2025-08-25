import os
import uuid
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtWidgets import QGraphicsItem

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element.resizable_element.PixmapResizable import ResizablePixmapItem


class PixmapElement(GraphicElementBase):

    def create_graphics_item(self):

        image_path = "C:\Bureau\\free-nature-images.jpg"
        if not os.path.exists(image_path):
            print("⚠ Image par défaut introuvable, utilisez un chemin valide.")
            return

        pixmap = QPixmap(image_path)

        # Taille de base = taille définie par start/end
        target_rect = QRectF(self.start, self.end).normalized()

        pixmap = pixmap.transformed(QTransform().scale(1, -1))
        pixmap = pixmap.scaled(target_rect.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio)

        item = ResizablePixmapItem(pixmap)
        item.setPos(target_rect.topLeft())
        item.setZValue(self.style.get_z_value())

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.style.get_key(), self.style.get_value())

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    image_path: str,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        pixmap = QPixmap(image_path)
        # Taille de base = taille définie par start/end
        target_rect = QRectF(first_point, second_point).normalized()

        pixmap = pixmap.transformed(QTransform().scale(1, -1))
        pixmap = pixmap.scaled(target_rect.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio)

        item = ResizablePixmapItem(pixmap)
        item.setPos(target_rect.topLeft())
        item.setZValue(z_value)

        item.setFlags(flags)
        item.setData(key, value)

        return item