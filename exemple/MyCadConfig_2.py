import sys

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

from MainCad import MainCad

from graphic_view_element.GraphicItemManager.LineElement.LineElement import LineElement
from graphic_view_element.GraphicItemManager.LineElement.LinePreview import LinePreview
from graphic_view_element.GraphicItemManager.LineElement.LineSerialize import LineSerialize
from graphic_view_element.GraphicItemManager.EllipseElement.EllipseElement import EllipseElement
from graphic_view_element.GraphicItemManager.EllipseElement.EllipsePreview import EllipsePreview
from graphic_view_element.GraphicItemManager.EllipseElement.EllipseSerialize import EllipseSerialize
from graphic_view_element.GraphicItemManager.RectangleElement.RectangleElement import RectangleElement
from graphic_view_element.GraphicItemManager.RectangleElement.RectanglePreview import RectanglePreview
from graphic_view_element.GraphicItemManager.RectangleElement.RectangleSerialize import RectangleSerialise
from graphic_view_element.GraphicItemManager.TextElement.TextElement import TextElement
from graphic_view_element.GraphicItemManager.TextElement.TextPreview import TextPreview
from graphic_view_element.GraphicItemManager.TextElement.TextSerialize import TextSerialise


class MyWidget:
    def configure(self, maincad):
        """
        Reçoit une instance de MainCad,
        et configure la vue, la scène, les outils, etc.
        """
        view = maincad.g_get_view
        graphic_view = maincad.g_get_graphic_view
        scene = maincad.g_get_scene

        # Exemple minimal :
        view.g_scale(1, -1)
        view.g_set_scene_rectangle(-20, -20, 700, 600)
        view.g_set_background_color("#5B5B5B")

        view.g_register_element("line", element_class=LineElement,
                                serialisation_class=LineSerialize(),
                                preview_class=LinePreview)
        view.g_register_shortcut(name="line", key=Qt.Key.Key_L)
        view.g_register_cursor(name="line", cursor=Qt.CursorShape.CrossCursor)

        view.g_register_element("rect", element_class=RectangleElement,
                                serialisation_class=RectangleSerialise(),
                                preview_class=RectanglePreview)
        view.g_register_shortcut(name="rect", key=Qt.Key.Key_R)

        view.g_register_element("ellipse", element_class=EllipseElement,
                                serialisation_class=EllipseSerialize(),
                                preview_class=EllipsePreview)
        view.g_register_shortcut(name="ellipse", key=Qt.Key.Key_E)

        view.g_register_element("text", element_class=TextElement,
                                serialisation_class=TextSerialise(),
                                preview_class=TextPreview)
        view.g_register_shortcut(name="text", key=Qt.Key.Key_T)


        view.g_add_item(name="line", first_point=QPointF(0, 0),
            second_point=QPointF(100, 100),
            border_color=QColor("blue"),
            border_width=5,
            border_style=Qt.PenStyle.SolidLine,
            z_value=100)

        view.g_add_item(name="rect", first_point=QPointF(50, 100),
                          second_point=QPointF(100, 150),
                          fill_color=QColor("white"),
                          border_color=QColor("green"),
                          border_width=5,
                          border_style=Qt.PenStyle.SolidLine,
                          z_value=100)

        view.g_add_item(name="ellipse", first_point=QPointF(150, 300),
                          second_point=QPointF(180, 200),
                          fill_color=QColor("white"),
                          border_color=QColor("blue"),
                          border_width=5,
                          border_style=Qt.PenStyle.SolidLine,
                          z_value=100)

        view.g_add_item(name="text", first_point=QPointF(150, 300),
                          second_point=QPointF(180, 250),
                          z_value=100)

        print("Moteur initialisé !")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainCad(configurator=MyWidget(), show_ruler=True)
    window.show()
    window.resize(500, 500)
    sys.exit(app.exec())
