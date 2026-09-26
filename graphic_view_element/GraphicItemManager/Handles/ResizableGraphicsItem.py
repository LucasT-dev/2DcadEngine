import math
from abc import abstractmethod

from PyQt6.QtCore import QPointF, QLineF, Qt
from PyQt6.QtWidgets import QGraphicsPathItem

from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.Handle import Handle
from libs.utils.arraylist import ArrayList
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.HandleStyle import HandleStyle, DEFAULT_STYLE


class ResizableGraphicsItem:

    def __init__(self):
        self.handles = {}  # Dictionnaire pour stocker les Handles
        self._old_geometry = None  # Pour gérer l'historique des modifications
        self._frozen_items = {}
        self._group_old_positions = None

        self.snap_radius: int = 15 # rayon d'accroche des points des lignes entre elles.
        self.snap_angle_threshold : float = 1.0 # ecart d'angle d'accroche
        self.angle_allowed: list = [0, 45, 90, 135, 180, -135, -90, -45]

        # Attribut de l'item
        self.handle_style: HandleStyle = DEFAULT_STYLE
        self.snap_point_enable: bool = True
        self.item_can_be_resizable = True
        self._custom_points_of_interest: list[QPointF] = []  # coordonnées locales au groupe

        self._add_point_of_interest()

    # Dans l'item group sauvegarder la position des enfants
    # Gestion des rectangle dans un groupe étrange
    # Ajouter le handles de coté fonctionnel

    def set_handle_style(self, handle_style : HandleStyle ):
        self.handle_style = handle_style

    def add_handle(self, role: str, position: QPointF, style: HandleStyle = None, cursor: Qt.CursorShape = None):
        """Ajoute un handle à l'item, avec un style optionnel (sinon DEFAULT_STYLE)."""

        handle = Handle(self, position, role, style= style if style is None else self.handle_style,  cursor= cursor)
        self.handles[role] = handle

    def handle_moved(self, role: str, new_pos: QPointF):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def update_handles_position(self):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def handle_press(self, role: str, position: QPointF):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def handle_released(self, role: str, position: QPointF):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def select_handle(self, select: bool):
        for handle in self.handles.values():
            handle.setVisible(select)

    def _is_group_move(self) -> bool:
        """Vrai si plusieurs items sont actuellement sélectionnés dans la scène."""
        scene = self.scene()
        if not scene:
            return False
        return len(scene.selectedItems()) > 1

    def begin_move_tracking(self):
        """
        À appeler dans mousePressEvent (clic sur le corps de l'item, pas un handle).
        Capture la position de départ de TOUS les items sélectionnés si on est
        en train de démarrer un déplacement de groupe. Sinon, retombe sur le
        suivi individuel existant (save_item_geometry).
        """
        if self._is_group_move():
            self._group_old_positions = {
                item: item.pos() for item in self.scene().selectedItems()
            }
        else:
            self._group_old_positions = None
            self.save_item_geometry()

    def end_move_tracking(self):
        """
        À appeler dans mouseReleaseEvent, en pendant de begin_move_tracking.
        Pousse UNE SEULE commande pour tout le groupe si un déplacement de
        groupe était en cours, sinon retombe sur le suivi individuel existant.
        """
        from libs.cadengine.draw.HistoryManager import MoveItemsCommand

        if self._group_old_positions:
            changed = {
                item: (old_pos, item.pos())
                for item, old_pos in self._group_old_positions.items()
                if old_pos != item.pos()
            }
            if changed:
                cmd = MoveItemsCommand(changed, description="move items")
                self.scene().undo_stack.push(cmd)

            self._group_old_positions = None
        else:
            self.save_history_geometry()

    def save_item_geometry(self):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def save_history_geometry(self):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def update_handles_size(self, zoom_level: float):
        """Redimensionne tous les handles selon le zoom."""
        for handle in self.handles.values():
            handle.update_size(zoom_level)

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'GraphicElementObject' :
        pass

    @abstractmethod
    def get_point_of_interest(self) -> list[QPointF]:
        """
        Implémentation par défaut : aucun point d'intérêt. Les sous-classes
        doivent la surcharger pour participer au snapping.*
        returne une liste de point de la scene
        """
        return []

    @abstractmethod
    def _add_point_of_interest(self):
        pass

    @abstractmethod
    def _update_point_of_interest(self):
        pass

    @abstractmethod
    def get_line_of_interest(self) -> list[QLineF]:
        """
        Par défaut : aucune ligne d'intérêt
        """
        return []

    def get_snap_is_enable(self) -> bool :
        return self.snap_point_enable

    def set_snap_enable(self, snap:bool) :
        self.snap_point_enable = snap


    def get_snap_radius(self) -> int:
        return self.snap_radius

    def set_snap_radius(self, radius: int):
        self.snap_radius = radius


    def get_item_is_resizable(self) -> bool:
        return self.item_can_be_resizable

    def set_item_can_be_resizable(self, is_resizable:bool):
        self.item_can_be_resizable = is_resizable



    def add_point_of_interest(self, local_point: QPointF):
        self._custom_points_of_interest.append(local_point)

    def replace_point_of_interest(self, local_point: QPointF, index: int):
        self._custom_points_of_interest[index] = local_point

    def clear_point_of_interest(self):
        self._custom_points_of_interest.clear()

    def len_points_of_interest(self) -> int:
        return len(self._custom_points_of_interest)

    def get_points_of_interest_local(self) -> list[QPointF]:
        """Retourne les points en coordonnées locales, utile pour"""
        return list(self._custom_points_of_interest)

    # Optimisation des calculs de snap des points/lignes
    def _begin_resize(self, item_moved):
        """À appeler une seule fois quand le drag/resize démarre"""
        self._snap_cache_dirty = True
        self._cached_static_points = None
        self._cached_static_lines = None
        self._cached_static_intersections = None

    def _end_resize(self):
        self._cached_static_points = None
        self._cached_static_lines = None
        self._cached_static_intersections = None
        self._snap_cache_dirty = True

    def _rebuild_static_cache(self, scene, item_moved):
        """Recalcule les points/lignes/intersections des items statiques"""
        static_points = ArrayList()
        static_lines: list[QLineF] = []

        for item in scene.items():
            if item is item_moved:
                continue
            if item_moved is not None and item.parentItem() is item_moved:
                continue
            if isinstance(item, Handle):
                continue

            if hasattr(item, "get_point_of_interest"):
                for point in item.get_point_of_interest():
                    static_points.add(point)

            if hasattr(item, "get_line_of_interest"):
                static_lines.extend(item.get_line_of_interest())

        # Intersections item statique x item statique : calculées une fois
        static_intersections = ArrayList()
        for i in range(len(static_lines)):
            for j in range(i + 1, len(static_lines)):
                intersect_type, point = static_lines[i].intersects(static_lines[j])
                if intersect_type != QLineF.IntersectionType.NoIntersection:
                    static_intersections.add(point)

        self._cached_static_points = static_points
        self._cached_static_lines = static_lines
        self._cached_static_intersections = static_intersections
        self._snap_cache_dirty = False

    def _find_snap_point(self, scene, scene_pos: QPointF, item_moved=None, exclude_point_index: int = None) -> QPointF | None:
        """
        :param scene:
        :param scene_pos:
        :param item_moved:
        :param exclude_point_index: Utiliser pour les PathLine, permettant de snap les autres points
        :return:
        """
        if not scene:
            return None

        best_point = None
        best_dist = self.get_snap_radius()

        candidates = ArrayList()

        moved_lines: list[QLineF] = []

        if self._snap_cache_dirty or self._cached_static_lines is None:
            self._rebuild_static_cache(scene, item_moved)

        broad_radius = best_dist * 2

        def add_segment_projection(a: QPointF, b: QPointF):
            proj = self._closest_point_on_segment(scene_pos, a, b)
            if (scene_pos - proj).manhattanLength() <= best_dist:
                candidates.add(proj)

        # item en mouvement recalculé à chaque frame
        if item_moved is not None:
            if hasattr(item_moved, "get_line_of_interest"):
                moved_lines.extend(item_moved.get_line_of_interest())



         # l'item en movement
        if item_moved is not None:

            if hasattr(item_moved, "get_line_of_interest"):
                moved_lines.extend(item_moved.get_line_of_interest())

            if isinstance(item_moved, QGraphicsPathItem) and hasattr(item_moved, "get_anchor_points_scene"):
                anchor_points = item_moved.get_anchor_points_scene()

                for i, point in enumerate(anchor_points):
                    if exclude_point_index is not None and i == exclude_point_index:
                        continue
                    candidates.add(point)

                for i in range(len(anchor_points) - 1):
                    if exclude_point_index is not None and exclude_point_index in (i, i + 1):
                        continue  # évite un milieu/segment impliquant le point déplacé
                    a = anchor_points[i]
                    b = anchor_points[i + 1]
                    candidates.add(QPointF((a.x() + b.x()) / 2, (a.y() + b.y()) / 2))
                    add_segment_projection(a, b)

            # --- points statiques : filtrage spatial seulement (pas de recalcul métier) ---
        for point in self._cached_static_points:
            if (scene_pos - point).manhattanLength() <= broad_radius:
                candidates.add(point)

            # --- intersections statique x statique : déjà calculées, juste filtrées par distance ---
        for point in self._cached_static_intersections:
            if (scene_pos - point).manhattanLength() <= best_dist:
                candidates.add(point)

            # --- intersections item déplacé x items statiques : seule chose recalculée à chaque frame ---
        for moved_line in moved_lines:
            for line in self._cached_static_lines:
                intersect_type, point = moved_line.intersects(line)
                if intersect_type == QLineF.IntersectionType.NoIntersection:
                    continue
                if (scene_pos - point).manhattanLength() <= best_dist:
                    candidates.add(point)

        for candidate in candidates:
            dist = (scene_pos - candidate).manhattanLength()
            if dist < best_dist:
                best_dist = dist
                best_point = candidate

        return best_point


    @staticmethod
    def _closest_point_on_segment(p: QPointF, a: QPointF, b: QPointF) -> QPointF:
        """Point du segment [a, b] le plus proche de p (projection orthogonale bornée)."""
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        px, py = p.x(), p.y()

        dx = bx - ax
        dy = by - ay

        length_sq = dx * dx + dy * dy
        if length_sq < 1e-9:
            return a  # segment dégénéré (a == b)

        t = ((px - ax) * dx + (py - ay) * dy) / length_sq
        t = max(0.0, min(1.0, t))  # borne au segment, pas la droite infinie

        return QPointF(ax + t * dx, ay + t * dy)

    def _find_angle_auto(self, fixed_points: QPointF | list[QPointF], scene_pos: QPointF,
                         angle_threshold: float = 5.0) -> QPointF | None:
        """
        Retourne un point contraint si l'angle (fixed -> scene_pos) est proche
        de 0°, 45°, 90°, 135°... pour au moins un des points fixes fournis.

        'fixed_points' peut être un QPointF unique (rétrocompatible) ou une
        liste de QPointF (ex: sommet précédent ET suivant d'une polyligne).
        Si plusieurs points fixes matchent, celui dont l'angle est le plus
        proche d'un angle contraint est retenu.
        """
        if isinstance(fixed_points, QPointF):
            fixed_points = [fixed_points]

        best_point = None
        best_deviation = angle_threshold

        for fixed in fixed_points:
            dx = scene_pos.x() - fixed.x()
            dy = scene_pos.y() - fixed.y()

            length = math.sqrt(dx * dx + dy * dy)
            if length < 1e-6:
                continue

            angle = math.degrees(math.atan2(dy, dx))
            closest = min(self.angle_allowed, key=lambda a: abs(angle - a))
            deviation = abs(angle - closest)

            if deviation <= best_deviation:
                best_deviation = deviation
                rad = math.radians(closest)
                best_point = QPointF(
                    fixed.x() + length * math.cos(rad),
                    fixed.y() + length * math.sin(rad)
                )

        return best_point

    def _closest_allowed_direction(self, fixed: QPointF, scene_pos: QPointF,
                                   angle_threshold: float) -> QPointF | None:
        """
        Renvoie un vecteur unitaire correspondant à l'angle autorisé le plus
        proche de la direction (fixed -> scene_pos), ou None si hors tolérance.
        """
        dx = scene_pos.x() - fixed.x()
        dy = scene_pos.y() - fixed.y()

        length = math.sqrt(dx * dx + dy * dy)
        if length < 1e-6:
            return None

        angle = math.degrees(math.atan2(dy, dx))
        closest = min(self.angle_allowed, key=lambda a: abs(angle - a))

        if abs(angle - closest) > angle_threshold:
            return None

        rad = math.radians(closest)
        return QPointF(math.cos(rad), math.sin(rad))

    def _find_corner_snap(self, fixed_a: QPointF, fixed_b: QPointF, scene_pos: QPointF,
                          angle_threshold: float = 5.0) -> QPointF | None:
        """
        Si les directions (fixed_a -> scene_pos) ET (fixed_b -> scene_pos)
        peuvent chacune s'aligner sur un angle autorisé, renvoie le point
        d'intersection des deux droites contraintes (coin exact).
        Renvoie None si l'une des deux directions n'est pas snappable, ou si
        les deux droites sont parallèles (pas d'intersection).
        """
        dir_a = self._closest_allowed_direction(fixed_a, scene_pos, angle_threshold)
        dir_b = self._closest_allowed_direction(fixed_b, scene_pos, angle_threshold)

        if dir_a is None or dir_b is None:
            return None

        # Droites "infinies" construites à partir des points fixes
        reach = 1_000_000.0
        line_a = QLineF(fixed_a, fixed_a + dir_a * reach)
        line_b = QLineF(fixed_b, fixed_b + dir_b * reach)

        intersect_type, point = line_a.intersects(line_b)

        if intersect_type == QLineF.IntersectionType.NoIntersection:
            return None  # droites parallèles

        return point





