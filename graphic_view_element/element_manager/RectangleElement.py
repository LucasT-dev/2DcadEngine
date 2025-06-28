from PyQt6.QtCore import QRectF
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QColor, QBrush

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class RectangleElement(GraphicElementBase):
    def create_graphics_item(self):
        rect = QRectF(self.start, self.end).normalized()

        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        brush = QBrush(QColor(self.style.get_fill_color()))

        item = QGraphicsRectItem(rect)
        item.setPen(pen)
        item.setBrush(brush)
        item.setZValue(0)
        return item