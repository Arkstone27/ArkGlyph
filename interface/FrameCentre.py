from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QListWidget, QListWidgetItem, QLabel, QTabBar, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor, QResizeEvent

import shutil

from interface.traitement_style import icones, IconLabels, SvgWidget
from download.Lot import Lot, get_lots_saved
from interface.VueScene import VueScene, SceneLot
from interface.gestion_processus import ListProcessus, ListNotifs

class FrameCentre(QFrame):
    def __init__(self, fenetre_principal):
        super().__init__(parent=fenetre_principal)
        self.fenetre_principal = fenetre_principal

        # Variables
        self.lots_ouverts, self.scenes = list(), list()

        # Widgets
        self.barre_superieure = BarreSuperieure(self)

        # Centre
        self.centre = QStackedWidget(self)
        self.vue_scene = VueScene(self.fenetre_principal.sidebar_outils)
        self.frame_ajout = FrameAjout(self)

        self.centre.addWidget(self.frame_ajout)
        self.centre.addWidget(self.vue_scene)
        
        # Disposition
        self.disposition = QVBoxLayout(self)
        self.disposition.setContentsMargins(0, 0, 0, 0)
        self.disposition.addWidget(self.barre_superieure)
        self.disposition.addWidget(self.centre)

        # Informations des processus & Notifications
        self.liste_processus = ListProcessus(self)
        self.liste_processus.raise_()

        self.liste_notifs = ListNotifs(self)
        self.liste_notifs.raise_()

    def action_ajout(self):
        self.centre.setCurrentIndex(0)
        self.barre_superieure.action_ajout(len(self.lots_ouverts))

    def action_lot(self, indice_lot: int):
        if indice_lot == self.barre_superieure.indice_new_tab:
            return
        self.centre.setCurrentIndex(1)
        self.vue_scene.update_lot(self.scenes[indice_lot])
        if len(self.lots_ouverts) != self.barre_superieure.tab_bar.count():
            self.barre_superieure.remove_new_tab()

    def ajout_lot(self, lot):
        if lot in self.lots_ouverts:
            return
        self.lots_ouverts.append(lot)
        self.scenes.append(SceneLot(lot, self.vue_scene))
        self.barre_superieure.ajout_lot(lot)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.liste_processus.update_position()
        self.liste_notifs.update_position()

class BarreSuperieure(QFrame):
    def __init__(self, frame_centre: FrameCentre):
        super().__init__(parent=frame_centre)
        # Variables
        self.ouverture = True
        self.frame_centre = frame_centre
        self.indice_new_tab = 0
        
        # Widgets
        self.tab_bar = QTabBar(self)

        self.tab_bar.addTab("...")
        self.tab_bar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.tab_bar.currentChanged.connect(self.frame_centre.action_lot)

        self.btn_ajout = QPushButton()
        self.btn_ajout.clicked.connect(self.frame_centre.action_ajout)
        self.btn_ajout.hide()

        self.btn_settings = QPushButton()

        self.btn_reduire = QPushButton()
        self.btn_reduire.clicked.connect(self.frame_centre.fenetre_principal.showMinimized)

        self.btn_agrandir = QPushButton()
        self.btn_agrandir.clicked.connect(self.frame_centre.fenetre_principal.maximizer)

        self.btn_fermer = QPushButton()
        self.btn_fermer.clicked.connect(self.frame_centre.fenetre_principal.close)

        # Styles
        for btn in (self.btn_ajout, self.btn_settings, self.btn_reduire, self.btn_agrandir, self.btn_fermer):
            btn.setObjectName("Trans")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setIconSize(QSize(20, 20))

        self.btn_ajout.setIcon(icones["new"])

        self.btn_settings.setIcon(icones["settings"])
        self.btn_reduire.setIcon(icones["minus"])
        self.btn_agrandir.setIcon(icones["maximize"])
        self.btn_fermer.setIcon(icones["close"])
        
        # Disposition
        self.disposition = QHBoxLayout(self)

        self.disposition.addWidget(self.tab_bar)
        self.disposition.addWidget(self.btn_ajout)

        self.disposition.addStretch(1)

        self.disposition.addWidget(self.btn_settings)
        self.disposition.addWidget(self.btn_reduire)
        self.disposition.addWidget(self.btn_agrandir)
        self.disposition.addWidget(self.btn_fermer)

    def remove_new_tab(self):
        self.tab_bar.removeTab(self.indice_new_tab)

    def action_ajout(self, indice_tab):
        if self.tab_bar.tabText(self.tab_bar.currentIndex()) == "...":
            return
        self.indice_new_tab = indice_tab
        self.tab_bar.addTab("...")
        self.tab_bar.setCurrentIndex(self.indice_new_tab)

    def ajout_lot(self, lot):
        self.tab_bar.setTabText(self.indice_new_tab, clean_nom(lot))
        self.tab_bar.setTabToolTip(self.indice_new_tab, lot.nom)

        indice_temp, self.indice_new_tab = self.indice_new_tab, None
        self.frame_centre.action_lot(indice_temp)
        self.btn_ajout.show()


