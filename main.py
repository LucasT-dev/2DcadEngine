import sys

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene

from graphic_view_element.element_manager.CircleCenterElement import CircleCenterElement
from graphic_view_element.element_manager.CircleElement import CircleElement
from graphic_view_element.element_manager.LineElement import LineElement
from graphic_view_element.element_manager.RectangleCenterElement import RectangleCenterElement
from graphic_view_element.element_manager.RectangleElement import RectangleElement
from graphic_view_element.element_manager.SquareCenterElement import SquareCenterElement
from graphic_view_element.element_manager.SquareElement import SquareElement
from graphic_view_element.preview_manager.CircleCenterPreview import CircleCenterPreview
from graphic_view_element.preview_manager.CirclePreview import CirclePreview
from graphic_view_element.preview_manager.LinePreview import LinePreview
from graphic_view_element.preview_manager.RectangleCenterPreview import RectangleCenterPreview
from graphic_view_element.preview_manager.RectanglePreview import RectanglePreview
from graphic_view_element.preview_manager.SquareCenterPreview import SquareCenterPreview
from graphic_view_element.preview_manager.SquarePreview import SquarePreview
from scene.GraphicView import GraphicViewContainer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.mouse_label = None
        self.scene = QGraphicsScene()

        # Vue avec règles en bas et à droite
        self.graphic_view = GraphicViewContainer(
            self.scene,
            show_ruler=True,
            ruler_positions={"horizontal": "bottom", "vertical": "left"}
        )

        self.initUI()

    def initUI(self):
        # Configuration de la fenêtre principale
        self.setWindowTitle("Moteur de dessin 2D")
        #self.setGeometry(00, 00, 400, 400) # taille de la fenetre


        self.setCentralWidget(self.graphic_view)

        # Initialisation du moteur de dessin
        self.initEngine()



    def initEngine(self):
        #self.graphic_view = GraphicView(self.scene, show_ruler=True)

        # Inversion du repere
        self.graphic_view.view.g_scale(1, -1)
        self.graphic_view.view.g_set_scene_rectangle(-20, -20, 700, 600)

         # Zone de dessin

        self.graphic_view.view.g_set_render_hit(QPainter.RenderHint.Antialiasing)
        self.graphic_view.view.g_set_background_color("#5B5B5B")

        # Défini le centre de la scene
        #self.graphic_view.view.g_center_camera_on(0, 0)


        self.graphic_view.view.camera.set_pan_enabled(True)
        self.graphic_view.view.camera.set_zoom_enabled(True)

        # Défini la position de la grille par rapport au repere
        self.graphic_view.view.grid.set_origin_position("top-left")  # ou "center", "top-left", etc.


        # Configurer la grille selon vos besoins #03fcbe
        #self.graphic_view.view.grid.draw_grid(QColor(3, 252, 190, 100), width=0, interval=10)
        #self.graphic_view.view.grid.draw_grid(QColor(250, 250, 250, 100), width=0, interval=50)

        # Ligne axe X/Y
        self.graphic_view.view.grid.draw_line(color=QColor(0, 255, 0, 150), width=1,
                                    start_x=-10, start_y=0,
                                    end_x=self.graphic_view.view.width(), end_y=0)

        self.graphic_view.view.grid.draw_line(color=QColor(255, 0, 0, 150), width=1,
                                    start_x=0, start_y=self.graphic_view.view.height(),
                                    end_x=0, end_y=-10)


        # Mise à jour du style des règles
        self.graphic_view.h_ruler.update_style(
            background="#2D2D2D",
            tick=QColor(0, 255, 0, 150),
            text="#FFFFFF",
            font_family="Helvetica",
            font_size=7
        )


        # Mise à jour du style des règles
        self.graphic_view.v_ruler.update_style(
            background="#2D2D2D",
            tick=QColor(255, 0, 0, 150),
            text="#FFFFFF",
            font_family="Helvetica",
            font_size=7
        )


        self.graphic_view.view.grid.draw_X_axis(
            color=QColor(0, 255, 0),  # Axes verts
            width=2,  # Épaisseur de 3 pixels
            name="X",  # Nom personnalisé
            axis_length=30,  # Axes de 300 pixels
            x_label="X"  # Label personnalisé pour X

        )

        self.graphic_view.view.grid.draw_Y_axis(
            color=QColor(255, 0, 0),  # Axes verts
            width=2,  # Épaisseur de 3 pixels
            name="Y",  # Nom personnalisé
            axis_length=30,  # Axes de 300 pixels
            y_label="Y",  # Label personnalisé pour Y
            text_rotate=180
        )

        #self.graphic_view.view.grid.move_coordinate_system("Y", 100, 100, -20, -40)
        #self.graphic_view.view.grid.move_coordinate_system("X", 100, 100, 20, 0)

        # Dessiner des points noirs de rayon 4 pixels espacés de 50 pixels
        """self.graphic_view.view.grid.draw_point(
            color=QColor("#000000"),
            radius=2,
            interval_x=50,
            interval_y=50,
            name="points"
        )"""


        self.graphic_view.view.camera.set_zoom_limits(0.8, 10.0)
        self.graphic_view.view.camera.set_zoom_factor(1.2) # 1.2
        self.graphic_view.view.camera.set_zoom_to_cursor(True)
        self.graphic_view.view.camera.zoom_to(1.0)

        self.graphic_view.view.g_set_unit("mm")

        #self.graphic_view.view.camera.set_zoom_percent(100)

        # 1. Place une ligne de 100 mm dans la scène
        self.graphic_view.view.scene().addLine(0, 0, 100, 0)

        # 2. Calibre automatiquement en fonction du rendu visuel
        dpi = self.graphic_view.view.camera.auto_calibrate_dpi_from_scene(mm_in_scene=100)
        print(f"DPI estimé automatiquement : {dpi:.2f}")

        # 3. Applique un zoom à 100% réel
        self.graphic_view.view.camera.set_zoom_percent(100)


        self.graphic_view.view.mouse_tracker.mouseMoved.connect(lambda state: self.mousse_move(state["scene_pos"]))


        self.graphic_view.view.tool_changed.connect(lambda tool: self.change_tool(tool))
        #self.graphic_view.view.mouse_tracker.mouseClicked.connect(lambda state: print("Click", state["buttons"]))
        #self.graphic_view.view.mouse_tracker.mouseDoubleClicked.connect(lambda state: print("Double click"))
        self.graphic_view.view.mouse_tracker.mouseWheel.connect(lambda state: self.wheel_move())
        #self.graphic_view.view.mouse_tracker.mouseDragged.connect(lambda state: print("mouseDragged"))
        #self.graphic_view.view.mouse_tracker.mouseHovered.connect(lambda state: print("mouseHovered"))

        self.graphic_view.view.g_add_text_annotation("mouse", "", 10, 10, font=QFont("Arial", 8), style=None)
        self.graphic_view.view.g_add_text_annotation("zoom", f"Zoom : 100 %", 10, 30, font=QFont("Arial", 8), style=None)
        self.graphic_view.view.g_add_text_annotation("tool", f"Tool", 10, 50, font=QFont("Arial", 8), style=None)



        # mise a jour de la position des regles
        #self.graphic_view.set_ruler_position(horizontal="top", vertical="right")



        self.graphic_view.view.g_register_preview_method("Circle", CirclePreview)
        self.graphic_view.view.g_register_preview_method("Rectangle", RectanglePreview)
        self.graphic_view.view.g_register_preview_method("Line", LinePreview)
        self.graphic_view.view.g_register_preview_method("CircleFromCenter", CircleCenterPreview)
        self.graphic_view.view.g_register_preview_method("RectangleFromCenter", RectangleCenterPreview)
        self.graphic_view.view.g_register_preview_method("SquareFromCenter", SquareCenterPreview)
        self.graphic_view.view.g_register_preview_method("Square", SquarePreview)

        self.graphic_view.view.g_register_view_element("Circle", CircleElement)
        self.graphic_view.view.g_register_view_element("Rectangle", RectangleElement)
        self.graphic_view.view.g_register_view_element("Line", LineElement)
        self.graphic_view.view.g_register_view_element("CircleFromCenter", CircleCenterElement)
        self.graphic_view.view.g_register_view_element("RectangleFromCenter", RectangleCenterElement)
        self.graphic_view.view.g_register_view_element("SquareFromCenter", SquareCenterElement)
        self.graphic_view.view.g_register_view_element("Square", SquareElement)

        self.graphic_view.view.g_set_tool("SquareFromCenter")
        #self.graphic_view.view.g_set_tool("Mouse")

        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_L, "Line")
        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_R, "Rectangle")
        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_C, "Circle")
        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_T, "Text")
        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_O, "CircleFromCenter")
        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_S, "Square")

        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_M, "Mouse")
        self.graphic_view.view.g_register_shortcut(Qt.Key.Key_Escape, "Mouse")

        self.graphic_view.view.g_register_cursor("Rectangle", Qt.CursorShape.CrossCursor)
        self.graphic_view.view.g_register_cursor("Line", Qt.CursorShape.CrossCursor)
        self.graphic_view.view.g_register_cursor("Text", Qt.CursorShape.CrossCursor)
        self.graphic_view.view.g_register_cursor("Circle", Qt.CursorShape.CrossCursor)

        self.graphic_view.view.g_register_cursor("Mouse", Qt.CursorShape.ArrowCursor)


        #self.graphic_view.view.g_set_fill_color(QColor(0,0,0, 0))

        #self.graphic_view.view.g_change_border_color_items_selected(QColor(0, 255, 0))


        self.graphic_view.view.g_add_item(CircleCenterElement.create_custom_graphics_item(

            center=QPointF(100, 100),
            edge=QPointF(110, 110),
            border_color=QColor(255,0,0, 255),
            border_with=1,
            border_style=Qt.PenStyle.DashDotDotLine,
            fill_color=QColor(0,0,255),
            z_value=100
        ))

        self.graphic_view.view.g_add_item(CircleCenterElement.create_custom_graphics_item(

            center=QPointF(100, 100),
            edge=QPointF(110, 110),
            border_color=QColor(255, 0, 0, 255),
            border_with=1,
            border_style=Qt.PenStyle.DashDotDotLine,
            fill_color=QColor(0, 0, 255),
            z_value=100
        ))

    def mousse_move(self, scene_pos):
        self.graphic_view.view.annotation_manager.update_text("mouse",  f"x : {int(scene_pos.x())} | y = {int(scene_pos.y())}")


    def change_tool(self, tool: str):
        self.graphic_view.view.annotation_manager.update_text("tool",  f"Tool : {tool}")


    def wheel_move(self):
        var = int(self.graphic_view.view.camera.get_zoom_percent())

        self.graphic_view.view.annotation_manager.update_text("zoom",  f"Zoom : {var} %")




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
