from PyQt6.QtWidgets import QApplication


def mm_to_pixels(mm: float, dpi: float = 96.0) -> float:
    return mm * (get_screen_dpi()[0] / 25.4)

def pixels_to_mm(pixels: float, dpi: float = 96.0) -> float:
    return pixels * (25.4 / get_screen_dpi()[0])

def get_screen_dpi():
    screen = QApplication.primaryScreen()
    if screen:
        return screen.physicalDotsPerInchX(), screen.physicalDotsPerInchY()
    return 96.0, 96.0