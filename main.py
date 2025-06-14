import sys

from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene

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


        self.graphic_view.view.camera.set_zoom_limits(1.0, 10.0)
        self.graphic_view.view.camera.set_zoom_factor(1.2)
        self.graphic_view.view.camera.set_zoom_to_cursor(True)
        self.graphic_view.view.camera.zoom_to(1.0)



        self.graphic_view.view.mouse_tracker.mouseMoved.connect(lambda state: self.mousse_move(state["scene_pos"]))
        self.graphic_view.view.mouse_tracker.mouseClicked.connect(lambda state: print("Click", state["buttons"]))
        self.graphic_view.view.mouse_tracker.mouseDoubleClicked.connect(lambda state: print("Double click"))
        self.graphic_view.view.mouse_tracker.mouseWheel.connect(lambda state: print("mouseWheel"))
        self.graphic_view.view.mouse_tracker.mouseDragged.connect(lambda state: print("mouseDragged"))
        self.graphic_view.view.mouse_tracker.mouseHovered.connect(lambda state: print("mouseHovered"))

        self.graphic_view.view.g_add_text_annotation("mouse", "", 10, 10, font=QFont("Arial", 8), style=None)


        # mise a jour de la position des regles
        #self.graphic_view.set_ruler_position(horizontal="top", vertical="right")

    def mousse_move(self, scene_pos):
        self.graphic_view.view.annotation_manager.update_text("mouse",  f"x = {int(scene_pos.x())} | y = {int(scene_pos.y())}")




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
