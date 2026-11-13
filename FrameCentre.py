from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QListWidget, QListWidgetItem, QLabel, QTabBar, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from Lot import Lot, get_lots_saved
from VueScene import VueScene

class FrameCentre(QFrame):
    def __init__(self, fenetre_principal):
        super().__init__(parent=fenetre_principal)
        self.fenetre_principal = fenetre_principal

        # Variables
        self.lots_ouverts = list()

        # Widgets
        self.barre_superieure = BarreSuperieure(self)

        # Centre
        self.centre = QStackedWidget(self) # self.tab_bar.currentChanged.connect(self.stack.setCurrentIndex)
        self.vue_scene = VueScene()
        self.frame_ajout = FrameAjout(self)

        self.centre.addWidget(self.frame_ajout)
        self.centre.addWidget(self.vue_scene)
        
        # Disposition
        self.disposition = QVBoxLayout(self)
        self.disposition.setContentsMargins(0, 0, 0, 0)
        self.disposition.addWidget(self.barre_superieure)
        self.disposition.addWidget(self.centre)

        self.centre.setCurrentIndex(1)
    def action_ajout(self):
        self.centre.setCurrentIndex(0)


        
class BarreSuperieure(QFrame):
    def __init__(self, frame_centre: FrameCentre):
        super().__init__(parent=frame_centre)
        # Variables
        self.ouverture = True
        self.frame_centre = frame_centre
        
        # Widgets
        self.tab_bar = QTabBar(self)
        self.tab_bar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.btn_ajout = QPushButton("+")
        self.btn_ajout.clicked.connect(self.frame_centre.action_ajout)
        self.btn_ajout.hide()

        self.btn_settings = QPushButton("⊛")

        self.btn_reduire = QPushButton("-")
        self.btn_reduire.clicked.connect(self.frame_centre.fenetre_principal.showMinimized)

        self.btn_agrandir = QPushButton("□")
        self.btn_agrandir.clicked.connect(self.frame_centre.fenetre_principal.showMaximized)

        self.btn_fermer = QPushButton("x")
        self.btn_fermer.clicked.connect(self.frame_centre.fenetre_principal.close)

        for btn in (self.btn_ajout, self.btn_settings, self.btn_reduire, self.btn_agrandir, self.btn_fermer):
            btn.setObjectName("Trans")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Disposition
        self.disposition = QHBoxLayout(self)

        self.disposition.addWidget(self.tab_bar)
        self.disposition.addWidget(self.btn_ajout)

        self.disposition.addStretch(1)

        self.disposition.addWidget(self.btn_settings)
        self.disposition.addWidget(self.btn_reduire)
        self.disposition.addWidget(self.btn_agrandir)
        self.disposition.addWidget(self.btn_fermer)



class FrameAjout(QFrame):
    def __init__(self, frame_centre: FrameCentre):
        super().__init__(parent=frame_centre)
        self.setObjectName("Ajout")

        # Variables
        self.lots = get_lots_saved()*40

        # Widgets
        self.label_lots = QLabel(f"{len(self.lots)} Lots" if len(self.lots) else "Aucun Lot")
        self.label_lots.setObjectName("Titre")

        self.liste_lots = QListWidget(self)
        self.liste_lots.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.liste_lots.itemClicked.connect(self.lot_selected)
        self.update_lots()

        # Disposition
        self.disposition_v = QVBoxLayout()
        self.disposition_v.addStretch(1)
        self.disposition_v.addWidget(self.label_lots)
        self.disposition_v.addWidget(self.liste_lots, 3)
        self.disposition_v.addStretch(3)

        self.disposition = QHBoxLayout(self)
        self.disposition.addStretch(1)
        self.disposition.addLayout(self.disposition_v, 5)
        self.disposition.addStretch(1)

    def update_lots(self):
        self.liste_lots.clear()
        max_width, height = 600, 100
        for lot in self.lots:
            item = QListWidgetItem(self.liste_lots)
            def_lot = DefLot(lot)

            max_width = max(def_lot.sizeHint().width() + 100, max_width)
            height = def_lot.sizeHint().height()

            item.setSizeHint(def_lot.sizeHint())
            self.liste_lots.setItemWidget(item, def_lot)

        self.liste_lots.setMaximumWidth(max_width)
        self.liste_lots.setMinimumWidth(max_width)
        self.liste_lots.setFixedHeight(height*max(1, min(len(self.lots), 8)))

    def lot_selected(self, item):
        indice_lot = self.liste_lots.currentRow()
        self.liste_lots.setCurrentRow(-1)
        print(indice_lot)


class DefLot(QFrame):
    def __init__(self, lot: Lot):
        super().__init__()
        self.setObjectName("Trans")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Widgets
        self.label_nom = QLabel(f"Archlate/{lot.nom}")
        self.label_nom.setObjectName("titre")
    
        self.label_infos = QLabel()
        self.label_infos.setObjectName("texte")

        self.label_infos.setText(f"{lot.nb_pages} pages ∙ <a href='{lot.url}' style='color: #bcb2ff' >{clean_url(lot.url)}</a>")
        self.label_infos.setOpenExternalLinks(True)

        self.btn_supprimer = QPushButton("⍔")
        self.btn_supprimer.setObjectName("Red")
        self.btn_supprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_supprimer.setFixedSize(34, 34)

        # Disposition
        self.disposition_v = QVBoxLayout()

        self.disposition_v.addWidget(self.label_nom)
        self.disposition_v.addWidget(self.label_infos)

        self.disposition = QHBoxLayout(self)
        self.disposition.addLayout(self.disposition_v)
        self.disposition.addWidget(self.btn_supprimer)

def clean_url(url: str):
    idx_debut = url.find("//") + 1
    url = url[idx_debut+1:]
    idx_fin_slash = url.find("/")
    idx_debut_slash = url[::-1].find("/")
    
    if idx_fin_slash == -1 or url.count("/") == 1:
        return url
    return f"{url[:idx_fin_slash]}/.../{url[-idx_debut_slash:]}"