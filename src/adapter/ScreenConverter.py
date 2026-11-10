from PyQt6.QtWidgets import QApplication


from PyQt6.QtCore import QSettings


def pixels_per_mm(widget) -> float:
    """Pixels (DIP) par mm physique, avec calibration manuelle éventuelle."""
    screen = widget.screen()
    dpr = screen.devicePixelRatio()
    # DPI physique (basé sur la taille réelle déclarée par l'écran), ramené en DIP
    dpi = screen.physicalDotsPerInchX() / dpr
    ppm = dpi / 25.4

    # Facteur de calibration utilisateur (1.0 par défaut)
    corr = float(QSettings("MonApp", "MonApp").value("screen_calibration", 1.26 )) #1.0
    return ppm * corr

def mm_to_pixels(mm: float, dpi: float = 96.0) -> float:
    return mm * (get_screen_dpi()[0] / 25.4)

def pixels_to_mm(pixels: float, dpi: float = 96.0) -> float:
    return pixels * (25.4 / get_screen_dpi()[0])

def get_screen_dpi():
    screen = QApplication.primaryScreen()
    if screen:
        return screen.physicalDotsPerInchX(), screen.physicalDotsPerInchY()
    return 96.0, 96.0