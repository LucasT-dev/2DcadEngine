from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtCore import QRectF

from graphic_view_element.preview_manager.PreviewShape import PreviewShape


class RectanglePreview(PreviewShape):

    def create_preview_item(self, start, end):

        rect = QRectF(start, end).normalized()
        self.graphics_item = QGraphicsRectItem(rect)
        self.graphics_item.setPen(self.pen)
        self.graphics_item.setBrush(self.brush)

    def update_item(self, start, end):
        rect = QRectF(start, end).normalized()
        self.graphics_item.setRect(rect)
