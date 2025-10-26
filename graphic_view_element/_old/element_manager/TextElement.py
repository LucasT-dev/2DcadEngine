import uuid

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QColor, QFont, QTransform

from graphic_view_element._old.element_manager.GraphicElementBase import GraphicElementBase
from graphic_view_element._old.resizable_element.TextResizable import ResizableTextItem


class TextElement(GraphicElementBase):

    def create_graphics_item(self):
        rect = self._compute_rect(self.start, self.end)

        item = ResizableTextItem()
        item.setFont(self.style.get_font())
        item.setPlainText(self.style.get_text())
        item.setTextWidth(rect.width())
        item.setPos(rect.topLeft())
        item.setZValue(self.style.get_z_value())
        item.setDefaultTextColor(self.style.get_text_color())

        # 🔁 Correction d’orientation locale
        item.setTransformOriginPoint(0, 0)
        item.setTransform(QTransform().scale(1, -1))

        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        item.setData(self.style.get_key(), self.style.get_value())

        return item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    text: str = "Text",
                                    text_color: QColor = QColor(0, 0, 0),
                                    font: QFont = QFont("Arial", 14),
                                    text_width: float = None,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        rect = TextElement._compute_rect(first_point, second_point)

        item = QGraphicsTextItem()
        item.setFont(font)
        item.setPlainText(text)
        item.setTextWidth(text_width if text_width is not None else rect.width())
        item.setPos(rect.topLeft())
        item.setZValue(z_value)
        item.setFlags(flags)
        item.setDefaultTextColor(text_color)

        item.setData(key, value)

        return item

    @staticmethod
    def _compute_rect(p1: QPointF, p2: QPointF) -> QRectF:
        return QRectF(p1, p2).normalized()
