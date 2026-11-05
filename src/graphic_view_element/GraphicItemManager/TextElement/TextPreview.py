from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsTextItem

from graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject


class TextPreview(PreviewObject):

    def create_preview_item(self, start: QPointF, end: QPointF):

        self._graphics_item = QGraphicsTextItem()
        self._graphics_item.setFont(self.get_style().get_font())
        self._graphics_item.setPlainText(self.get_style().get_text())
        self._graphics_item.setTextWidth(self.get_style().get_text_width())
        self._graphics_item.setPos(start)
        self._graphics_item.setDefaultTextColor(self.get_style().get_fill_color())

        # 🔁 Correction de l’orientation du texte
        self._graphics_item.setTransformOriginPoint(0, 0)
        self._graphics_item.setTransform(QTransform().scale(1, -1))

        #self.graphics_item.setZValue(self.style.get_z_value())

    def update_item(self, start: QPointF, end: QPointF):
        if not self._graphics_item:
            return

        self._graphics_item.setTextWidth(self.get_style().get_text_width())
        self._graphics_item.setPos(end)

    def create_item(self, start: QPointF, end: QPointF):
        pass