from abc import ABC, abstractmethod
from PyQt6.QtCore import QPointF

from graphic_view_element.style.StyleElement import StyleElement


class PreviewShape(ABC):

    def __init__(self, style: StyleElement):

        self.fill_color = style.get_fill_color()
        self.width = style.get_border_width()
        self.border_color = style.get_border_color()
        self.border_style = style.get_border_style()

        self.pen = style.get_pen()
        self.brush = style.get_brush()

        self.font = style.get_font()
        self.text = style.get_text()
        self.text_color = style.get_text_color()

        self.text_width = style.get_text_width()

        self.graphics_item = None



    @abstractmethod
    def create_preview_item(self, start: QPointF, end: QPointF):
        pass

    @abstractmethod
    def update_item(self, start: QPointF, end: QPointF):
        pass

    def get_item(self):
        return self.graphics_item

