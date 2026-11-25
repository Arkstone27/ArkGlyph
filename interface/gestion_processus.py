from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QFrame, QLabel, QListWidgetItem, QPushButton
from PySide6.QtCore import QSize, Qt, QThreadPool, QRunnable, QObject, Signal, Slot, QObject, QTimer

from interface.traitement_style import icones, Icon
from gestion_lot.download_lot import download_lot

class ListProcessus(QListWidget):
    def __init__(self, frame_centre):
        super().__init__(parent=frame_centre)
        self.setObjectName("Process")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFixedWidth(400)

        self.frame_centre = frame_centre

    def ajout_processus(self, titre_processus: str):
        info_processus = InfosProcessus(titre_processus)

        item = QListWidgetItem()
        info_processus.item = item

        taille = info_processus.sizeHint()
        item.setSizeHint(QSize(taille.width(), taille.height()+20))
        self.insertItem(0, item)
        self.setItemWidget(item, info_processus)

        self.update_taille(item)
        self.update_position()
        return info_processus

    def update_taille(self, item: QListWidgetItem):
        if item is None:
            self.setFixedHeight(0)
            return 
        
        self.setFixedHeight(item.sizeHint().height() * self.count())

    def fin_processus(self, info_processus):
        item = info_processus.item

        self.takeItem(self.indexFromItem(item).row())
        del item
        del info_processus

        self.update_taille(self.item(0))
        self.update_position()

    def update_position(self):
        margin = 20
        x = margin
        y = self.frame_centre.height() - self.height() - margin
        self.move(x, y)

class InfosProcessus(QFrame):
    def __init__(self, titre_processus: str):
        super().__init__()
        self.item = None

        # Widgets
        big_icon = Icon(icones["cpu"], 50)
        label_titre = QLabel(titre_processus)
        label_titre.setObjectName("titre")

        self.label_status = QLabel(" Initialisation...")
        self.label_status.setObjectName("texte")

        # Disposition
        self.disposition = QHBoxLayout(self)
        self.disposition_v = QVBoxLayout()

        self.disposition_v.addWidget(label_titre)
        self.disposition_v.addWidget(self.label_status)
        self.disposition_v.addStretch(1)

        self.disposition.addWidget(big_icon)
        self.disposition.addLayout(self.disposition_v)
        self.disposition.addStretch(1)

    def update_status(self, new_status: str):
        self.label_status.setText(" "+new_status)

class ListNotifs(QListWidget):
    def __init__(self, frame_centre):
        super().__init__(parent=frame_centre)
        self.setObjectName("Process")
        self.setFixedWidth(400)

        self.frame_centre = frame_centre


    def ajout_notif(self, titre_notif: str, infos: str, warning: bool, temps_vanish: int=0):
        info_notif = InfosNotif(titre_notif, infos, warning, temps_vanish, self)
        taille = info_notif.sizeHint()

        item = QListWidgetItem()
        info_notif.item = item

        item.setSizeHint(QSize(taille.width(), taille.height()+20))
        self.insertItem(0, item)
        self.setItemWidget(item, info_notif)

        self.update_taille()
        self.update_position()

    def supprimer_notif(self, info_notif):
        item = info_notif.item

        self.takeItem(self.indexFromItem(item).row())
        del item
        del info_notif

        self.update_taille()
        self.update_position()
    
    def update_position(self):
        margin = 20
        x = self.frame_centre.width() - self.width() - margin
        y = self.frame_centre.height() - self.height() - margin
        self.move(x, y)

    def update_taille(self):
        if self.count() == 0:
            self.setFixedHeight(0)
            return 

        height = 0
        for indice in range(self.count()):
            item = self.item(indice)
            height += item.sizeHint().height()
        
        self.setFixedHeight(height)

