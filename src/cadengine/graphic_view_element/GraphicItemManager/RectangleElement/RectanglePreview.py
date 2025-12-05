from PyQt6.QtCore import QRectF
from PyQt6.QtWidgets import QGraphicsRectItem

from src.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject


class RectanglePreview(PreviewObject):

    def create_preview_item(self, start, end):

        rect = QRectF(start, end).normalized()
        self._graphics_item = QGraphicsRectItem(rect)
        self._graphics_item.setPen(self.get_style().get_pen())
        self._graphics_item.setBrush(self.get_style().get_brush())

    def update_item(self, start, end):
        rect = QRectF(start, end).normalized()
        self._graphics_item.setRect(rect)