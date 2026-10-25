from PySide6.QtWidgets import QApplication, QMainWindow

import sys

from FenetreArchive import FenetreArchive

class FenetrePrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Propriétés de la fenêtre
        self.setWindowTitle("ArchLate")
        self.setGeometry(200,200,1024,768)

        # Widgets
        self.fenetre_archive = FenetreArchive(self)
        self.setCentralWidget(self.fenetre_archive)

        self.menu_bar = self.menuBar()
        self.menu_fichier = self.menu_bar.addMenu("Fichier")



if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Style
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    fenetre_principal = FenetrePrincipal()
    fenetre_principal.show()

    app.exec()