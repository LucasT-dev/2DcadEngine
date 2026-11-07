import logging

import keyboard
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtWidgets import QGraphicsItem


from graphic_view_element.GraphicItemManager.BezierCubiqueLineElement.BezierCubeLineElement import BezierCubeLineElement
from graphic_view_element.GraphicItemManager.BezierCubiqueLineElement.BezierCubeLinePreview import BezierCubeLinePreview
from graphic_view_element.GraphicItemManager.BezierCubiqueLineElement.BezierCubeLineResizable import BezierCubeLineResizable
from graphic_view_element.GraphicItemManager.CircleElement.CircleElement import CircleElement
from graphic_view_element.GraphicItemManager.CircleElement.CirclePreview import CirclePreview
from graphic_view_element.GraphicItemManager.CircleElement.CircleResizable import CircleResizable
from graphic_view_element.GraphicItemManager.CurveLineElement.CurveLineElement import CurveLineElement
from graphic_view_element.GraphicItemManager.CurveLineElement.CurveLinePreview import CurveLinePreview
from graphic_view_element.GraphicItemManager.CurveLineElement.CurveLineResizable import CurveLineResizable
from graphic_view_element.GraphicItemManager.CustomGroupElement.CustomGroupElement import GroupElement
from graphic_view_element.GraphicItemManager.CustomGroupElement.CustomGroupPreview import GroupPreview
from graphic_view_element.GraphicItemManager.EllipseElement.EllipseElement import EllipseElement
from graphic_view_element.GraphicItemManager.EllipseElement.EllipsePreview import EllipsePreview
from graphic_view_element.GraphicItemManager.EllipseElement.EllipseResizable import EllipseResizable
from graphic_view_element.GraphicItemManager.GroupElement.GroupResizable import GroupResizable
from graphic_view_element.GraphicItemManager.LineElement.LineElement import LineElement
from graphic_view_element.GraphicItemManager.LineElement.LinePreview import LinePreview
from graphic_view_element.GraphicItemManager.LineElement.LineResizable import LineResizable
from graphic_view_element.GraphicItemManager.PathLineElement.PathLineResizable import PathLineResizable
from graphic_view_element.GraphicItemManager.PathLineElement.PathLineElement import PathLineElement
from graphic_view_element.GraphicItemManager.PathLineElement.PathLinePreview import PathLinePreview
from graphic_view_element.GraphicItemManager.PixmapElement.PixmapElement import PixmapElement
from graphic_view_element.GraphicItemManager.PixmapElement.PixmapPreview import PixmapPreview
from graphic_view_element.GraphicItemManager.PixmapElement.PixmapResizable import PixmapResizable
from graphic_view_element.GraphicItemManager.RectangleElement.RectangleElement import RectangleElement
from graphic_view_element.GraphicItemManager.RectangleElement.RectanglePreview import RectanglePreview
from graphic_view_element.GraphicItemManager.RectangleElement.RectangleResizable import RectangleResizable
from graphic_view_element.GraphicItemManager.SVGElement.ImageSVGElement import ImageSVGElement
from graphic_view_element.GraphicItemManager.SVGElement.ImageSVGPreview import ImageSVGPreview
from graphic_view_element.GraphicItemManager.SVGElement.ImageSVGResizable import ImageSVGResizable
from graphic_view_element.GraphicItemManager.SquareElement.SquareElement import SquareElement
from graphic_view_element.GraphicItemManager.SquareElement.SquarePreview import SquarePreview
from graphic_view_element.GraphicItemManager.SquareElement.SquareResizable import SquareResizable
from graphic_view_element.GraphicItemManager.TextElement.TextElement import TextElement
from graphic_view_element.GraphicItemManager.TextElement.TextPreview import TextPreview
from graphic_view_element.GraphicItemManager.TextElement.TextResizable import TextResizable

log = logging.getLogger(__name__)

