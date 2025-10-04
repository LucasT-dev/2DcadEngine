import sys
import uuid

import keyboard
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtWidgets import QApplication, QGraphicsItem

from exemple.ItemInfoFormatter import ItemInfoFormatter
from graphic_view_element.element_manager.CircleCenterElement import CircleCenterElement
from graphic_view_element.element_manager.EllipseElement import CircleElement
from graphic_view_element.element_manager.LineElement import LineElement
from graphic_view_element.element_manager.PixmapElement import PixmapElement
from graphic_view_element.element_manager.RectangleCenterElement import RectangleCenterElement
from graphic_view_element.element_manager.RectangleElement import RectangleElement
from graphic_view_element.element_manager.RightLineElement import RightLineElement
from graphic_view_element.element_manager.SquareCenterElement import SquareCenterElement
from graphic_view_element.element_manager.SquareElement import SquareElement
from graphic_view_element.element_manager.TextElement import TextElement
from graphic_view_element.preview_manager.CircleCenterPreview import CircleCenterPreview
from graphic_view_element.preview_manager.CirclePreview import CirclePreview
from graphic_view_element.preview_manager.LinePreview import LinePreview
from graphic_view_element.preview_manager.PixmapPreview import PixmapPreview
from graphic_view_element.preview_manager.RectangleCenterPreview import RectangleCenterPreview
from graphic_view_element.preview_manager.RectanglePreview import RectanglePreview
from graphic_view_element.preview_manager.RightLinePreview import RightLinePreview
from graphic_view_element.preview_manager.SquareCenterPreview import SquareCenterPreview
from graphic_view_element.preview_manager.SquarePreview import SquarePreview
from graphic_view_element.preview_manager.TextPreview import TextPreview
from MainCad import MainCad
from serialisation.SceneSerializer import SceneSerializer

