from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsTextItem

from graphic_view_element.preview_manager.PreviewShape import PreviewShape


class TextPreview(PreviewShape):

    def create_preview_item(self, start: QPointF, end: QPointF):

        self.graphics_item = QGraphicsTextItem()
        self.graphics_item.setFont(self.font)
        self.graphics_item.setPlainText(self.text)
        self.graphics_item.setTextWidth(self.text_width)
        self.graphics_item.setPos(start)
        self.graphics_item.setDefaultTextColor(self.fill_color)

        # 🔁 Correction de l’orientation du texte
        self.graphics_item.setTransformOriginPoint(0, 0)
        self.graphics_item.setTransform(QTransform().scale(1, -1))

        #self.graphics_item.setZValue(self.style.get_z_value())

    def update_item(self, start: QPointF, end: QPointF):
        if not self.graphics_item:
            return

        self.graphics_item.setTextWidth(self.text_width)
        self.graphics_item.setPos(end)

    def create_item(self, start: QPointF, end: QPointF):
        pass
