from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsLineItem

from graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject


class LinePreview(PreviewObject):

    def create_preview_item(self, start: QPointF, end: QPointF):

        self._graphics_item = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
        self._graphics_item.setPen(self.get_style().get_pen())

    def update_item(self, start, end):

        if self._graphics_item is not None:
            self._graphics_item.setLine(start.x(), start.y(), end.x(), end.y())

            self._graphics_item.show()
            self._graphics_item.update()

