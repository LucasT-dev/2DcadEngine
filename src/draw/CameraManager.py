from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsView

from adapter import ScreenConverter


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

        self._base_scale = None
        self.view = view

        self.config = CameraConfig()

        # État actuel de la caméra
        self._current_zoom = 1.0
        self._pan_start_pos = QPoint()
        self._is_panning = False

        # Connecter les événements de la vue
        self._setup_view()
        self.reset_view()
        self.calibrate_scale()

        self.zoom_changed = None

    def _setup_view(self):
        """Configuration initiale de la vue"""
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse
                                        if self.config.zoom_to_cursor
                                        else QGraphicsView.ViewportAnchor.AnchorViewCenter
        )
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


    def _ppm(self) -> float:
        return ScreenConverter.pixels_per_mm(self.view)

    def calibrate_scale(self):
        self._base_scale = self._ppm()
        self.view.setTransform(QTransform.fromScale(self._base_scale, self._base_scale))
        self._emit_zoom()

    def _apply_zoom_factor(self, factor: float):
        self.view.scale(factor, factor)
        self._emit_zoom()

    def reset_view(self):
        self.calibrate_scale()  # au lieu de QTransform()

    def set_zoom(self, zoom: float):
        zoom = max(self.config.min_zoom, min(self.config.max_zoom, zoom))
        base = self._ppm()
        self._base_scale = base
        self.view.setTransform(QTransform.fromScale(zoom * base, zoom * base))
        self._emit_zoom()

    def get_current_zoom(self) -> float:
        base = getattr(self, "_base_scale", 0) or 1.0
        return self.view.transform().m11() / base

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
        if not self.config.zoom_enabled:
            return False

        step = self.config.zoom_factor if event.angleDelta().y() > 0 else 1 / self.config.zoom_factor
        current = self.get_current_zoom()
        new_zoom = max(self.config.min_zoom, min(self.config.max_zoom, current * step))
        real_factor = new_zoom / current

        if abs(real_factor - 1) > 1e-9:
            self._apply_zoom_factor(real_factor)
        return True

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
        return self.get_current_zoom() * 100.0

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

    def _emit_zoom(self):
        """Émet la valeur réelle, lue depuis la transformation (jamais en retard)."""
        z = self.get_current_zoom()
        self.view.zoom_changed.emit(z)
        self.view.zoom_percent_changed.emit(z * 100.0)


