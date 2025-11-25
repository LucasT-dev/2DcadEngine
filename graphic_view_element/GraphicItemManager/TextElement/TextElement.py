import uuid

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform, QColor, QFont
from PyQt6.QtWidgets import QGraphicsItem

from graphic_view_element.GraphicItemManager.GraphicElementObject import ElementObject
from graphic_view_element.GraphicItemManager.TextElement.TextResizable import TextResizable


class TextElement(ElementObject):

    def create_graphics_item(self, first_point: QPointF, second_point: QPointF):

        rect = self._compute_rect(first_point, second_point)

        item = TextResizable()
        item.setFont(self.get_style().get_font())
        item.setPlainText(self.get_style().get_text())
        item.setTextWidth(rect.width())
        item.setPos(rect.topLeft())
        item.setZValue(self.get_style().get_z_value())
        item.setDefaultTextColor(self.get_style().get_text_color())

        # 🔁 Correction d’orientation locale
        item.setTransformOriginPoint(0, 0)
        item.setTransform(QTransform().scale(1, -1))

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.get_style().get_key(), self.get_style().get_value())

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    text: str = "Text",
                                    text_color: QColor = QColor(0, 0, 0),
                                    font: QFont = QFont("Arial", 14),
                                    text_width: float = 1,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    transform: QTransform = QTransform(),
                                    visibility: bool = True,
                                    scale: float = 1.0,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        rect = TextElement._compute_rect(first_point, second_point)

        item = TextResizable()
        item.setFont(font)
        item.setPlainText(text)
        item.setTextWidth(text_width if text_width is not None else rect.width())
        item.setPos(rect.topLeft())
        item.setZValue(z_value)
        item.setFlags(flags)
        item.setDefaultTextColor(text_color)
        item.setTransform(transform)

        item.setData(key, value)

        return item

    @staticmethod
    def _compute_rect(p1: QPointF, p2: QPointF) -> QRectF:
        return QRectF(p1, p2).normalized()