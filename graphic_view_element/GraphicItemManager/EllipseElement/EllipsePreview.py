from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem

from graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject


class EllipsePreview(PreviewObject):

    def create_preview_item(self, start: QPointF, end: QPointF):

        circle = QRectF(start, end).normalized()
        self._graphics_item = QGraphicsEllipseItem(circle)
        self._graphics_item.setPen(self.get_style().get_pen())
        self._graphics_item.setBrush(self.get_style().get_brush())

    def update_item(self, start: QPointF, end: QPointF):
        circle = QRectF(start, end).normalized()
        self._graphics_item.setRect(circle)
