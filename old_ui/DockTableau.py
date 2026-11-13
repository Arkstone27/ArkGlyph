from PySide6.QtWidgets import (QApplication, QDockWidget, QTableWidget,
                               QFrame, QLabel, QPushButton, QHBoxLayout,
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QMimeData, QPoint, QRect
from PySide6.QtGui import QDrag, QPixmap, QPainter

import pandas as pd

from load_icones import icone_arrow_right, icone_arrow_left

def create_fake_data():
    dico = {f"Test {i}": ["t"*j for j in range(100)] for i in range(6)}

    return pd.DataFrame.from_dict(dico)


class DockTableau(QDockWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setAllowedAreas((Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea))
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.setObjectName("DeckTableau")

        # Widgets
        self.tableau = Tableau(self)
        self.setWidget(self.tableau)

        self.titre = TitreDeck(self)
        self.setTitleBarWidget(self.titre)

        self.dockLocationChanged.connect(self.titre.new_location)

    def changer_taille(self, ouvert: bool):
        if ouvert:
            width_max = self.tableau.get_taille_max()
            self.setMaximumWidth(width_max)
            self.setMinimumWidth(width_max//self.tableau.nb_columns)
            self.tableau.show()
        else:
            self.setMaximumWidth(50)
            self.setMinimumWidth(0)
            self.tableau.hide()

class Tableau(QTableWidget):
    def __init__(self, parent=None):
        super().__init__()
        header = HeaderDrag(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(header)

        self.nb_rows, self.nb_columns = 1, 1
        self.afficher_data(create_fake_data())

    def afficher_data(self, data: pd.DataFrame):

        self.nb_rows, self.nb_columns = data.shape
        self.setRowCount(self.nb_rows)
        self.setColumnCount(self.nb_columns)

        self.setHorizontalHeaderLabels(data.keys())

        for indice_row, row in enumerate(data.itertuples()):
            for indice_column in range(self.nb_columns):
                self.setItem(indice_row, indice_column, QTableWidgetItem(str(row[indice_column])))

    def get_taille_max(self):
        taille_header = self.horizontalHeader().length()

        return taille_header + self.verticalHeader().width() + self.frameWidth()*2 + 13

class HeaderDrag(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.debut_drag = None
        self.indice_tableau = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.debut_drag = event.position().toPoint()
            self.indice_tableau = self.logicalIndexAt(self.debut_drag)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.debut_drag is None or self.indice_tableau < 0:
            return

        if not(event.buttons() & Qt.MouseButton.LeftButton):
            return

        if (event.position().toPoint() - self.debut_drag).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)

        mime_data = QMimeData()
        indice_column = str(self.indice_tableau)
        mime_data.setText(indice_column)

        drag.setMimeData(mime_data)

        # Affichage du contenu
        w = self.sectionSize(self.indice_tableau)
        h = self.height()
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)

        rectangle = QRect(self.sectionViewportPosition(self.indice_tableau), 0, w, h)

        painter = QPainter(pixmap)
        self.render(painter, QPoint(0,0), rectangle)
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint() - rectangle.topLeft()) # Point d'accroche

        drag.exec(Qt.DropAction.MoveAction)
        self.debut_drag = None

class TitreDeck(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("TitreDeck")
        self.parent = parent

        # Widgets
        self.btn_left = QPushButton()
        self.btn_left.setIcon(icone_arrow_left)
        self.btn_left.clicked.connect(self.action_left)

        self.btn_right = QPushButton()
        self.btn_right.setIcon(icone_arrow_right)
        self.btn_right.clicked.connect(self.action_right)

        self.titre = QLabel("Tableau")
        self.open = True

        # Disposition
        self.disposition = QHBoxLayout(self)

    def new_location(self, area):
        self.open = True
        self.parent.changer_taille(self.open)

        if area == Qt.DockWidgetArea.LeftDockWidgetArea:
            self.open_left()
        elif area == Qt.DockWidgetArea.RightDockWidgetArea:
            self.open_right()

    def clear(self):
        while self.disposition.count() > 0:
            item = self.disposition.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def open_left(self):
        self.clear()

        self.disposition.addStretch(1)
        self.disposition.addWidget(self.titre)
        self.disposition.addStretch(1)
        self.disposition.addWidget(self.btn_left)

    def open_right(self):
        self.clear()

        self.disposition.addWidget(self.btn_right)
        self.disposition.addStretch(1)
        self.disposition.addWidget(self.titre)
        self.disposition.addStretch(1)

    def action_left(self):
        self.open = not self.open

        if self.open:
            self.open_right()
        else:
            self.clear()
            self.disposition.addWidget(self.btn_right)
        self.parent.changer_taille(self.open)

    def action_right(self):
        self.open = not self.open

        if self.open:
            self.open_left()
        else:
            self.clear()
            self.disposition.addWidget(self.btn_left)
        self.parent.changer_taille(self.open)