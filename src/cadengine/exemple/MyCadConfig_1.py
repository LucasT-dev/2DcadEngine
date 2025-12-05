import faulthandler
import json
import sys

import keyboard
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPageSize, QPageLayout, QTransform
from PyQt6.QtWidgets import QApplication, QGraphicsItem

from src.cadengine.exemple.ItemInfoFormatter import ItemInfoFormatter
from src.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CircleElement import CircleElement
from src.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CirclePreview import CirclePreview
from src.cadengine.graphic_view_element.GraphicItemManager.CircleElement.CircleResizable import CircleResizable
from src.cadengine.graphic_view_element.GraphicItemManager.EllipseElement.EllipseElement import EllipseElement
from src.cadengine.graphic_view_element.GraphicItemManager.EllipseElement.EllipsePreview import EllipsePreview
from src.cadengine.graphic_view_element.GraphicItemManager.EllipseElement.EllipseResizable import EllipseResizable
from src.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupElement import GroupElement
from src.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupPreview import GroupPreview
from src.cadengine.graphic_view_element.GraphicItemManager.GroupElement.GroupResizable import GroupResizable
from src.cadengine.graphic_view_element.GraphicItemManager.LineElement.LineElement import LineElement
from src.cadengine.graphic_view_element.GraphicItemManager.LineElement.LineResizable import LineResizable
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapElement import PixmapElement
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapPreview import PixmapPreview
from src.cadengine.graphic_view_element.GraphicItemManager.PixmapElement.PixmapResizable import PixmapResizable
from src.cadengine.graphic_view_element.GraphicItemManager.LineElement.LinePreview import LinePreview
from src.cadengine.graphic_view_element.GraphicItemManager.RectangleElement.RectangleElement import RectangleElement
from src.cadengine.graphic_view_element.GraphicItemManager.RectangleElement.RectanglePreview import RectanglePreview
from src.cadengine.graphic_view_element.GraphicItemManager.RectangleElement.RectangleResizable import RectangleResizable
from src.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquareElement import SquareElement
from src.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquarePreview import SquarePreview
from src.cadengine.graphic_view_element.GraphicItemManager.SquareElement.SquareResizable import SquareResizable
from src.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextElement import TextElement
from src.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextPreview import TextPreview
from src.cadengine.graphic_view_element.GraphicItemManager.TextElement.TextResizable import TextResizable
from src.cadengine.MainCad import MainCad

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
OK -> undo des groupes / ungroupe !
OK -> destruction des groupes
OK -> Export sous PDF...
OK -> resize groupe a tester
OK -> bug -> les objects bouge lors de la création d'un item
OK -> bug -> pas de undo sur la création d'item

historique -> historiser les changements de couleur (move/resize OK) -> A tester

bug -> disparition des item apres un group / ungroup
legée bug sur le zoom

