from PySide6.QtWidgets import QGridLayout, QSpinBox, QGraphicsScene, QGraphicsView, QTableWidget, QPushButton, QWidget
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QCursor

import pandas as pd

from traitement_style import icones
from Lot import Lot

def create_fake_data():
    dico = {f"Test {i}": ["t"*j for j in range(100)] for i in range(6)}

    return pd.DataFrame.from_dict(dico)

class VueScene(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Widgets
        self.spin_box = SpinBoxPages()
        self.spin_box.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.btn_tableau = QPushButton()
        self.btn_tableau.setIcon(icones["table"])
        self.btn_tableau.setIconSize(QSize(20,20))
        self.btn_tableau.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Disposition
        self.disposition = QGridLayout(self)

        self.disposition.setRowStretch(0, 0)
        self.disposition.setRowStretch(1, 1)
        self.disposition.setRowStretch(2, 0)

        self.disposition.setColumnStretch(0, 1)
        self.disposition.setColumnStretch(1, 0)
        self.disposition.setColumnStretch(2, 1)

        self.disposition.addWidget(self.spin_box, 2, 1)
        self.disposition.addWidget(self.btn_tableau, 0, 2, Qt.AlignmentFlag.AlignRight)

    def update_lot(self, lot):
        self.spin_box.update_lot(lot)

class SpinBoxPages(QSpinBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_lot(self, lot: Lot):
        self.setSuffix(f"/{lot.nb_pages}")
        self.setRange(1, lot.nb_pages)

class SceneLot(QGraphicsScene): 
    def __init__(self, lot: Lot):
        super().__init__()

        # Variables
        self.lot = lot
        self.data = create_fake_data()


class Tableau(QTableWidget):
    def __init__(self):
        super().__init__()
