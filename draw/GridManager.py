from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QColor, QFont, QBrush
from PyQt6.QtWidgets import QGraphicsTextItem


class Grid:

    def __init__(self, view):

        super().__init__()

        self.view = view
        self.scene = view.scene()

        self.grid_name_saved = []

        self.origin = None

    def set_origin_position(self, position: str = "center"):
        """
        Définit la position du point zéro et ajuste la génération des lignes en conséquence.

        :param position: Position du point zéro ("center", "top-left", "top-right", "bottom-left", "bottom-right")
        """
        scene_width = self.view.width()
        scene_height = self.view.height()

        # Définir les points de départ et fin pour les lignes en fonction de la position
        if position == "center":
            start_x = -scene_width // 2
            end_x = scene_width // 2
            start_y = -scene_height // 2
            end_y = scene_height // 2

        elif position == "top-left":
            start_x = 0
            end_x = scene_width
            start_y = 0
            end_y = scene_height

        elif position == "top-right":
            start_x = -scene_width
            end_x = 0
            start_y = 0
            end_y = scene_height

        elif position == "bottom-left":
            start_x = 0
            end_x = scene_width
            start_y = -scene_height
            end_y = 0

        elif position == "bottom-right":
            start_x = -scene_width
            end_x = 0
            start_y = -scene_height
            end_y = 0
        else:
            raise ValueError("Position non valide")

        # Sauvegarder les coordonnées pour les autres méthodes
        self.origin = {
            "start_x": start_x,
            "end_x": end_x,
            "start_y": start_y,
            "end_y": end_y,
            "position": position
        }

    def draw_line(self, color: QColor, width: int, start_x: float, start_y: float, end_x: float, end_y: float, name: str = "line", line_style: Qt.PenStyle=Qt.PenStyle.SolidLine):

        grid_pen = QPen(color)
        grid_pen.setStyle(line_style)
        grid_pen.setWidth(width)

        self.scene.addLine(
            start_x, start_y,
            end_x, end_y,
            grid_pen
        )

        if name not in self.grid_name_saved:
            self.grid_name_saved.append(name)

    def get_origin_position(self) -> tuple[float, float]:
        """Retourne la position absolue du point zéro dans la scène"""
        position = self.origin["position"]
        match position:
            case "center":
                return 0, 0
            case "top-left":
                return self.origin["start_x"], self.origin["start_y"]
            case "top-right":
                return self.origin["end_x"], self.origin["start_y"]

            case "bottom-left":
                return self.origin["start_x"], self.origin["end_y"]
            case "bottom-right":
                return self.origin["end_x"], self.origin["end_y"]
            case _:
                return (0, 0)

    def draw_grid(self, color: QColor, width: int, interval: int=1, name: str= "grid", line_style: Qt.PenStyle=Qt.PenStyle.SolidLine):

        if not hasattr(self, 'origin'):
            self.set_origin_position("center")  # Position par défaut

        grid_pen = QPen(color)
        grid_pen.setStyle(line_style)
        grid_pen.setWidth(width)

        ox, oy = self.get_origin_position()  # point (0, 0) visuel

        # --- Lignes verticales (X)
        x = ox
        while x >= self.origin["start_x"]:
            self._draw_grid_line(x, self.origin["start_y"], x, self.origin["end_y"], grid_pen, name)
            x -= interval
        x = ox + interval
        while x <= self.origin["end_x"]:
            self._draw_grid_line(x, self.origin["start_y"], x, self.origin["end_y"], grid_pen, name)
            x += interval

        # --- Lignes horizontales (Y)
        y = oy
        while y >= self.origin["start_y"]:
            self._draw_grid_line(self.origin["start_x"], y, self.origin["end_x"], y, grid_pen, name)
            y -= interval
        y = oy + interval
        while y <= self.origin["end_y"]:
            self._draw_grid_line(self.origin["start_x"], y, self.origin["end_x"], y, grid_pen, name)
            y += interval

        if name not in self.grid_name_saved:
            self.grid_name_saved.append(name)

    def _draw_grid_line(self, x1, y1, x2, y2, pen, name):
        line = self.scene.addLine(x1, y1, x2, y2, pen)
        line.setData(1, name)

    def draw_point(self, color: QColor, radius: int, interval_x: int = 50, interval_y: int = 50, name: str = "point"):
        """
        Dessine des points centrés autour du point (0, 0) défini par set_origin_position().
        """

        if not hasattr(self, 'origin'):
            self.set_origin_position("center")  # fallback

        ox, oy = self.get_origin_position()  # point (0,0) visuel
        pen = QPen(color)
        brush = QBrush(color)

        # --- Boucle X à partir de ox
        x = ox
        while x >= self.origin["start_x"]:
            self._draw_point_column(x, oy, radius, interval_y, pen, brush, name, direction="down")
            self._draw_point_column(x, oy, radius, interval_y, pen, brush, name, direction="up")
            x -= interval_x
        x = ox + interval_x
        while x <= self.origin["end_x"]:
            self._draw_point_column(x, oy, radius, interval_y, pen, brush, name, direction="down")
            self._draw_point_column(x, oy, radius, interval_y, pen, brush, name, direction="up")
            x += interval_x

        if name not in self.grid_name_saved:
            self.grid_name_saved.append(name)

    def _draw_point_column(self, x: float, origin_y: float, radius: int, interval_y: int, pen, brush, name,
                           direction: str):
        """
        Dessine une colonne verticale de points à partir d'un point de départ (x, origin_y).
        """
        if direction == "down":
            y = origin_y
            while y <= self.origin["end_y"]:
                self._draw_one_point(x, y, radius, pen, brush, name)
                y += interval_y
        elif direction == "up":
            y = origin_y - interval_y
            while y >= self.origin["start_y"]:
                self._draw_one_point(x, y, radius, pen, brush, name)
                y -= interval_y

    def _draw_one_point(self, x, y, radius, pen, brush, name):
        point = self.scene.addEllipse(
            x - radius / 2,
            y - radius / 2,
            radius,
            radius,
            pen,
            brush
        )
        point.setData(1, name)


    def clear_grid_by_name(self, name: str):
        for item in self.scene.items():
            if item.data(1) == name:
                self.scene.removeItem(item)
                self.grid_name_saved.remove(name)
                break

    def clear_grid(self):
        for name in self.grid_name_saved:
            self.scene.removeItemByName(name)
        self.grid_name_saved = []

    def draw_X_axis(self, color: QColor = QColor("#FF0000"), width: int = 2, name: str = "axis",
                    x_start: float=0, y_start: float =0, axis_length: int = 200,
                    x_label: str =None, font: QFont=QFont("Arial", 8), text_rotate: int=0):
        """
        Dessine un repère avec les axes X et Y et leurs labels.

        :param font:
        :param color: Couleur des axes (rouge par défaut)
        :param width: Épaisseur des axes (2 par défaut)
        :param name: Nom identifiant le repère (pour pouvoir le supprimer plus tard)
        :param x_start:
        :param y_start:
        :param axis_length: Longueur des axes en pixels
        :param x_label: Texte pour l'axe X
        :param font:
        :param text_rotate:
        """

        x_start_pos = x_start
        y_start_pos = y_start
        x_end_pos = x_start + axis_length
        y_end_pos = y_start

        # Créer le style de ligne pour les axes
        axis_pen = QPen(color)
        axis_pen.setWidth(width)

        # Dessiner l'axe X (horizontal)
        x_axis = self.scene.addLine(x_start_pos, y_start_pos,
                                    x_end_pos, y_end_pos,
                                    axis_pen)
        x_axis.setData(1, name)

        # Ajouter les labels si demandé
        if x_label:
            # Label X
            x_text = self.scene.addText(x_label)
            x_text.setDefaultTextColor(color)
            x_text.setFont(font)
            x_text.setPos(x_end_pos, 0)
            x_text.setRotation(text_rotate)
            x_text.setData(1, name)

        # Ajouter le nom à la liste des grilles sauvegardées
        if name not in self.grid_name_saved:
            self.grid_name_saved.append(name)

    def draw_Y_axis(self, color: QColor = QColor("#FF0000"), width: int = 2, name: str = "axis",
                    x_start: float = 0, y_start: float = 0, axis_length: int = 200,
                    y_label: str = "Y", font: QFont=QFont("Arial", 8), text_rotate: int=0):
        """
        Dessine un repère avec les axes X et Y et leurs labels.

        :param color: Couleur des axes (rouge par défaut)
        :param width: Épaisseur des axes (2 par défaut)
        :param name: Nom identifiant le repère (pour pouvoir le supprimer plus tard)
        :param axis_length: Longueur des axes en pixels
        :param y_label: Texte pour l'axe Y
        :param font:
        :param text_rotate:

        """
        x_start_pos = x_start
        y_start_pos = y_start
        x_end_pos = x_start
        y_end_pos = y_start + axis_length

        # Créer le style de ligne pour les axes
        axis_pen = QPen(color)
        axis_pen.setWidth(width)

        # Dessiner l'axe X (horizontal)
        x_axis = self.scene.addLine(x_start_pos, y_start_pos,
                                    x_end_pos, y_end_pos,
                                    axis_pen)
        x_axis.setData(1, name)

        # Ajouter les labels si demandé
        if y_label:
            # Label Y
            y_text = self.scene.addText(y_label)
            y_text.setDefaultTextColor(color)
            y_text.setPos(0, y_end_pos)
            y_text.setRotation(text_rotate)
            y_text.setFont(font)
            y_text.setData(1, name)

        # Ajouter le nom à la liste des grilles sauvegardées
        if name not in self.grid_name_saved:
            self.grid_name_saved.append(name)

    def move_coordinate_system(self, name: str,
                               new_x: float=0.0, new_y: float=0.0,
                               text_offset_x: float=0.0, text_offset_y: float=0.0):
        """
        Déplace un repère existant vers une nouvelle position.

        :param name: Identifiant du repère à déplacer
        :param new_x: Nouvelle position X
        :param new_y: Nouvelle position Y
        :param text_offset_x:
        :param text_offset_y:
        """

        # Collecter tous les éléments du repère et trouver la position d'origine
        for item in self.scene.items():
            if item.data(1) == name:

                if isinstance(item, QGraphicsTextItem):

                    item.setPos(new_x + text_offset_x, new_y + text_offset_y)

                else :
                    item.setPos(new_x, new_y)







