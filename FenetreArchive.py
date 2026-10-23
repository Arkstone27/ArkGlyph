from PySide6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsScene, QGraphicsView, QPushButton, QSpinBox, QTabBar, QComboBox, QLineEdit)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from time import time
from Lot import Lot, get_lots_saved
from download_lot import is_valide, download_lot

class FenetreArchive(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        # Gestion des Lots
        self.chemins_lots, self.noms_lots = get_lots_saved()

        # Widgets
        self.tabs = QTabWidget(self, tabsClosable=True)
        self.onglets_lots = dict()

        self.onglet_ajout = OngletAjoutLot(self)
        self.tabs.addTab(self.onglet_ajout, "+")
        self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None) # Retire la croix de fermeture

        # Disposition
        self.disposition = QVBoxLayout(self)
        self.disposition.addWidget(self.tabs)

    def ajout_lot(self, indice_lot):
        if len(self.chemins_lots) == 0:
            return

        chemin_lot = self.chemins_lots[indice_lot]
        lot = Lot(chemin_lot)
        if lot.nom in self.onglets_lots:
            self.tabs.setCurrentIndex(self.onglets_lots[lot.nom].indice_position)
            return

        onglet_lot = OngletLot(lot, len(self.onglets_lots), self)

        self.onglets_lots[lot.nom] = onglet_lot
        self.tabs.insertTab(self.tabs.count() - 1, onglet_lot, lot.nom)
        self.tabs.setCurrentIndex(self.tabs.count() - 2)

class OngletLot(QGraphicsView):
    def __init__(self, lot, indice_position, parent=None):
        super().__init__()
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.indice_position = indice_position

        # Lot
        self.lot = lot
        self.indice_page = 0

        # Scene
        self.scene = QGraphicsScene()

        self.page = QPixmap(self.lot.chemins_pages[self.indice_page].resolve())
        self.page_item = self.scene.addPixmap(self.page)
        self.changer_page(self.indice_page)

        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.afficher_page_entiere()

        self.taille_max = self.transform().m11()
        self.last_zoom = time()

        # SpinBox
        self.spin_box = SpinBoxPages(self.lot, parent=self)
        self.spin_box.valueChanged.connect(lambda indice: self.changer_page(indice - 1))

        self.disposition_v = QVBoxLayout(self)
        self.disposition_v.addStretch(1)

        self.disposition_h = QHBoxLayout(self)

        self.disposition_h.addStretch(1)
        self.disposition_h.addWidget(self.spin_box)
        self.disposition_h.addStretch(1)

        self.disposition_v.addLayout(self.disposition_h)

    def afficher_page_entiere(self):
        rectangle = self.scene.itemsBoundingRect() # Recupere le rectangle englobant tous les elements (le plus gros etant la page)

        if not rectangle.isNull():
            self.fitInView(rectangle, Qt.AspectRatioMode.KeepAspectRatio) # Conserve le ratio de la page

            self.taille_max = self.transform().m11()

    def changer_page(self, new_indice: int):
        self.indice_page = new_indice
        self.page = QPixmap(self.lot.chemins_pages[self.indice_page].resolve())

        self.page_item.setPixmap(self.page)

    def resizeEvent(self, event):
        if (time() - self.last_zoom) > 0.1:
            self.afficher_page_entiere()

    def wheelEvent(self, event):# On réécrit les choses à faire avec la molette
        facteur_zoom = 1.15
        self.last_zoom = time()

        if event.angleDelta().y() > 0:
            self.scale(facteur_zoom, facteur_zoom)
        elif self.transform().m11() > self.taille_max*facteur_zoom:
            self.scale(1/facteur_zoom, 1/facteur_zoom)

class SpinBoxPages(QSpinBox):
    def __init__(self, lot: Lot, parent=None):
        super().__init__()

        # Widget
        self.setSuffix(f"/{lot.nb_pages}")
        self.setRange(1, lot.nb_pages)

class OngletAjoutLot(QWidget):
    def __init__(self, parent: FenetreArchive):
        super().__init__()
        self.parent = parent

        # Widgets
        self.combobox_lots = QComboBox()
        self.update_lots(self.parent.noms_lots)
        self.btn_charger = QPushButton("Charger le lot")
        self.btn_charger.clicked.connect(self.charger_lot)

        # Disposition
        self.disposition_h = QHBoxLayout(self)
        self.disposition_h.addStretch(1)

        self.disposition_v = QVBoxLayout(self)
        self.disposition_v.addStretch(1)

        self.disposition_v.addWidget(QLabel("icone-ouverture", self))
        self.disposition_v.addWidget(QLabel("Lots sauvegardés localement :", self))
        self.disposition_v.addWidget(self.combobox_lots)
        self.disposition_v.addWidget(self.btn_charger)

        self.disposition_v.addWidget(QLabel("Télécharger un lot :", self))
        self.disposition_v.addWidget(WidgetDownload(self))

        self.disposition_v.addStretch(1)

        self.disposition_h.addLayout(self.disposition_v)
        self.disposition_h.addStretch(1)

    def update_lots(self, noms_lots: list):
        self.combobox_lots.clear()
        self.combobox_lots.addItems(noms_lots)

    def charger_lot(self):
        self.parent.ajout_lot(self.combobox_lots.currentIndex())

class WidgetDownload(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        # Widgets
        self.line_edit = QLineEdit(parent=self, placeholderText="url")
        self.btn_download = QPushButton("icone-télécharger", self)

        # Disposition
        self.disposition = QHBoxLayout(self)
        self.disposition.addWidget(self.line_edit)
        self.disposition.addWidget(self.btn_download)
