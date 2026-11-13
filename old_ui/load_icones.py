from PySide6.QtGui import QIcon, QPainter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtSvg import QSvgRenderer

icone_cross = QIcon("icones/cross.svg")
icone_arrow_left = QIcon("icones/arrow-left.svg")
icone_arrow_right = QIcon("icones/arrow-right.svg")

class SvgWidget(QWidget):
    def __init__(self, chemin_svg, taille, parent=None):
        super().__init__(parent)

        self.rendu = QSvgRenderer(chemin_svg, self)
        self.rendu.setAspectRatioMode(Qt.KeepAspectRatio)
        self.rendu.repaintNeeded.connect(self.update)

        self.setFixedSize(taille, taille)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.rendu.render(painter, self.rect())
        painter.end()

    def sizeHint(self):
        return self.rendu.defaultSize()