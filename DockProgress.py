from PySide6.QtWidgets import QDockWidget, QListWidget, QWidget
from PySide6.QtCore import Qt, QThreadPool, QRunnable, QObject, Signal, Slot

from download_lot import download_lot
import time


class DockProgress(QDockWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("DockProgress")

        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.setTitleBarWidget(QWidget(self))
        self.setFixedHeight(45)

        self.liste_status = ListeStatus()
        self.setWidget(self.liste_status)


class ListeStatus(QListWidget):
    def __init__(self):
        super().__init__()

        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)

        # self.anim_loading = QMovie("icones/loading.gif")
        # self.anim_loading.start()
        #
        # self.label_loading =QLabel()
        # self.label_loading.setMovie(self.anim_loading)
        # self.label_loading.setFixedSize(20,20)
        # self.label_loading.setScaledContents(True)
        #
        # self.object_loading = QListWidgetItem(self)
        #
        # self.setItemWidget(self.object_loading, self.label_loading)

        self.addItem("Aucun processus en cours !")
        self.nb_processus = 0

    def new_processus(self, message_debut):
        self.nb_processus += 1
        self.item(0).setText(f"{self.nb_processus} processus en cours...")

        self.addItem("|")
        self.addItem(message_debut)

        return self.count() - 1

    def update_processus(self, indice: int, message: str):
        self.item(indice).setText(message)

    def fin_processus(self, indice):
        for i in range(2):
            item = self.takeItem(indice-i)
            del item

        self.nb_processus -= 1
        if self.nb_processus == 0:
            self.item(0).setText("Aucun processus en cours !")

class SignauxWorker(QObject):
    status = Signal(str, int)
    fin = Signal(bool, str)

class Gestion_Processus: # En parallèle
    def __init__(self):
        self.thread_pool = QThreadPool()
        self.indice_download = 0

    def set_Fenetres(self, fenetre_principale):
        self.fenetre_principale = fenetre_principale
        self.fenetre_archive = fenetre_principale.fenetre_archive
        self.liste_status = fenetre_principale.dock_progress.liste_status

    def download_lot(self, url_lot):
        self.indice_download = self.liste_status.new_processus("Initialisation du téléchargement...")
        worker = DownloadWorker(url_lot)

        worker.signaux.status.connect(self.update_download)
        worker.signaux.fin.connect(self.fin_download)

        self.thread_pool.start(worker)

    @Slot(str, int)
    def update_download(self, status, progression):
        print(status)
        self.liste_status.update_processus(self.indice_download, status)

    @Slot(bool, str)
    def fin_download(self, reussite, status):
        self.fenetre_archive.fin_download(reussite, status)
        self.liste_status.fin_processus(self.indice_download)

class DownloadWorker(QRunnable):
    def __init__(self, url_lot: str):
        super().__init__()
        self.signaux = SignauxWorker()
        self.url_lot = url_lot

    @Slot()
    def run(self):
        download_lot(self.url_lot, self.signaux)

gestion_processus = Gestion_Processus()




