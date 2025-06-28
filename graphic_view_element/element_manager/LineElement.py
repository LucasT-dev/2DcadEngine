from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui import QPen, QColor

from graphic_view_element.element_manager.GraphicElementBase import GraphicElementBase


class LineElement(GraphicElementBase):
    def create_graphics_item(self):
        pen = QPen(QColor(self.style.get_border_color()))
        pen.setWidth(self.style.get_border_width())
        pen.setStyle(self.style.get_border_style())

        item = QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
        item.setPen(pen)
        item.setZValue(0)
        return item