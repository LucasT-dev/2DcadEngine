from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem

from graphic_view_element._old.preview_manager.PreviewShape import PreviewShape


class CirclePreview(PreviewShape):

    def create_preview_item(self, start, end):

        circle = QRectF(start, end).normalized()
        self.graphics_item = QGraphicsEllipseItem(circle)
        self.graphics_item.setPen(self.pen)
        self.graphics_item.setBrush(self.brush)

    def update_item(self, start, end):
        circle = QRectF(start, end).normalized()
        self.graphics_item.setRect(circle)

    def create_item(self, start: QPointF, end: QPointF):
        pass