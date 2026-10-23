from PySide6.QtWidgets import QApplication, QMainWindow

from PySide6.QtGui import QPalette, QColor

import sys

from FenetreArchive import FenetreArchive

class FenetrePrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Propriétés de la fenêtre
        self.setWindowTitle("ArchLate")
        self.setGeometry(200,200,1024,768)

        # Style (temporaire)
        palette = QPalette()
        palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.WindowText, QColor(0,248,255))

        self.setPalette(palette)

        # Widgets
        self.fenetre_archive = FenetreArchive(self)
        self.setCentralWidget(self.fenetre_archive)

        self.menu_bar = self.menuBar()
        self.menu_fichier = self.menu_bar.addMenu("Fichier")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fenetre_principal = FenetrePrincipal()
    fenetre_principal.show()

    app.exec()