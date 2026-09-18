import os
from contextlib import contextmanager, nullcontext

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QImage, QPageLayout, QPageSize, QColor, QBrush, QPen
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtSvg import QSvgGenerator

from libs.cadengine.exception.ImportExportExceptions import ExportError
from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.Handle import Handle


def _is_background_light(background: Qt.GlobalColor | QColor, luminance_threshold: float = 0.6) -> bool:
    """
    Détermine si le fond est suffisamment clair pour justifier l'inversion
    des items (sinon ils deviendraient invisibles sur le fond).
    Un fond transparent (alpha=0) est considéré comme non concerné :
    aucune inversion, car il n'y a pas de "couleur de fond" à opposer.

    Utilise la luminance relative perçue (formule standard ITU-R BT.601).
    """
    color = QColor(background)

    if color.alpha() == 0:
        return False  # fond transparent : pas d'inversion, laisse les items tels quels

    luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255.0

    return luminance >= luminance_threshold

class ExportSceneManager:

    def __init__(self, view):
        """
        :param view: la GraphicView (QGraphicsView) associée.
        """
        self.view = view

    @property
    def scene(self):
        return self.view.scene()

    def _validate_output_path(self, path: str) -> None:
        """
        Vérifie que le chemin de sortie est utilisable avant de lancer l'export.
        Lève une exception claire plutôt que de laisser Qt échouer silencieusement
        (fichier vide ou non créé, sans message d'erreur exploitable).
        """
        if not path:
            raise ValueError("Le chemin de destination est vide.")

        directory = os.path.dirname(path) or "."

        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Le dossier de destination n'existe pas : '{directory}'")

        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Pas de droit d'écriture dans le dossier : '{directory}'")

        # Si le fichier existe déjà, vérifie qu'on peut bien l'écraser
        if os.path.exists(path) and not os.access(path, os.W_OK):
            raise PermissionError(f"Le fichier existe déjà et n'est pas modifiable : '{path}'")

    def export_svg(self, path: str, size: tuple[int, int] = None,
                   render_rect: QRectF = None,
                   flip_y: bool = True,
                   margin_ratio: float = 0.02) -> None:
        """
        Exporte la scène ou une zone donnée au format SVG.
        """
        self._validate_output_path(path)

        try:
            if render_rect is None:
                render_rect = self.scene.itemsBoundingRect()

                if render_rect.isEmpty():
                    render_rect = self.scene.sceneRect()

                margin_x = render_rect.width() * margin_ratio
                margin_y = render_rect.height() * margin_ratio
                render_rect = render_rect.adjusted(-margin_x, -margin_y, margin_x, margin_y)

            generator = QSvgGenerator()
            generator.setFileName(path)

            target_size = size if size else render_rect.size().toSize()
            generator.setSize(target_size)
            generator.setViewBox(QRectF(0, 0, target_size.width(), target_size.height()))
            generator.setTitle("CAD Engine")
            generator.setDescription("Generate by CAD Engine")

            painter = QPainter(generator)
            try:
                if flip_y:
                    painter.translate(0, target_size.height())
                    painter.scale(1, -1)

                target_rect = QRectF(0, 0, target_size.width(), target_size.height())
                self.scene.render(painter, target=target_rect, source=render_rect)
            finally:
                painter.end()

            if not os.path.exists(path) or os.path.getsize(path) == 0:
                raise IOError("Le fichier SVG généré est vide ou n'a pas été créé.")

        except Exception as e:
            raise ExportError(path, e) from e

    def export_pdf(self, pathfile: str, render_rect: QRectF = None,
                   page_size=QPageSize.PageSizeId.A4,
                   orientation=QPageLayout.Orientation.Portrait,
                   flip_y: bool = True,
                   margin_ratio: float = 0.02,
                   invert_white_object = True
                   ):

        self._validate_output_path(pathfile)

        try:
            if render_rect is None:
                render_rect = self.scene.itemsBoundingRect()

                if render_rect.isEmpty():
                    render_rect = self.scene.sceneRect()

                margin_x = render_rect.width() * margin_ratio
                margin_y = render_rect.height() * margin_ratio
                render_rect = render_rect.adjusted(-margin_x, -margin_y, margin_x, margin_y)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFileName(pathfile)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setPageSize(QPageSize(page_size))
            printer.setPageOrientation(orientation)
            printer.setFullPage(True)

            target_rect = QRectF(printer.pageRect(QPrinter.Unit.DevicePixel))

            context = self._temporarily_invert_white_items() if invert_white_object else nullcontext()

            with context:
                painter = QPainter(printer)
                try:
                    if flip_y:
                        painter.translate(0, target_rect.height())
                        painter.scale(1, -1)

                    self.scene.render(painter, target=target_rect, source=render_rect)
                finally:
                    painter.end()

            if not os.path.exists(pathfile) or os.path.getsize(pathfile) == 0:
                raise IOError("Le fichier PDF généré est vide ou n'a pas été créé.")

        except Exception as e:
            raise ExportError(pathfile, e) from e

    def export_png(self, path: str, size: tuple[int, int] = None,
                   render_rect: QRectF = None,
                   flip_y: bool = True,
                   margin_ratio: float = 0.02,
                   background: Qt.GlobalColor = Qt.GlobalColor.white,
                   invert_white_object: bool = True) -> None:

        self._validate_output_path(path)

        try:
            if render_rect is None:
                render_rect = self.scene.itemsBoundingRect()

                if render_rect.isEmpty():
                    render_rect = self.scene.sceneRect()

                margin_x = render_rect.width() * margin_ratio
                margin_y = render_rect.height() * margin_ratio
                render_rect = render_rect.adjusted(-margin_x, -margin_y, margin_x, margin_y)

            image_size = size if size else render_rect.size().toSize()

            image = QImage(image_size, QImage.Format.Format_ARGB32)
            image.fill(background)

            should_invert = invert_white_object and _is_background_light(background)

            context = self._temporarily_invert_white_items() if should_invert else nullcontext()

            with context:
                painter = QPainter(image)
                try:
                    if flip_y:
                        painter.translate(0, image_size.height())
                        painter.scale(1, -1)

                    target_rect = QRectF(0, 0, image_size.width(), image_size.height())
                    self.scene.render(painter, target=target_rect, source=render_rect)
                finally:
                    painter.end()

            if not image.save(path, "PNG"):
                raise IOError(f"QImage.save a échoué pour '{path}'")

        except Exception as e:
            raise ExportError(path, e) from e



    @contextmanager
    def _temporarily_invert_white_items(self, threshold: int = 250):
        """
        Parcourt tous les items de la scène et remplace temporairement le
        pen/brush blanc (ou proche du blanc) par du noir.
        Restaure les couleurs d'origine à la fin.

        'threshold' : luminosité minimale (0-255 par canal RGB) à partir de
        laquelle une couleur est considérée comme blanche à inverser.
        """
        saved_states = []  # [(item, old_pen, old_brush)]

        def is_near_white(color: QColor) -> bool:
            return color.red() >= threshold and color.green() >= threshold and color.blue() >= threshold and color.alpha() > 0

        for item in self.scene.items():
            if isinstance(item, Handle):
                continue

            has_pen = hasattr(item, "pen") and hasattr(item, "setPen")
            has_brush = hasattr(item, "brush") and hasattr(item, "setBrush")

            if not has_pen and not has_brush:
                continue

            old_pen = item.pen() if has_pen else None
            old_brush = item.brush() if has_brush else None

            changed = False

            if has_pen and is_near_white(old_pen.color()):
                new_pen = QPen(old_pen)
                new_pen.setColor(QColor(0, 0, 0, old_pen.color().alpha()))
                item.setPen(new_pen)
                changed = True

            if has_brush and old_brush.style() != Qt.BrushStyle.NoBrush and is_near_white(old_brush.color()):
                new_brush = QBrush(old_brush)
                new_brush.setColor(QColor(0, 0, 0, old_brush.color().alpha()))
                item.setBrush(new_brush)
                changed = True

            if changed:
                saved_states.append((item, old_pen, old_brush, has_pen, has_brush))

        try:
            yield
        finally:
            for item, old_pen, old_brush, has_pen, has_brush in saved_states:
                if has_pen:
                    item.setPen(old_pen)
                if has_brush:
                    item.setBrush(old_brush)