"""
Todo list :

OK -> voir pour mettre une meilleure preview pour les piwmap
OK -> corriger les hitbox des textes
OK -> bug avec les lettres des raccourci non utilisable dans les textes
OK -> systeme de groupe d'object
OK -> historique -> gestion des groupes d'object
OK -> bug -> régle et niveau de zoom non fonctionnel
OK -> ajouter la possibilité de creer des groupes d'object
OK -> systeme de sauvegarde de la scene en fichier de config
OK -> bug -> les images sont pas enregistré
OK -> bug -> apres une restauration l'emplacement du pixmap est différent
OK -> bug -> text a l'envers
OK -> bug -> verifier les groupes d'item sauvegardé
OK -> bug -> groupe d'item a revoir !
OK -> bug -> resize des groupes non fonctionnel
OK -> bug -> resize des groupes non fonctionnel supprimé

historique -> historiser les changements de couleur (move/resize OK) -> A tester



bug -> disparition des item apres un group / ungroup
undo des groupes !
destruction des groupes

Systeme de sauvegarde d'objet

sauvegarde d'un object

"""
class MyWindow(MainCad):

    def g_init_engine(self):

        # self.graphic_view = GraphicView(self.scene, show_ruler=True)

        # Inversion du repere
        self.g_get_view.g_scale(1, -1)
        self.g_get_view.g_set_scene_rectangle(-20, -20, 700, 600)

        # Zone de dessin

        self.g_get_view.g_set_render_hit(QPainter.RenderHint.Antialiasing)
        self.g_get_view.g_set_background_color("#5B5B5B")

        # Défini le centre de la scene
        # self.g_get_view.g_center_camera_on(0, 0)

        self.g_get_view.camera.set_pan_enabled(True)
        self.g_get_view.camera.set_zoom_enabled(True)

        # Défini la position de la grille par rapport au repere
        self.g_get_view.grid.set_origin_position("top-left")  # ou "center", "top-left", etc.

        # Afficher une grille
        # self.g_get_view.grid.draw_grid(QColor(3, 252, 190, 100), width=0, interval=10)
        # self.g_get_view.grid.draw_grid(QColor(250, 250, 250, 100), width=0, interval=50)

        # Ligne axe X/Y
        self.g_get_view.grid.draw_line(color=QColor(0, 255, 0, 150), width=1,
                                              start_x=-10, start_y=0,
                                              end_x=self.g_get_view.width(), end_y=0)

        self.g_get_view.grid.draw_line(color=QColor(255, 0, 0, 150), width=1,
                                              start_x=0, start_y=self.g_get_view.height(),
                                              end_x=0, end_y=-10)

        # Mise à jour du style des règles
        self.g_get_graphic_view.h_ruler.update_style(
            background="#2D2D2D",
            tick=QColor(0, 255, 0, 150),
            text="#FFFFFF",
            font_family="Helvetica",
            font_size=7
        )

        # Mise à jour du style des règles
        self.g_get_graphic_view.v_ruler.update_style(
            background="#2D2D2D",
            tick=QColor(255, 0, 0, 150),
            text="#FFFFFF",
            font_family="Helvetica",
            font_size=7
        )

        # Ajoute l'Axe X
        self.g_get_view.grid.draw_X_axis(
            color=QColor(0, 255, 0),  # Axes verts
            width=2,  # Épaisseur de 3 pixels
            name="X",  # Nom personnalisé
            axis_length=30,  # Axes de 300 pixels
            x_label="X"  # Label personnalisé pour X

        )

        # Ajoute l'Axe Y
        self.g_get_view.grid.draw_Y_axis(
            color=QColor(255, 0, 0),  # Axes verts
            width=2,  # Épaisseur de 3 pixels
            name="Y",  # Nom personnalisé
            axis_length=30,  # Axes de 300 pixels
            y_label="Y",  # Label personnalisé pour Y
            text_rotate=180
        )

        # self.g_get_view.grid.move_coordinate_system("Y", 100, 100, -20, -40)
        # self.g_get_view.grid.move_coordinate_system("X", 100, 100, 20, 0)

        # Dessiner des points noirs de rayon 4 pixels espacés de 50 pixels
        """self.g_get_view.grid.draw_point(
            color=QColor("#000000"),
            radius=2,
            interval_x=50,
            interval_y=50,
            name="points"
        )"""

        self.g_get_view.camera.set_zoom_limits(0.8, 10.0)
        self.g_get_view.camera.set_zoom_factor(1.2)  # 1.2
        self.g_get_view.camera.set_zoom_to_cursor(True)
        self.g_get_view.camera.zoom_to(1.0)

        # Définir unité des règle (mm, cm, pixel)
        self.g_get_view.g_set_unit("mm")

        # Applique un zoom à 100% réel
        self.g_get_view.camera.set_zoom_percent(100)

        self.g_get_view.mouse_tracker.mouseMoved.connect(lambda state: self.mousse_move(state["scene_pos"]))
        self.g_get_view.mouse_tracker.mouseMoved.connect(lambda state: self.update_history(self._scene))
        self.g_get_view.tool_changed.connect(lambda tool: self.change_tool(tool))
        self.g_get_view.selection_changed.connect(lambda selection: self.selection_changed(selection))

        # self.g_get_view.mouse_tracker.mouseClicked.connect(lambda state: print("Click", state["buttons"]))
        # self.g_get_view.mouse_tracker.mouseDoubleClicked.connect(lambda state: print("Double click"))
        self.g_get_view.mouse_tracker.mouseWheel.connect(lambda state: self.wheel_move())
        # self.g_get_view.mouse_tracker.mouseDragged.connect(lambda state: print("mouseDragged"))
        # self.g_get_view.mouse_tracker.mouseHovered.connect(lambda state: print("mouseHovered"))

        self.g_get_view.g_add_text_annotation("mouse", "<b>x :</b> 0 <b>| y :</b> 0", 10, 10,
                                                     font=QFont("Arial", 8), style=None)
        self.g_get_view.g_add_text_annotation("zoom", f"<b>Zoom :</b> 100 %", 10, 30, font=QFont("Arial", 8),
                                                     style=None)
        self.g_get_view.g_add_text_annotation("tool", f"<b>Tool :</b> mouse", 10, 50, font=QFont("Arial", 8),
                                                     style=None)

        self.g_get_view.g_add_text_annotation("item_info", f"<b> Item information </b>", 500, 10,
                                                     font=QFont("Arial", 8), style=None)

        self.g_get_view.g_add_text_annotation("history_info", f"<b> History </b>", 500, 300,
                                              font=QFont("Arial", 8), style=None)

        # mise a jour de la position des regles
        # self.graphic_view.set_ruler_position(horizontal="top", vertical="right")

        self.g_get_view.g_register_preview_method("Circle", CirclePreview)
        self.g_get_view.g_register_preview_method("Rectangle", RectanglePreview)
        self.g_get_view.g_register_preview_method("Line", LinePreview)
        self.g_get_view.g_register_preview_method("RightLine", RightLinePreview)
        self.g_get_view.g_register_preview_method("CircleFromCenter", CircleCenterPreview)
        self.g_get_view.g_register_preview_method("RectangleFromCenter", RectangleCenterPreview)
        self.g_get_view.g_register_preview_method("SquareFromCenter", SquareCenterPreview)
        self.g_get_view.g_register_preview_method("Square", SquarePreview)
        self.g_get_view.g_register_preview_method("Text", TextPreview)
        self.g_get_view.g_register_preview_method("Pixmap", PixmapPreview)

        self.g_get_view.g_register_view_element("Circle", CircleElement)
        self.g_get_view.g_register_view_element("Rectangle", RectangleElement)
        self.g_get_view.g_register_view_element("Line", LineElement)
        self.g_get_view.g_register_view_element("RightLine", RightLineElement)
        self.g_get_view.g_register_view_element("CircleFromCenter", CircleCenterElement)
        self.g_get_view.g_register_view_element("RectangleFromCenter", RectangleCenterElement)
        self.g_get_view.g_register_view_element("SquareFromCenter", SquareCenterElement)
        self.g_get_view.g_register_view_element("Square", SquareElement)
        self.g_get_view.g_register_view_element("Text", TextElement)
        self.g_get_view.g_register_view_element("Pixmap", PixmapElement)

        # self.g_get_view.g_set_tool("SquareFromCenter")
        self.g_get_view.g_set_tool("Mouse")


        self.g_get_view.g_register_shortcut(Qt.Key.Key_C, "Circle")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_R, "Rectangle")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_L, "Line")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_I, "RightLine")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_O, "CircleFromCenter")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_Y, "RectangleFromCenter")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_H, "SquareFromCenter")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_S, "Square")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_T, "Text")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_P, "Pixmap")

        self.g_get_view.g_register_shortcut(Qt.Key.Key_M, "Mouse")
        self.g_get_view.g_register_shortcut(Qt.Key.Key_Escape, "Mouse")

        self.g_get_view.g_register_cursor("Rectangle", Qt.CursorShape.CrossCursor)
        self.g_get_view.g_register_cursor("Line", Qt.CursorShape.CrossCursor)
        self.g_get_view.g_register_cursor("Text", Qt.CursorShape.CrossCursor)
        self.g_get_view.g_register_cursor("Circle", Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_cursor("Mouse", Qt.CursorShape.ArrowCursor)

        # self.g_get_view.g_set_fill_color(QColor(0,0,0, 0))

        # self.g_get_view.g_change_border_color_items_selected(QColor(0, 255, 0))

        self.g_get_view.g_add_item(CircleCenterElement.create_custom_graphics_item(

            center=QPointF(100, 100),
            edge=QPointF(110, 110),
            border_color=QColor(255, 0, 0, 255),
            border_with=1,
            border_style=Qt.PenStyle.DashDotDotLine,
            fill_color=QColor(0, 0, 255),
            key=0,
            value="test data 0",
            z_value=100
        ))

        uuid_test = str(uuid.uuid4())

        self.g_get_view.g_add_item(CircleCenterElement.create_custom_graphics_item(

            center=QPointF(100, 100),
            edge=QPointF(110, 110),
            border_color=QColor(255, 0, 0, 255),
            border_with=1,
            border_style=Qt.PenStyle.DashDotDotLine,
            fill_color=QColor(0, 0, 255),
            key=0, value=uuid_test,
            z_value=100
        ))

        item = self.g_get_view.g_get_item_by_data(key=0, value=uuid_test)
        item.setData(3, "Test 3")



        self.g_get_view.g_set_shortcut_undo_action()
        self.g_get_view.g_set_shortcut_redo_action()
        self.g_get_view.g_set_shortcut_delete_item()


        self.g_get_view.set_undo_limit(10)

        keyboard.add_hotkey('g', self.group_function)
        keyboard.add_hotkey('u', self.ungroup_function)

        keyboard.add_hotkey('a', self.serialize)
        keyboard.add_hotkey('b', self.unserialize)

        print("Moteur initialisé !")

    def serialize(self):

        g_get_item = self.g_get_view.g_get_items()
        SceneSerializer.save_to_file(g_get_item, "test_json")

    def unserialize(self):

        items = SceneSerializer.load_from_file("test_json")

        for item in items:

            print(item)
            self.g_get_view.g_add_item(item)




    def group_function(self):
        print("group")
        self.g_get_view.g_group_selected_items()

    def ungroup_function(self):
        print("ungroup")
        self.g_get_view.g_ungroup_selected_items()


    def mousse_move(self, scene_pos):

        self.g_get_view.annotation_manager.update_text("mouse",
                                                              f"<b>x :</b> {int(scene_pos.x())} <b>| y :</b> {int(scene_pos.y())}")

    def update_history(self, scene):

        self.g_get_view.annotation_manager.update_text("history_info",
                                                       f"<b> History <hr> </b> {self.get_history_string(scene.undo_stack)}")

    def change_tool(self, tool: str):
        self.g_get_view.annotation_manager.update_text("tool", f"<b>Tool :</b> {tool}")
        if tool == "Mouse" :
            self.g_get_view.g_unselect_items()

    def wheel_move(self):
        var = int(self.g_get_view.camera.get_zoom_percent())

        self.g_get_view.annotation_manager.update_text("zoom", f"<b>Zoom :</b> {var} %")

    def selection_changed(self, items: list[QGraphicsItem]):
        if not items:
            self.g_get_view.annotation_manager.update_text("item_info", f" ")
            return

        text = ItemInfoFormatter().format_items(items)
        self.g_get_view.annotation_manager.update_text("item_info", f"{text}")

    def get_history_string(self, undo_stack):
        """
               Retourne une chaîne listant toutes les actions enregistrées
               dans l'ordre, en marquant la position courante.
               """
        lines = []
        current_index = undo_stack.index()  # position courante dans la pile

        for i in range(undo_stack.count()):
            cmd = undo_stack.command(i)

            # Si la commande possède une méthode details(), on l'utilise
            cmd_text = cmd.details() if hasattr(cmd, "details") else cmd.text()

            if i == current_index:
                lines.append(f"<b> > {cmd_text} <br> </b>")  # Marque l'action suivante à exécuter pour redo
            else:
                lines.append(f"  {cmd_text} <br>")

        return "\n".join(lines)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    window.resize(800, 600)

    sys.exit(app.exec())



