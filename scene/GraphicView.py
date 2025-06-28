from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QColor, QFont, QCursor
from PyQt6.QtWidgets import QGraphicsView, QWidget, QGridLayout, QGraphicsScene

from draw.CameraManager import Camera
from draw.CursorManager import CursorManager
from draw.Draw import Draw
from draw.DynamicInformationManager import AnnotationManager
from draw.GridManager import Grid
from draw.MouseTracker import MouseTracker
from draw.RulesManager import HorizontalRuler, VerticalRuler, CornerRuler
from graphic_view_element.PreviewManager import PreviewManager
from graphic_view_element.ElementManager import ElementManager
from graphic_view_element.style.StyleElement import StyleElement


class GraphicViewContainer(QWidget):
    def __init__(self, scene: QGraphicsScene, show_ruler=False, ruler_positions=None, parent=None):
        super().__init__(parent)

        self.view = GraphicView(scene)
        self.show_ruler = show_ruler

        # Définir les positions par défaut si non spécifiées
        self.ruler_positions = ruler_positions or {
            "horizontal": "top",    # "top" ou "bottom"
            "vertical": "left"      # "left" ou "right"
        }

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.h_ruler = None
        self.v_ruler = None
        self.rule_corner = None

        self._setup_ui()

    def _setup_ui(self):
        if self.show_ruler:
            self.h_ruler = HorizontalRuler(self.view)
            self.v_ruler = VerticalRuler(self.view)
            self.rule_corner = CornerRuler(self.view)

            # Index du coin vide
            corner_row = 0 if self.ruler_positions["horizontal"] == "top" else 2
            corner_col = 0 if self.ruler_positions["vertical"] == "left" else 2

            # Position horizontale
            if self.ruler_positions["horizontal"] == "top":
                self.layout.addWidget(self.h_ruler, 0, 1)
            elif self.ruler_positions["horizontal"] == "bottom":
                self.layout.addWidget(self.h_ruler, 2, 1)

            # Position verticale
            if self.ruler_positions["vertical"] == "left":
                self.layout.addWidget(self.v_ruler, 1, 0)
            elif self.ruler_positions["vertical"] == "right":
                self.layout.addWidget(self.v_ruler, 1, 2)

            # Ajouter la vue graphique au centre
            self.layout.addWidget(self.view, 1, 1)

            # Ajouter le coin vide
            self.layout.addWidget(self.rule_corner, corner_row, corner_col)

            self.view.rulers = {"h": self.h_ruler, "v": self.v_ruler}

        else:
            self.layout.addWidget(self.view, 0, 0)

        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(1, 1)
        self.setLayout(self.layout)

    def set_ruler_position(self, horizontal: str = None, vertical: str = None):
        """Change dynamiquement la position des règles (top/bottom et left/right)."""
        if horizontal in ("top", "bottom"):
            self.ruler_positions["horizontal"] = horizontal

        if vertical in ("left", "right"):
            self.ruler_positions["vertical"] = vertical

        # Supprimer les anciens widgets de la grille
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                self.layout.removeWidget(widget)
                widget.setParent(None)

        # Réinitialiser l'interface avec les nouvelles positions
        self._setup_ui()


