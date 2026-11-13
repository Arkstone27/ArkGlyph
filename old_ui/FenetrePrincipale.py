from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt

import sys

from FenetreArchive import FenetreArchive
from DockProgress import DockProgress, gestion_processus
from DockTableau import DockTableau

class FenetrePrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Propriétés de la fenêtre
        self.setWindowTitle("ArchLate")
        self.setGeometry(200,200,1024,768)

        # Widgets
        self.fenetre_archive = FenetreArchive(self)
        self.setCentralWidget(self.fenetre_archive)

        self.dock_progress = DockProgress(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_progress)

        self.dock_tableau = DockTableau(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_tableau)

        self.menu_bar = self.menuBar()
        self.menu_fichier = self.menu_bar.addMenu("Fichier")

        # Thread Pool
        gestion_processus.set_Fenetres(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Style
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    fenetre_principal = FenetrePrincipal()
    fenetre_principal.show()

    app.exec()