"""
class MyWindow(MainCad):

    def g_init_engine(self):

        # self.graphic_view = GraphicView(self.scene, show_ruler=True)

        # Inversion du repere
        self.g_get_view.g_set_scale(1, -1)
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
            axis_length=15,  # Axes de 15 pixels
            x_label="X"  # Label personnalisé pour X

        )

        # Ajoute l'Axe Y
        self.g_get_view.grid.draw_Y_axis(
            color=QColor(255, 0, 0),  # Axes verts
            width=2,  # Épaisseur de 3 pixels
            name="Y",  # Nom personnalisé
            axis_length=15,  # Axes de 15 pixels
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
        #self.g_get_view.camera.zoom_to(1.0)

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

        self.g_get_view.g_register_element(element_name="line", element_class=LineElement, preview_class=LinePreview, resizable_class=LineResizable)
        self.g_get_view.g_register_shortcut(name="line", key=Qt.Key.Key_L)
        self.g_get_view.g_register_cursor(name="line", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element(element_name="rect", element_class=RectangleElement, preview_class=RectanglePreview, resizable_class=RectangleResizable)
        self.g_get_view.g_register_shortcut(name="rect", key=Qt.Key.Key_R)
        self.g_get_view.g_register_cursor(name="rect", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element(element_name="ellipse", element_class=EllipseElement, preview_class=EllipsePreview, resizable_class=EllipseResizable)
        self.g_get_view.g_register_shortcut(name="ellipse", key=Qt.Key.Key_E)
        self.g_get_view.g_register_cursor(name="ellipse", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element(element_name="text", element_class=TextElement, preview_class=TextPreview, resizable_class=TextResizable)
        self.g_get_view.g_register_shortcut(name="text", key=Qt.Key.Key_T)
        self.g_get_view.g_register_cursor(name="text", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element(element_name="square", element_class=SquareElement, preview_class=SquarePreview, resizable_class=SquareResizable)
        self.g_get_view.g_register_shortcut(name="square", key=Qt.Key.Key_S)
        self.g_get_view.g_register_cursor(name="square", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element("circle", element_class=CircleElement, preview_class=CirclePreview, resizable_class=CircleResizable)
        self.g_get_view.g_register_shortcut(name="circle", key=Qt.Key.Key_C)
        self.g_get_view.g_register_cursor(name="circle", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element("image", element_class=PixmapElement, preview_class=PixmapPreview, resizable_class=PixmapResizable)
        self.g_get_view.g_register_shortcut(name="image", key=Qt.Key.Key_P)
        self.g_get_view.g_register_cursor(name="image", cursor=Qt.CursorShape.CrossCursor)

        self.g_get_view.g_register_element("group", element_class=GroupElement,
                                           preview_class=GroupPreview, resizable_class=GroupResizable)
        self.g_get_view.g_register_shortcut(name="group", key=Qt.Key.Key_G)
        self.g_get_view.g_register_cursor(name="group", cursor=Qt.CursorShape.CrossCursor)

        # modifie les propriete par défaut des items
        self.g_get_view.g_set_default_border_color(QColor(0, 0, 0, 255))
        self.g_get_view.g_set_default_fill_color(QColor(255, 255, 255, 255))
        self.g_get_view.g_set_default_border_width(1)
        self.g_get_view.g_set_default_border_style(Qt.PenStyle.SolidLine)

        self.g_get_view.g_add_item(name="ellipse", history=True, first_point=QPointF(50, 400),
                        second_point=QPointF(0, 100),
                        fill_color=QColor("white"),
                        border_color=QColor("blue"),
                        border_width=2,
                        border_style=Qt.PenStyle.DashDotDotLine,
                        z_value=100,
                        transform=QTransform(),
                        visibility=True,
                        scale=1.0
                                   )

        self.g_get_view.g_add_item(name="text", history=True, first_point=QPointF(150, 300),
                        second_point=QPointF(180, 250),
                        z_value=100)

        # self.g_get_view.g_change_border_color_items_selected(QColor(0, 255, 0))

        self.g_get_view.g_add_item(name="ellipse",
                        first_point=QPointF(150, 300),
                        second_point=QPointF(180, 200),
                        border_color=QColor(255, 0, 0, 255),
                        border_width=1,
                        border_style=Qt.PenStyle.DashDotDotLine,
                        fill_color=QColor(0, 0, 255),
                        z_value=100,
                        transform=QTransform(),
                        visibility=True,
                        scale=1.0
        )

        self.g_get_view.g_set_shortcut_undo_action()
        self.g_get_view.g_set_shortcut_redo_action()
        self.g_get_view.g_set_shortcut_delete_item()

        self.g_get_view.set_undo_limit(10)


        keyboard.add_hotkey('g', self.group_function)
        keyboard.add_hotkey('u', self.ungroup_function)

        keyboard.add_hotkey('a', self.serialize)
        keyboard.add_hotkey('b', self.deserialize)

        keyboard.add_hotkey('escape', self.escape)

        keyboard.add_hotkey('p', self.export_to_pdf)

        print("Moteur initialisé !")

    def escape(self):
        self.g_get_view.g_set_tool("mousse")
        self.g_get_view.g_set_cursor(Qt.CursorShape.ArrowCursor)

    def serialize(self):

        data = self.g_get_view.g_serialize_item_scene()

        with open("test_1.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def deserialize(self):
        # Lire le fichier JSON
        with open("test_1.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Appeler ta fonction interne qui reconstruit les objets

        for item in self.g_get_view.g_deserialize_items(data):
            self.g_get_view.g_add_QGraphicitem(item)

    def export_to_pdf(self):

        visible_scene_rect = self.g_get_view.mapToScene(self.g_get_view.viewport().rect()).boundingRect()

        self.g_get_view.export_scene_to_pdf(
            scene=self.g_get_view.scene(),
            filename="output.pdf",
            render_rect=visible_scene_rect,
            format=QPageSize.PageSizeId.A4,
            orientation=QPageLayout.Orientation.Landscape
        )

    def group_function(self):
        self.g_get_view.g_group_selected_items()

    def ungroup_function(self):
        self.g_get_view.g_ungroup_selected_items()


    def mousse_move(self, scene_pos):

        self.g_get_view.annotation_manager.update_text("mousse",
                                                              f"<b>x :</b> {int(scene_pos.x())} <b>| y :</b> {int(scene_pos.y())}")

    def update_history(self, scene):

        self.g_get_view.annotation_manager.update_text("history_info",
                                                       f"<b> History <hr> </b> {self.get_history_string(scene.undo_stack)}")

    def change_tool(self, tool: str):
        self.g_get_view.annotation_manager.update_text("tool", f"<b>Tool :</b> {tool}")
        if tool == "mousse" :
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

    faulthandler.enable(all_threads=True)

    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    window.resize(800, 600)

    sys.exit(app.exec())



