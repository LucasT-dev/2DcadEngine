
from PyQt6.QtWidgets import QGraphicsLineItem

from graphic_view_element._old.preview_manager.PreviewShape import PreviewShape


class LinePreview(PreviewShape):

    def create_preview_item(self, start, end):

        self.graphics_item = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
        self.graphics_item.setPen(self.pen)

    def update_item(self, start, end):
        self.graphics_item.setLine(start.x(), start.y(), end.x(), end.y())