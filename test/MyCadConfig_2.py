import sys

from PyQt6.QtWidgets import QApplication

from MainCad import MainCad


class MyWidget:
    def configure(self, maincad):
        """
        Reçoit une instance de MainCad,
        et configure la vue, la scène, les outils, etc.
        """
        view = maincad.g_get_view
        graphic_view = maincad.g_get_graphic_view
        scene = maincad.g_get_scene

        # Exemple minimal :
        view.g_scale(1, -1)
        view.g_set_scene_rectangle(-20, -20, 700, 600)
        view.g_set_background_color("#5B5B5B")

        print("Moteur initialisé !")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainCad(configurator=MyWidget(), show_ruler=True)
    window.show()
    window.resize(500, 500)
    sys.exit(app.exec())