class GraphicWindowWidget:

    def init(self, maincad):


        # Inversion du repere
        maincad.g_get_view.g_set_scale(1, -1)
        maincad.g_get_view.g_set_scene_rectangle(-20, -20, 1500, 1500)
        maincad.g_get_view.g_set_background_color("#000000")

        maincad.g_get_view.g_set_unit("mm")
        maincad.g_get_view.camera.zoom_to(1.0)



        ##view.setRenderHint(QPainter.SmoothPixmapTransform)

        # Zone de dessin

        maincad.g_get_graphic_view.h_ruler.update_style(
            background="#FFFFFF",
            tick=QColor(0, 255, 0, 150),
            text="X",
            font_family="Helvetica",
            font_size=7
        )

        maincad.g_get_graphic_view.v_ruler.update_style(
            background="#123456",
            tick=QColor(255, 0, 0, 150),
            text="Y",
            font_family="Helvetica",
            font_size=7
        )

        maincad.g_get_view.g_set_render_hit(render=QPainter.RenderHint.Antialiasing)
        maincad.g_get_view.g_set_render_hit(render=QPainter.RenderHint.SmoothPixmapTransform)

        #maincad.g_get_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        #maincad.g_get_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        #maincad.g_get_view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        maincad.g_get_view.camera.set_pan_enabled(True)
        maincad.g_get_view.camera.set_zoom_enabled(True)

        # Défini la position de la grille par rapport au repere
        maincad.g_get_view.grid.set_origin_position("top-left")  # ou "center", "top-left", etc.



        maincad.g_get_view.zoom_changed.connect(lambda state: self.wheel_move(maincad))
        maincad.g_get_view.selection_changed.connect(lambda selection: self.on_selection_changed(selection))
        maincad.g_get_view.mouse_tracker.mouseMoved.connect(lambda scene: self.mousse_move(scene))
        maincad.g_get_view.key_press_event.connect(lambda key: self.key_press_event(maincad, key))


        maincad.g_get_view.g_register_element(element_name="line", element_class=LineElement, preview_class=LinePreview,
                                resizable_class=LineResizable)
        maincad.g_get_view.g_register_shortcut(name="line", key=Qt.Key.Key_L)
        maincad.g_get_view.g_register_cursor(name="line", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element(element_name="rectangle", element_class=RectangleElement, preview_class=RectanglePreview,
                                resizable_class=RectangleResizable)
        maincad.g_get_view.g_register_shortcut(name="rectangle", key=Qt.Key.Key_R)
        maincad.g_get_view.g_register_cursor(name="rectangle", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element(element_name="square", element_class=SquareElement,
                                              preview_class=SquarePreview,
                                              resizable_class=SquareResizable)
        maincad.g_get_view.g_register_shortcut(name="square", key=Qt.Key.Key_S)
        maincad.g_get_view.g_register_cursor(name="square", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element(element_name="circle", element_class=CircleElement,
                                              preview_class=CirclePreview,
                                              resizable_class=CircleResizable)
        maincad.g_get_view.g_register_shortcut(name="circle", key=Qt.Key.Key_C)
        maincad.g_get_view.g_register_cursor(name="circle", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element(element_name="ellipse", element_class=EllipseElement,
                                              preview_class=EllipsePreview,
                                              resizable_class=EllipseResizable)
        maincad.g_get_view.g_register_shortcut(name="ellipse", key=Qt.Key.Key_E)
        maincad.g_get_view.g_register_cursor(name="ellipse", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("image", element_class=PixmapElement, preview_class=PixmapPreview,
                                resizable_class=PixmapResizable)
        maincad.g_get_view.g_register_shortcut(name="image", key=Qt.Key.Key_P)
        maincad.g_get_view.g_register_cursor(name="image", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("text", element_class=TextElement, preview_class=TextPreview,
                                              resizable_class=TextResizable)
        maincad.g_get_view.g_register_shortcut(name="text", key=Qt.Key.Key_T)
        maincad.g_get_view.g_register_cursor(name="text", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("path line", element_class=PathLineElement, preview_class=PathLinePreview,
                                              resizable_class=PathLineResizable)
        maincad.g_get_view.g_register_shortcut(name="path line", key=Qt.Key.Key_M)
        maincad.g_get_view.g_register_cursor(name="path line", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("curve", element_class=CurveLineElement, preview_class=CurveLinePreview,
                                              resizable_class=CurveLineResizable)
        maincad.g_get_view.g_register_shortcut(name="curve", key=Qt.Key.Key_I)
        maincad.g_get_view.g_register_cursor(name="curve", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("bezier cubic line", element_class=BezierCubeLineElement,
                                              preview_class=BezierCubeLinePreview,
                                              resizable_class=BezierCubeLineResizable)
        maincad.g_get_view.g_register_shortcut(name="bezier cubic line", key=Qt.Key.Key_H)
        maincad.g_get_view.g_register_cursor(name="bezier cubic line", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("svg", element_class=ImageSVGElement, preview_class=ImageSVGPreview,
                                              resizable_class=ImageSVGResizable)
        maincad.g_get_view.g_register_cursor(name="svg", cursor=Qt.CursorShape.CrossCursor)

        maincad.g_get_view.g_register_element("group", element_class=GroupElement, preview_class=GroupPreview,
                                              resizable_class=GroupResizable)
        maincad.g_get_view.g_register_cursor(name="group", cursor=Qt.CursorShape.CrossCursor)


        maincad.g_get_view.g_set_default_text("Text")
        maincad.g_get_view.g_set_default_text_color(QColor(255, 255, 255))
        maincad.g_get_view.g_set_default_border_color(QColor(255, 255, 255))


        # Création des axes X et Y
        maincad.g_get_view.g_add_item(name="line", history=True,
                                    first_point=QPointF(-10, 0),
                                    second_point=QPointF(2000, 0),
                                    border_color=QColor(0, 255, 0, 255),
                                    border_width=1,
                                    border_style=Qt.PenStyle.SolidLine,
                                    z_value=100,
                                    key=50,
                                    value="x-axis",
                                    flags=QGraphicsItem.GraphicsItemFlag(0)
        )
        maincad.g_get_view.g_add_item(name="line", history=True,
                                    first_point=QPointF(0, 2000),
                                    second_point=QPointF(0, -10),
                                    border_color=QColor(255, 0, 0, 255),
                                    border_width=1,
                                    border_style=Qt.PenStyle.SolidLine,
                                    z_value=100,
                                    key=50,
                                    value="y-axis",
                                    flags=QGraphicsItem.GraphicsItemFlag(0)
        )

        maincad.g_get_view.g_add_text_annotation("zoom", f"<b>Zoom :</b> 100 %", 10, 10, font=QFont("Arial", 8),
                                              style=None)

        maincad.g_get_view.g_set_shortcut_undo_action()
        maincad.g_get_view.g_set_shortcut_redo_action()
        maincad.g_get_view.g_set_shortcut_delete_item()

        keyboard.add_hotkey('escape', lambda: self.escape(maincad))




    def escape(self, maincad):
        maincad.g_get_view.g_set_tool("mousse")
        maincad.g_get_view.g_set_cursor(Qt.CursorShape.ArrowCursor)

    def wheel_move(self, maincad):
        var = int(maincad.g_get_view.camera.get_zoom_percent())

        maincad.g_get_view.annotation_manager.update_text("zoom", f"<b>Zoom :</b> {var} %")

    def on_selection_changed(self, items: list[QGraphicsItem]):
        """Gère le changement de sélection et émet le signal personnalisé."""

    def mousse_move(self, _scene):
        pass


    def group_function(self, maincad):
        maincad.g_get_view.g_group_selected_items()

    def ungroup_function(self, maincad):
        maincad.g_get_view.g_ungroup_selected_items()

    def key_press_event(self, maincad, key):
        if key == Qt.Key.Key_G:
            self.group_function(maincad)
        if key == Qt.Key.Key_U:
            self.ungroup_function(maincad)


