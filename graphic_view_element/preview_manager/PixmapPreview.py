from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem
from PyQt6.QtCore import QRectF, Qt

from graphic_view_element.preview_manager.PreviewShape import PreviewShape

pixmap_path = "C:\Bureau\\free-nature-images.jpg"

class PixmapPreview(PreviewShape):

    def create_preview_item(self, start, end):
        rect = QRectF(start, end).normalized()

        pixmap = QPixmap(pixmap_path)
        pixmap = pixmap.transformed(QTransform().scale(1, -1))

        scaled_pixmap = pixmap.scaled(
            rect.size().toSize(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.graphics_item = QGraphicsPixmapItem(scaled_pixmap)
        self.graphics_item.setOffset(rect.topLeft())

    def update_item(self, start, end):
        rect = QRectF(start, end).normalized()

        pixmap = QPixmap(pixmap_path)
        pixmap = pixmap.transformed(QTransform().scale(1, -1))

        scaled_pixmap = pixmap.scaled(
            rect.size().toSize(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.graphics_item.setPixmap(scaled_pixmap)
        self.graphics_item.setOffset(rect.topLeft())
