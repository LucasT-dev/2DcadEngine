from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem
from PyQt6.QtCore import QRectF, Qt

from graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject

pixmap_path = "C:\Bureau\\free-nature-images.jpg"

class PixmapPreview(PreviewObject):

    def create_preview_item(self, start, end):
        rect = QRectF(start, end).normalized()

        pixmap = QPixmap(pixmap_path)
        pixmap = pixmap.transformed(QTransform().scale(1, -1))

        scaled_pixmap = pixmap.scaled(
            rect.size().toSize(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self._graphics_item = QGraphicsPixmapItem(scaled_pixmap)
        self._graphics_item.setOffset(rect.topLeft())

    def update_item(self, start, end):

        rect = QRectF(start, end).normalized()

        pixmap = QPixmap(pixmap_path)
        pixmap = pixmap.transformed(QTransform().scale(1, -1))

        scaled_pixmap = pixmap.scaled(
            rect.size().toSize(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self._graphics_item.setPixmap(scaled_pixmap)
        self._graphics_item.setOffset(rect.topLeft())