class GraphicView(QGraphicsView):

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)

        # Composants métiers
        self.draw = Draw()
        self.grid = Grid(self)
        self.camera = Camera(self)
        self.cursor_manager = CursorManager()
        self.annotation_manager = AnnotationManager(self)

        # Event
        self.mouse_tracker = MouseTracker(self)


        # Element style
        self.style_element = StyleElement()

        # Creation des element
        self.element_registry = ElementManager()

        # Preview
        self.preview_manager = PreviewManager(scene, self.style_element, self.element_registry)
        #self.GraphicItem = GraphicItem(scene)


        self.shortcut_map = {}  # clé Qt.Key → nom d'outil



        # Configuration de base de la vue
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


    def g_set_render_hit(self, render: QPainter.RenderHint):
        """
        Sets a specific render hint for the QPainter instance.

        This method allows enabling or modifying the rendering hints for
        the current QPainter instance. Rendering hints can optimize
        rendering for quality, performance, or other specified criteria.

        :param render: A render hint to be applied to the QPainter instance.
        :type render: QPainter.RenderHint
        :return: None
        """
        self.setRenderHint(render)

    def g_set_background_color(self, hex_color: str):
        """
        Définit la couleur de fond à partir d'une valeur hexadécimale.

        :param hex_color: Couleur au format hexadécimal (ex: '#FF0000' ou '#FF0000FF' avec alpha)
        """
        self.setBackgroundBrush(QBrush(QColor(hex_color)))

    def g_scale(self, sx, sy):
        self.scale(sx, sy)

    def g_set_scene_rectangle(self, ax: float=-1000, ay: float=-1000, aw: float=2000, ah: float=2000):
        self.setSceneRect(ax, ay, aw, ah)

    def g_center_camera_on(self, pos_x: int, pos_y: int):
        self.centerOn(pos_x, pos_y)


    # --------------------start text annotation --------------------

    def g_add_text_annotation(self, id_: str, text: str, x: int, y: int, font: QFont, style):
        self.annotation_manager.add_label(id_, text, x, y, font=font, style=style)

    def g_update_text_annotation(self, id_: str, new_text: str):
        self.annotation_manager.update_text(id_, new_text)

    def g_remove_annotation(self, id_: str):
        self.annotation_manager.remove_label(id_)

    # -------------------- end text annotation ---------------------

    # -------------------- start scene unit ------------------------

    def g_set_unit(self, unit: str):
        if unit not in ("px", "mm", "cm"):
            raise ValueError("Unit must be 'px', 'mm' or 'cm'")

        if hasattr(self, 'rulers'):
            self.rulers["h"].unit = unit
            self.rulers["v"].unit = unit

            self._update_rulers()

    # -------------------- end scene unit --------------------------


    # -------------------- start style method ------------------

    def g_set_fill_color(self, color: QColor):
        self.style_element.set_fill_color(color)

    def g_set_border_color(self, color: QColor):
        self.style_element.set_border_color(color)

    def g_set_border_width(self, width: int):
        self.style_element.set_border_width(width)

    def g_set_border_style(self, border_style: Qt.PenStyle):
        self.style_element.set_border_style(border_style)

    def g_set_tool(self, tool: str):
        self.style_element.set_tool(tool)

    def g_get_tool(self):
        self.style_element.get_tool()

    # -------------------- end style method --------------------


    # -------------------- start register object preview method-

    def g_register_preview_method(self, tool_name: str, preview_class):
        self.preview_manager.register_tool_preview(tool_name, preview_class)

    # -------------------- end register object preview method --


    # -------------------- start register object view method ---
    def g_register_view_element(self, tool_name: str, view_class):
        """Associer une preview à un nom d’outil (Tool ou str)."""
        self.element_registry.register(tool_name, view_class)

    # -------------------- end register object view method -----


    # -------------------- start register shortcut tool --------

    def g_register_shortcut(self, qt_key: Qt.Key, tool_name: str):
        """Associe une touche Qt à un nom d’outil (ex: Qt.Key_L → 'line')"""
        self.shortcut_map[qt_key] = tool_name
        print(f"[RACCOURCI] {qt_key.name} → {tool_name}")

    # -------------------- end register shortcut tool ----------


    # -------------------- start register cursor tool --------

    def g_register_cursor(self, tool_name: str, cursor: Qt.CursorShape | QCursor):
        """Associe une touche Qt à un nom d’outil (ex: Qt.Key_L → 'line')"""
        self.cursor_manager.register_tool(tool_name, cursor)
        print(f"[Cursor register] {tool_name} → {cursor.name}")

    def g_set_cursor(self, cursor: Qt.CursorShape | QCursor):
        self.setCursor(cursor)


    # -------------------- end register cursor tool ----------


    # -------------------- private method --------------------

    def _update_rulers(self):
        """Mettre à jour les règles si elles existent"""
        if hasattr(self, 'rulers'):
            self.rulers["h"].update()
            self.rulers["v"].update()

    # -------------------- private method --------------------

    def g_get_mouse_state(self):
        return self.mouse_tracker.get_mouse_state()


    # -------------------- EVENT --------------------
    def wheelEvent(self, event):
        self.mouse_tracker.process_wheel(event)

        if not self.camera.handle_wheel(event):
            super().wheelEvent(event)

        # mise a jour des rulers
        self._update_rulers()

        print(self.camera.get_current_zoom())


    def mousePressEvent(self, event):

        # Ignorer si clic molette
        if event.button() == Qt.MouseButton.MiddleButton:
            # Tu peux laisser passer le mouvement caméra ici si tu veux :
            self.mouse_tracker.process_mouse_press(event)
            self.camera.handle_mouse_press(event)  # facultatif
            return  # on ne fait rien d’autre (pas de preview, pas de super())


        self.mouse_tracker.process_mouse_press(event)

        if not self.camera.handle_mouse_press(event):
            super().mousePressEvent(event)

        # mise a jour des rulers
        self._update_rulers()

        # Création de la preview
        self.preview_manager.start_preview(self.mapToScene(event.pos()))


    def mouseReleaseEvent(self, event):

        # Ignorer si clic molette
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_tracker.process_mouse_release(event)
            self.camera.handle_mouse_release(event)
            return

        self.mouse_tracker.process_mouse_release(event)

        if not self.camera.handle_mouse_release(event):
            super().mouseReleaseEvent(event)

        self.preview_manager.create_item(self.mapToScene(event.pos()))



    def mouseDoubleClickEvent(self, event):
        self.mouse_tracker.process_mouse_double_click(event)
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_tracker.process_mouse_move(event)

        if not self.camera.handle_mouse_move(event):
            super().mouseMoveEvent(event)

        self.preview_manager.update_preview(self.mapToScene(event.pos()))




    def resizeEvent(self, event):
        super().resizeEvent(event)

        # mise a jour des rulers
        self._update_rulers()

        self.annotation_manager.resize_all()



    def scrollContentsBy(self, dx: int, dy: int):
        super().scrollContentsBy(dx, dy)

        # mise a jour des rulers
        self._update_rulers()


    def keyPressEvent(self, event):

        print("KEY PRESS")

        key = event.key()

        if key in self.shortcut_map:
            tool = self.shortcut_map[key]
            self.g_set_tool(tool)
            print(f"[TOOL] Activation de l'outil '{tool}' via touche : {key}")
            event.accept()

            cursor = self.cursor_manager.get_cursor(tool)
            if cursor:
                self.setCursor(cursor)
            else:
                self.unsetCursor()

            return

        super().keyPressEvent(event)

    # -------------------- EVENT --------------------

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        if painter.begin(self.viewport()):
            try:
                scale = self.transform().m11()
            finally:
                painter.end()













