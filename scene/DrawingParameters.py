from PyQt6.QtCore import Qt


class DrawingParameters:
    def __init__(self):
        # Couleurs par défaut (R, G, B, A)
        self.fill_color = (0, 0, 0, 255)  # Noir opaque
        self.border_color = (0, 0, 0, 255)  # Noir opaque

        self.border_width = 2

        self.line_style = Qt.PenStyle.SolidLine
        self.cap_style = Qt.PenCapStyle.RoundCap
        self.join_style = Qt.PenJoinStyle.RoundJoin
