import sys

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

from src.cadengine.MainCad import MainCad
from src.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CircleElement import CircleElement
from src.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CirclePreview import CirclePreview
from src.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CircleResizable import CircleResizable
from src.cadengine.graphic_view_element.GraphicItemManager.EllipseElement.EllipseElement import EllipseElement
from src.cadengine.graphic_view_element.GraphicItemManager.EllipseElement.EllipseResizable import EllipseResizable
from src.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupElement import GroupElement
from src.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupPreview import GroupPreview
from src.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupResizable import GroupResizable
from src.cadengine.graphic_view_element.GraphicItemManager.LineElement.LineElement import LineElement
from src.cadengine.graphic_view_element.GraphicItemManager.LineElement.LinePreview import LinePreview
from src.cadengine.graphic_view_element.GraphicItemManager.LineElement.LineResizable import LineResizable
from src.cadengine.graphic_view_element.GraphicItemManager.EllipseElement.EllipsePreview import EllipsePreview
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapElement import PixmapElement
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapPreview import PixmapPreview
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapResizable import PixmapResizable
from src.cadengine.graphic_view_element.GraphicItemManager.RectangleElement.RectangleElement import RectangleElement
from src.cadengine.graphic_view_element.GraphicItemManager.RectangleElement.RectanglePreview import RectanglePreview
from src.cadengine.graphic_view_element.GraphicItemManager.RectangleElement.RectangleResizable import RectangleResizable
from src.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquareElement import SquareElement
from src.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquarePreview import SquarePreview
from src.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquareResizable import SquareResizable
from src.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextElement import TextElement
from src.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextPreview import TextPreview
from src.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextResizable import TextResizable


class MyWidget:
    def configure(self, maincad):
        """
        Reçoit une instance de MainCad,
        et configure la vue, la scène, les outils, etc.
        """
        view = maincad.g_get_view
        graphic_view = maincad.g_get_graphic_view
        scene = maincad.g_get_scene


        view.g_set_scale(1, -1)
        view.g_set_scene_rectangle(-20, -20, 700, 600)
        view.g_set_background_color("#5B5B5B")

        view.g_register_element(element_name="line", element_class=LineElement, preview_class=LinePreview,
                                           resizable_class=LineResizable)
        view.g_register_shortcut(name="line", key=Qt.Key.Key_L)
        view.g_register_cursor(name="line", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element(element_name="rect", element_class=RectangleElement, preview_class=RectanglePreview,
                                           resizable_class=RectangleResizable)
        view.g_register_shortcut(name="rect", key=Qt.Key.Key_R)
        view.g_register_cursor(name="rect", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element(element_name="ellipse", element_class=EllipseElement, preview_class=EllipsePreview,
                                           resizable_class=EllipseResizable)
        view.g_register_shortcut(name="ellipse", key=Qt.Key.Key_E)
        view.g_register_cursor(name="ellipse", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element(element_name="text", element_class=TextElement, preview_class=TextPreview,
                                           resizable_class=TextResizable)
        view.g_register_shortcut(name="text", key=Qt.Key.Key_T)
        view.g_register_cursor(name="text", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element(element_name="square", element_class=SquareElement, preview_class=SquarePreview,
                                           resizable_class=SquareResizable)
        view.g_register_shortcut(name="square", key=Qt.Key.Key_S)
        view.g_register_cursor(name="square", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element("circle", element_class=CircleElement, preview_class=CirclePreview,
                                resizable_class=CircleResizable)
        view.g_register_shortcut(name="circle", key=Qt.Key.Key_C)
        view.g_register_cursor(name="circle", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element("image", element_class=PixmapElement, preview_class=PixmapPreview,
                                resizable_class=PixmapResizable)
        view.g_register_shortcut(name="image", key=Qt.Key.Key_P)
        view.g_register_cursor(name="image", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element("group", element_class=GroupElement, preview_class=GroupPreview,
                                resizable_class=GroupResizable)
        view.g_register_shortcut(name="group", key=Qt.Key.Key_G)
        view.g_register_cursor(name="group", cursor=Qt.CursorShape.CrossCursor)


        view.g_add_item(name="line", history=True, first_point=QPointF(0, 0),
            second_point=QPointF(100, 100),
            border_color=QColor("blue"),
            border_width=5,
            border_style=Qt.PenStyle.SolidLine,
            z_value=100)

        view.g_add_item(name="rect", history=True, first_point=QPointF(50, 100),
                          second_point=QPointF(100, 150),
                          fill_color=QColor("white"),
                          border_color=QColor("green"),
                          border_width=5,
                          border_style=Qt.PenStyle.SolidLine,
                          z_value=100)

        view.g_add_item(name="ellipse", history=True, first_point=QPointF(150, 300),
                          second_point=QPointF(180, 200),
                          fill_color=QColor("white"),
                          border_color=QColor("blue"),
                          border_width=5,
                          border_style=Qt.PenStyle.SolidLine,
                          z_value=100)

        view.g_add_item(name="text", history=True, first_point=QPointF(150, 300),
                          second_point=QPointF(180, 250),
                          z_value=100)

        print("Moteur initialisé !")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainCad(configurator=MyWidget(), show_ruler=True)
    window.show()
    window.resize(500, 500)
    sys.exit(app.exec())
