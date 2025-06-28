from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsView


@dataclass
class CameraConfig:
    """Configuration de la caméra"""
    zoom_enabled: bool = True  # Activer/désactiver le zoom
    zoom_factor: float = 1.15  # Facteur de zoom par cran de molette
    min_zoom: float = 0.1  # Niveau minimum de zoom
    max_zoom: float = 10.0  # Niveau maximum de zoom
    zoom_to_cursor: bool = True  # Zoom centré sur le curseur
    pan_enabled: bool = True  # Activer/désactiver le déplacement
    smooth_zoom: bool = True  # Activer le zoom progressif


class Camera:

    def __init__(self, view):
        super().__init__()

        self._calibrated_dpi = None
        self.view = view

        self.config = CameraConfig()

        # État actuel de la caméra
        self._current_zoom = 1.0
        self._pan_start_pos = QPoint()
        self._is_panning = False

        # Connecter les événements de la vue
        self._setup_view()

    def _setup_view(self):
        """Configuration initiale de la vue"""
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse
                                        if self.config.zoom_to_cursor
                                        else QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def set_zoom_enabled(self, enabled: bool):
        """Activer/désactiver le zoom"""
        self.config.zoom_enabled = enabled

    def set_pan_enabled(self, enabled: bool):
        """Activer/désactiver le déplacement"""
        self.config.pan_enabled = enabled

    def set_zoom_to_cursor(self, enabled: bool):
        """Activer/désactiver le zoom centré sur le curseur"""
        self.config.zoom_to_cursor = enabled
        self.view.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse if enabled
            else QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

    def set_zoom_limits(self, min_zoom: float, max_zoom: float):
        """Définir les limites de zoom"""
        self.config.min_zoom = max(0.01, min_zoom)
        self.config.max_zoom = max(min_zoom, max_zoom)

    def set_zoom_factor(self, factor: float):
        """Définir le facteur de zoom"""
        self.config.zoom_factor = max(1.01, factor)

    def reset_view(self):
        """Réinitialiser la vue"""
        self.view.setTransform(QTransform())
        self._current_zoom = 1.0

    def get_current_zoom(self) -> float:
        """Obtenir le niveau de zoom actuel"""
        return self._current_zoom

    def zoom_to(self, level: float, center: QPointF = None):
        """Zoomer à un niveau spécifique"""
        if not self.config.zoom_enabled:
            return

        # Limiter le niveau de zoom
        level = max(self.config.min_zoom, min(self.config.max_zoom, level))

        # Calculer le facteur de zoom relatif
        factor = level / self._current_zoom

        if center is not None:
            # Sauvegarder l'ancre de transformation
            old_anchor = self.view.transformationAnchor()
            self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

            # Centrer sur le point spécifié
            self.view.centerOn(center)

            # Appliquer le zoom
            self.view.scale(factor, factor)

            # Restaurer l'ancre de transformation
            self.view.setTransformationAnchor(old_anchor)
        else:
            # Zoom normal
            self.view.scale(factor, factor)

        self._current_zoom = level

    def handle_wheel(self, event) -> bool:
        """Gérer l'événement de la molette de souris"""
        if not self.config.zoom_enabled:
            return False

        # Calculer le facteur de zoom
        delta = event.angleDelta().y()
        zoom_factor = self.config.zoom_factor if delta > 0 else 1 / self.config.zoom_factor

        # Calculer le nouveau niveau de zoom
        new_zoom = self._current_zoom * zoom_factor

        # Vérifier les limites
        if self.config.min_zoom <= new_zoom <= self.config.max_zoom:
            if self.config.smooth_zoom:
                # Zoom progressif
                steps = 5
                factor = pow(zoom_factor, 1/steps)
                for _ in range(steps):
                    self.view.scale(factor, factor)
            else:
                # Zoom direct
                self.view.scale(zoom_factor, zoom_factor)

            self._current_zoom = new_zoom
            return True

        return False

    def auto_calibrate_dpi_from_scene(self, mm_in_scene=100.0):
        """
        Affiche une ligne horizontale dans la scène et mesure sa taille en pixels
        pour estimer la résolution physique (DPI) de l'écran.
        """
        start = self.view.mapFromScene(0, 0)
        end = self.view.mapFromScene(mm_in_scene, 0)
        pixels = abs(end.x() - start.x())

        # Calcul du DPI estimé (pixels par mm * 25.4)
        if pixels == 0:
            raise ValueError("La scène n'est pas visible ou trop zoomée.")

        pixels_per_mm = pixels / mm_in_scene
        self._calibrated_dpi = pixels_per_mm * 26.45 #25.40

        #self._calibrated_dpi = 30

        return self._calibrated_dpi

    def set_zoom_percent(self, percent: float):
        """
        Définit un zoom basé sur une échelle réelle (100% = 1 mm scène = 1 mm physique).
        """
        if percent <= 0:
            raise ValueError("Zoom percent must be positive")

        dpi = getattr(self, "_calibrated_dpi", self.view.logicalDpiX())
        pixels_per_mm = dpi / self._calibrated_dpi

        target_scale = pixels_per_mm * (percent / 100.0)
        self.zoom_to(target_scale)

    def get_zoom_percent(self) -> float:
        """
        Retourne le pourcentage de zoom courant, où 100% = échelle physique réelle.
        """
        # Facteur de transformation : combien de pixels pour 1 unité scène
        pixels_per_scene_unit = self.view.transform().m11()

        # DPI calibré ou valeur estimée par défaut
        dpi = getattr(self, "_calibrated_dpi", self.view.logicalDpiX())

        # Combien de pixels devraient représenter 1 mm en affichage physique
        pixels_per_mm_real = dpi / 25.4

        # À 100%, on veut 1 unité scène = 1 mm physique
        # Donc pixels_per_scene_unit doit égaler pixels_per_mm_real
        percent = (pixels_per_scene_unit / pixels_per_mm_real) * 100.0

        return percent

    def handle_mouse_press(self, event) -> bool:
        """Gérer l'événement de clic de souris"""
        if not self.config.pan_enabled:
            return False

        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            return True

        return False

    def handle_mouse_release(self, event) -> bool:
        """Gérer l'événement de relâchement du clic"""
        if event.button() == Qt.MouseButton.MiddleButton and self._is_panning:
            self._is_panning = False
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            return True

        return False

    def handle_mouse_move(self, event) -> bool:
        """Gérer l'événement de déplacement de la souris"""
        if not self.config.pan_enabled or not self._is_panning:
            return False

        # Calculer le déplacement
        delta = event.pos() - self._pan_start_pos
        self._pan_start_pos = event.pos()

        # Déplacer la vue
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )

        return True