class InfosNotif(QFrame):
    def __init__(self, titre_notif: str, infos: str, warning: bool, temps_vanish: int, liste_notifs: ListNotifs):
        super().__init__()

        # Widgets
        icone = icones["warning"] if warning else icones["notification"]
        big_icon = Icon(icone, 50)
        label_titre = QLabel(titre_notif)
        label_titre.setObjectName("titre")

        self.btn_fermer = QPushButton()
        self.btn_fermer.setIcon(icones["close"])
        self.btn_fermer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fermer.setFixedSize(34, 34)
        self.btn_fermer.setObjectName("Trans")
        self.btn_fermer.clicked.connect(lambda c, l=liste_notifs: l.supprimer_notif(self))

        self.label_status = QLabel(clean_infos(infos))
        self.label_status.setObjectName("texte")

        # Disposition
        self.disposition = QHBoxLayout(self)
        self.disposition_icon = QVBoxLayout()
        self.disposition_icon.addWidget(big_icon)
        self.disposition_icon.addStretch(1)

        self.disposition_v = QVBoxLayout()
        self.disposition_v.addWidget(label_titre)
        self.disposition_v.addWidget(self.label_status)
        self.disposition_v.addStretch(1)

        self.disposition.addLayout(self.disposition_icon)
        self.disposition.addLayout(self.disposition_v, 1)
        self.disposition.addWidget(self.btn_fermer, 0, Qt.AlignmentFlag.AlignTop)

        # Timer (si besoin) (temps_vanish en ms)
        if temps_vanish != 0:
            self.timer =QTimer(self)
            self.timer.setSingleShot(True)

            self.timer.timeout.connect(lambda l=liste_notifs: l.supprimer_notif(self))
            self.timer.start(temps_vanish)

def coupure_intelligente(ligne, indice_max):
    while ligne[indice_max] != " " or indice_max < 5:
        indice_max -= 1
    return indice_max

def clean_infos(infos: str):
    new_infos = " "
    lignes = infos.split("\n")
    
    for ligne in lignes:
        while len(ligne) > 25:
            indice_coupure = coupure_intelligente(ligne, 25)
            new_infos += ligne[:indice_coupure+1]
            new_infos += "\n"
            ligne = ligne[indice_coupure+1:]

        new_infos += ligne
        new_infos += "\n"
    return new_infos[:-1]

class SignauxWorker(QObject):
    status = Signal(str, int)
    fin = Signal(bool, str)

class Gestion_Processus(QObject): # En parallèle
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()    

    def set_widgets(self, fenetre_principale):
        self.liste_processus = fenetre_principale.frame_centre.liste_processus
        self.liste_notifs = fenetre_principale.frame_centre.liste_notifs

        self.frame_ajout = fenetre_principale.frame_centre.frame_ajout
        self.widget_download = fenetre_principale.sidebar_outils.widget_download

    def download_lot(self, url_lot):
        self.info_processus_download: InfosProcessus = self.liste_processus.ajout_processus("Téléchargement")
        worker = DownloadWorker(url_lot)

        worker.signaux.status.connect(self.update_download)
        worker.signaux.fin.connect(self.fin_download)

        self.thread_pool.start(worker)

    @Slot(str, int)
    def update_download(self, status, progression):
        print(status)
        self.sender()        
        self.info_processus_download.update_status(status)

    @Slot(bool, str)
    def fin_download(self, reussite, status):

        print(status)
        self.sender()
        if reussite:
            self.liste_notifs.ajout_notif("Téléchargement", status, False)
        else:
            self.liste_notifs.ajout_notif("Attention !", status, True)
        self.liste_processus.fin_processus(self.info_processus_download)

        self.widget_download.set_actif(True)
        self.frame_ajout.update_lots()

class DownloadWorker(QRunnable):
    def __init__(self, url_lot: str):
        super().__init__()
        self.signaux = SignauxWorker()
        self.url_lot = url_lot

    @Slot()
    def run(self):
        download_lot(self.url_lot, self.signaux)

gestion_processus = Gestion_Processus()