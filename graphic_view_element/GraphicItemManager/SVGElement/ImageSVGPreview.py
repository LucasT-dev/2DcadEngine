from pathlib import Path

from PyQt6.QtGui import QTransform, QPolygonF
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtCore import QRectF, QPointF

from libs.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject

current_dir = Path(__file__).parent
image_path = str(current_dir.parents[2] / "image" / "image_icon.svg")

class ImageSVGPreview(PreviewObject):

    def create_preview_item(self, start, end):
        svg_item = QGraphicsSvgItem(image_path)

        self._graphics_item = svg_item

        self._update_transform(start, end)

    def update_item(self, start, end):
        self._update_transform(start, end)

    def _update_transform(self, start: QPointF, end: QPointF):
        if self._graphics_item is None:
            return

        target_rect = QRectF(start, end).normalized()

        native_rect = QRectF(self._graphics_item.boundingRect())

        if native_rect.width() < 1e-6 or native_rect.height() < 1e-6:
            return
        if target_rect.width() < 1e-6 or target_rect.height() < 1e-6:
            return

        scale_x = target_rect.width() / native_rect.width()
        scale_y = target_rect.height() / native_rect.height()

        dx = target_rect.x() - native_rect.x() * scale_x
        dy = target_rect.y() + target_rect.height() + native_rect.y() * scale_y

        transform = QTransform(scale_x, 0, 0, -scale_y, dx, dy)

        self._graphics_item.setTransform(transform)
        self._graphics_item.setPos(0, 0)