class FrameAjout(QFrame):
    def __init__(self, frame_centre: FrameCentre):
        super().__init__(parent=frame_centre)
        self.setObjectName("Ajout")
        self.frame_centre = frame_centre

        # Variables
        self.lots = list()
        self.deflots = list()
        self.indices_disabled = set()

        # Widgets
        self.widget_load = SvgWidget("interface/resources/dark-icons/lot-load.svg", 100)

        self.label_lots = QLabel()
        self.label_lots.setObjectName("Titre")

        self.liste_lots = QListWidget(self)
        self.liste_lots.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.liste_lots.itemClicked.connect(self.lot_selected)
        self.update_lots()

        # Disposition
        self.disposition_v = QVBoxLayout()
        self.disposition_v.addStretch(1)
        self.disposition_v.addWidget(self.widget_load, 1, Qt.AlignmentFlag.AlignHCenter)
        self.disposition_v.addWidget(self.label_lots)
        self.disposition_v.addWidget(self.liste_lots, 3)
        self.disposition_v.addStretch(3)

        self.disposition = QHBoxLayout(self)
        self.disposition.addStretch(1)
        self.disposition.addLayout(self.disposition_v, 5)
        self.disposition.addStretch(1)

    def update_lots(self):
        self.lots = get_lots_saved(self.lots)
        self.label_lots.setText(f"{len(self.lots)} Lots" if len(self.lots) else "Aucun Lot")

        self.liste_lots.clear()
        self.deflots, self.indices_disabled = list(), set()
        lots_ouverts = self.frame_centre.lots_ouverts

        max_width, height = 600, 100
        for indice_lot, lot in enumerate(self.lots):
            item = QListWidgetItem(self.liste_lots)
            def_lot = DefLot(lot, self)
            self.deflots.append(def_lot)
            if lot in lots_ouverts:
                def_lot.disabled()
                self.indices_disabled.add(indice_lot)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)

            max_width = max(def_lot.sizeHint().width() + 100, max_width)
            height = def_lot.sizeHint().height()

            item.setSizeHint(def_lot.sizeHint())
            self.liste_lots.setItemWidget(item, def_lot)

        self.liste_lots.setMaximumWidth(max_width)
        self.liste_lots.setMinimumWidth(max_width)
        self.liste_lots.setFixedHeight(height*max(1, min(len(self.lots), 8)))

    def lot_selected(self, item):
        indice_lot = self.liste_lots.currentRow()
        if indice_lot in self.indices_disabled or indice_lot == -1:
            return

        item = self.liste_lots.item(indice_lot)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.deflots[indice_lot].disabled()

        self.indices_disabled.add(indice_lot)
        self.liste_lots.setCurrentRow(-1)
        self.frame_centre.ajout_lot(self.lots[indice_lot])

    def supprimer_lot(self, lot: Lot):
        indice_lot = self.lots.index(lot)
        self.lots.pop(indice_lot)

        shutil.rmtree(lot.chemin_lot)
        
        self.update_lots()

class DefLot(QFrame):
    def __init__(self, lot: Lot, frame_ajout: FrameAjout):
        super().__init__()
        self.setObjectName("Trans")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Widgets
        self.label_nom = QLabel(f"Archlate/{lot.nom}")
        self.label_nom.setObjectName("titre")

        self.label_infos = IconLabels([icones["paper"], f"{lot.nb_pages} pages ∙", icones["link"], f"<a href='{lot.url}' style='color: #bcb2ff' >{clean_url(lot.url)}</a>"],
                                      ["texte"]*4,20)

        self.btn_supprimer = QPushButton()
        self.btn_supprimer.setIcon(icones["trash"])
        self.btn_supprimer.setIconSize(QSize(20, 20))
        self.btn_supprimer.setObjectName("Red")
        self.btn_supprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_supprimer.setFixedSize(34, 34)

        self.btn_supprimer.clicked.connect(lambda checked=False, lot=lot: frame_ajout.supprimer_lot(lot))

        # Disposition
        self.disposition_v = QVBoxLayout()

        self.disposition_v.addWidget(self.label_nom)
        self.disposition_v.addWidget(self.label_infos)

        self.disposition = QHBoxLayout(self)
        self.disposition.addLayout(self.disposition_v)
        self.disposition.addWidget(self.btn_supprimer)

    def disabled(self):
        self.setCursor(QCursor(Qt.CursorShape.ForbiddenCursor))
        self.label_nom.setEnabled(False)
        self.btn_supprimer.hide()

def clean_url(url: str):
    idx_debut = url.find("//") + 1
    url = url[idx_debut+1:]
    idx_fin_slash = url.find("/")
    idx_debut_slash = url[::-1].find("/")
    
    if idx_fin_slash == -1 or url.count("/") == 1:
        return url
    return f"{url[:idx_fin_slash]}/.../{url[-idx_debut_slash:]}"

def clean_nom(lot: Lot):
    nom = lot.nom
    indice_tiret = len(nom) - nom[::-1].find("-")

    if len(nom[:indice_tiret]) < 12:
        return nom
    return f"{nom[:6]}... -{nom[indice_tiret:]}"