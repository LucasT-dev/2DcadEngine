from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsView

from app.adapter import ScreenConverter


@dataclass
class CameraConfig:
    """Configuration de la caméra"""
    zoom_enabled: bool = True  # Activer/désactiver le zoom
    zoom_factor: float = 1.10  # Facteur de zoom par cran de molette
    min_zoom: float = 0.1  # Niveau minimum de zoom
    max_zoom: float = 10.0  # Niveau maximum de zoom
    zoom_to_cursor: bool = True  # Zoom centré sur le curseur
    pan_enabled: bool = True  # Activer/désactiver le déplacement
    smooth_zoom: bool = False  # Activer le zoom progressif


class Camera:

    def __init__(self, view: QGraphicsView):
        super().__init__()

        self.zoom_changed = None

        self.view = view

        self.config = CameraConfig()

        # État actuel de la caméra
        self._current_zoom = 1.0
        self._pan_start_pos = QPoint()
        self._is_panning = False

        # Connecter les événements de la vue
        self._setup_view()
        self.reset_view()
        #self.calibrate_scale()

    def _setup_view(self):
        """Configuration initiale de la vue"""
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse
                                        if self.config.zoom_to_cursor
                                        else QGraphicsView.ViewportAnchor.AnchorViewCenter
        )
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def calibrate_scale(self):
        """
        Calibre l'échelle de la vue pour que 1 unité de la scène = 1 mm physique.
        """
        # Récupère le DPI de l'écran
        dpi = ScreenConverter.get_screen_dpi()[0]
        pixels_per_mm = dpi / 25.4  # Nombre de pixels par mm

        # Définit une transformation pour que 1 unité de la scène = 1 mm
        transform = QTransform()
        transform.scale(pixels_per_mm, pixels_per_mm)
        self.view.setTransform(transform)

        # Met à jour le niveau de zoom actuel
        self._current_zoom = 1.0

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

        # Sauvegarder l'ancre de transformation
        old_anchor = self.view.transformationAnchor()

        if center is not None:
            self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            self.view.centerOn(center)

        # Calculer le facteur de zoom relatif
        factor = level / self._current_zoom
        self.view.scale(factor, factor)

        # Restaurer l'ancre de transformation
        if center is not None:
            self.view.setTransformationAnchor(old_anchor)

        self._current_zoom = level


    def handle_wheel(self, event) -> bool:
        """Gère l'événement de la molette de souris pour zoomer/dézoomer."""
        if not self.config.zoom_enabled:
            return False

        delta = event.angleDelta().y()
        zoom_factor = self.config.zoom_factor if delta > 0 else 1 / self.config.zoom_factor
        new_zoom = self._current_zoom * zoom_factor

        # Vérifier les limites de zoom
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

            self.view.zoom_changed.emit(self._current_zoom)
            return True

        return True

    def set_zoom(self, zoom: float):
        """
        Définit le niveau de zoom (1.0 = taille réelle).
        """
        # Récupère le DPI de l'écran
        dpi = ScreenConverter.get_screen_dpi()[0]
        pixels_per_mm = dpi / 25.4

        # Calcule la transformation pour le zoom souhaité
        transform = QTransform()
        transform.scale(zoom * pixels_per_mm, zoom * pixels_per_mm)
        self.view.setTransform(transform)

        # Met à jour le niveau de zoom actuel
        self._current_zoom = zoom

    def set_zoom_percent(self, percent: float):
        """
        Définit le niveau de zoom en pourcentage (100% = taille réelle).

        Args:
            percent: Pourcentage de zoom (ex: 100 = 100%, 200 = 200%).
        """
        if percent <= 0:
            raise ValueError("Le pourcentage de zoom doit être positif.")

        # Convertit le pourcentage en niveau de zoom
        zoom_level = percent / 100.0
        self.set_zoom(zoom_level)

    def get_zoom_percent(self) -> float:
        """
        Retourne le niveau de zoom actuel en pourcentage.
        100% = taille réelle (1:1).
        """
        return self._current_zoom * 100.0

    def handle_mouse_press(self, event) -> bool:
        """Gère l'événement de clic de souris pour le déplacement."""
        if not self.config.pan_enabled:
            return False

        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            return True

        return False

    def handle_mouse_release(self, event) -> bool:
        """Gère l'événement de relâchement du clic pour le déplacement."""
        if event.button() == Qt.MouseButton.MiddleButton and self._is_panning:
            self._is_panning = False
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            return True

        return False

    def handle_mouse_move(self, event) -> bool:
        """Gère l'événement de déplacement de la souris pour le déplacement."""
        if not self.config.pan_enabled or not self._is_panning:
            return False

        delta = event.pos() - self._pan_start_pos
        self._pan_start_pos = event.pos()

        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )

        return True




