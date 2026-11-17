from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QFrame

import sys

from interface.SideBarOutils import SideBarOutils
from interface.FrameCentre import FrameCentre
from interface.WidgetNotifs import WidgetNotifs

from interface.traitement_style import application_palette, chargement_fonts
from interface.gestion_processus import gestion_processus

class FenetrePrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Propriétés de la fenêtre
        self.setWindowTitle("ArchLate")
        self.setGeometry(200,200,1024,768)
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # On retire les bords

        self.frame_all = QFrame(self)

        self.sidebar_outils = SideBarOutils(self)
        self.frame_centre = FrameCentre(self)
        gestion_processus.set_widgets(self)
        
        # Disposition
        self.disposition = QHBoxLayout(self.frame_all)
        self.disposition.setContentsMargins(0,0,0,0)

        self.disposition.addWidget(self.sidebar_outils)
        self.disposition.addWidget(self.frame_centre)

        self.setCentralWidget(self.frame_all)

    def maximizer(self):
        self.showMaximized()
        if not self.sidebar_outils.visible:
            self.sidebar_outils.switch_visible()


def chargement_app():
    app = QApplication(sys.argv)

    # Style
    chargement_fonts()
    application_palette()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    fenetre_principal = FenetrePrincipal()
    fenetre_principal.show()

    sys.exit(app.exec())
