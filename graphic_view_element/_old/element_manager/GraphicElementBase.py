from abc import ABC, abstractmethod


class GraphicElementBase(ABC):

    def __init__(self, start, end, style):
        self.start = start
        self.end = end
        self.style = style

    @abstractmethod
    def create_graphics_item(self):
        """Crée le QGraphicsItem à afficher dans la scène"""
        pass