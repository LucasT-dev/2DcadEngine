from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsPathItem

from libs.cadengine.graphic_view_element.GraphicItemManager.CurveLineElement import CurveLineResizable
from libs.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import MultiPointPreviewObject


class BezierCubeLinePreview(MultiPointPreviewObject):

    def create_preview_item(self, start: QPointF, end: QPointF):
        self._points = [start]
        self._graphics_item = QGraphicsPathItem()
        self._graphics_item.setPen(self.get_style().get_pen())
        self._rebuild_path(end)

    def update_item(self, start: QPointF, end: QPointF):
        if self._graphics_item is None or not self._points:
            return
        self._rebuild_path(end)

    def _rebuild_path(self, live_point: QPointF):
        # Le point volant (souris) est inclus temporairement pour l'aperçu,
        # sans être ajouté définitivement à self._points.
        preview_points = self._points + [live_point]
        path = CurveLineResizable.build_smooth_path(preview_points)

        self._graphics_item.setPath(path)
        self._graphics_item.show()
        self._graphics_item.update()