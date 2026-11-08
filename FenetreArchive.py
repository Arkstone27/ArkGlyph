from PySide6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsScene, QGraphicsView, QPushButton, QSpinBox, QTabBar,
    QComboBox, QLineEdit, QFrame, QMessageBox, QGraphicsPathItem, QMenu)
from PySide6.QtGui import QPixmap, QPainterPath, QPen, QBrush, QColor, QPainter
from PySide6.QtCore import Qt, QRectF, QPointF

from time import time

from DockProgress import gestion_processus
from Lot import Lot, get_lots_saved
from load_icones import SvgWidget, icone_cross

class FenetreArchive(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("FenetreArchive")

        # Widgets
        self.tabs = QTabWidget(self, tabsClosable=True)
        self.onglets_lots = dict()

        self.onglet_ajout = OngletAjoutLot(self)
        self.tabs.addTab(self.onglet_ajout, " + ")
        self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None) # Retire la croix de fermeture

        # Disposition
        self.disposition = QVBoxLayout(self)
        self.disposition.addWidget(self.tabs)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Gestion des Lots
        self.update_lots()

        # Indices de progressions
        self.indice_download = 0

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

    def update_lots(self):
        self.chemins_lots, self.noms_lots = get_lots_saved()
        self.onglet_ajout.update_lots(self.noms_lots)

    def fin_download(self, reussite: bool, message: str):
        print(message)
        if reussite:
            self.update_lots()
            QMessageBox.information(self, "Opération reussie", message)
        else:
            QMessageBox.warning(self, "Echec du download !", message)
        self.onglet_ajout.wigdet_download.btn_download.setEnabled(True)

class OngletLot(QGraphicsView):
    def __init__(self, lot, indice_position, parent=None):
        super().__init__()

        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.indice_position = indice_position
        self.setAcceptDrops(True)

        # Lot
        self.lot = lot
        self.indice_page = 0

        # Scene
        self.scene = QGraphicsScene()

        self.page = QPixmap(self.lot.chemins_pages[self.indice_page].resolve())
        self.w, self.h = self.page.size().width(), self.page.size().height()

        self.page_item = self.scene.addPixmap(self.page)
        self.changer_page(self.indice_page)

        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.afficher_page_entiere()

        self.etat_zoom = 0
        self.last_zoom = time()

        # Initialisation des dessins des zones de textes
        self.point_depart = None
        self.point_fin = None
        self.rectangle_actuel = None

        self.zones_textes = list()
        self.couleurs_zones = [creation_brush_pen_zone(*couleur) for couleur in (
            (67,48,117), (103, 48, 117), (48, 62, 117), (48, 97, 117), (117, 48, 97), (48, 117, 102), (117, 48, 62))]

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

        # Menu déroulant
        self.menu_deroulant = QMenu(self)
        action_dupliquer = self.menu_deroulant.addAction("Dupliquer")
        action_dupliquer.triggered.connect(self.duplication_zone_texte)

        action_supprimer = self.menu_deroulant.addAction("Supprimer")
        action_supprimer.triggered.connect(self.remove_zone_texte)

        self.menu_deroulant.addSeparator()
        action_type = self.menu_deroulant.addAction("Choisir le type   ")

    def afficher_page_entiere(self):
        rectangle = self.scene.itemsBoundingRect()# Recupere le rectangle englobant tous les elements (le plus gros etant la page)

        if not rectangle.isNull():
            self.fitInView(rectangle, Qt.AspectRatioMode.KeepAspectRatio) # Conserve le ratio de la page

            self.etat_zoom = 0

    def changer_page(self, new_indice: int):
        self.indice_page = new_indice
        self.page = QPixmap(self.lot.chemins_pages[self.indice_page])

        self.page_item.setPixmap(self.page)

        if self.page.width() > self.w or self.page.height() > self.h:
            self.afficher_page_entiere()

        self.w, self.h = self.scene.width(), self.scene.height()
    def resizeEvent(self, event):
        if (time() - self.last_zoom) > 0.1:
            self.afficher_page_entiere()

    def wheelEvent(self, event):# On réécrit les choses à faire avec la molette
        facteur_zoom = 1.15
        self.last_zoom = time()

        if event.angleDelta().y() > 0:
            self.scale(facteur_zoom, facteur_zoom)
            self.etat_zoom += 1

        elif self.etat_zoom != 0:
            self.etat_zoom -= 1
            self.scale(1/facteur_zoom, 1/facteur_zoom)
        super().wheelEvent(event)

    def contextMenuEvent(self, event):
        if self.scene.selectedItems():
            self.menu_deroulant.exec(event.globalPos())

    def mousePressEvent(self, event):
        point_click = self.mapToScene(event.position().toPoint()) # Convertit les coos de la fenêtre en coos de la scène
        if event.button() == Qt.MouseButton.RightButton and self.point_dans_scene(point_click):
            self.point_depart = point_click

            self.rectangle_actuel = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.point_depart and (event.buttons() &  Qt.MouseButton.RightButton):
            point_actuel = self.mapToScene(event.position().toPoint())

            if self.point_dans_scene(point_actuel):
                rectangle = QRectF(self.point_depart, point_actuel).normalized()

                path = QPainterPath()
                path.addRoundedRect(rectangle, 15, 15) # arrondi de 15px

                if self.rectangle_actuel is None:
                    self.rectangle_actuel = ZoneTexteItem(path, self.scene)

                    brush, pen = self.couleurs_zones[0]
                    self.rectangle_actuel.setPen(pen) # épaisseur de 2px
                    self.rectangle_actuel.setBrush(brush)

                    self.scene.addItem(self.rectangle_actuel)

                else:
                    self.rectangle_actuel.setPath(path) # Mise à jour

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.rectangle_actuel:
            brush, pen = self.couleurs_zones[0]
            self.rectangle_actuel.setBrush(brush)

            self.zones_textes.append(ZoneTexte(self.rectangle_actuel, 0))

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.remove_zone_texte()
        elif event.key() == Qt.Key.Key_D:
            self.duplication_zone_texte()

        super().keyPressEvent(event)

    def point_dans_scene(self, point):
        x, y = point.x(), point.y()

        return 0 <= x <= self.w and 0 <= y <= self.h

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        position_drop = self.mapToScene(event.position().toPoint())

        if event.mimeData().hasText() and self.point_dans_scene(position_drop):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            indice_column = int(event.mimeData().text())
            position_drop = event.position().toPoint()
            item_dessous = self.itemAt(position_drop)

            if isinstance(item_dessous, ZoneTexteItem):
                self.changer_lien_zone(item_dessous, indice_column)

            event.acceptProposedAction()

    def remove_zone_texte(self):
        new_zones = list()
        for zone_texte in self.zones_textes:
            if zone_texte.scene_rectangle.isSelected():
                # print(zone_texte.scene_rectangle.path().boundingRect())
                self.scene.removeItem(zone_texte.scene_rectangle)
                del zone_texte
            else:
                new_zones.append(zone_texte)
        self.zones_textes = new_zones

    def duplication_zone_texte(self):
        for zone_texte in self.zones_textes:
            if zone_texte.scene_rectangle.isSelected():
                self.zones_textes.append(zone_texte.copy())
                self.scene.addItem(self.zones_textes[-1].scene_rectangle)

    def changer_lien_zone(self, scene_rectangle: ZoneTexteItem, lien_tableau: int):
        for zone_texte in self.zones_textes:
            if zone_texte.scene_rectangle == scene_rectangle:
                zone_texte.changer_lien(lien_tableau, *self.couleurs_zones[lien_tableau%len(self.couleurs_zones)])
                break


class SpinBoxPages(QSpinBox):
    def __init__(self, lot: Lot, parent=None):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widget
        self.setSuffix(f"/{lot.nb_pages}")
        self.setRange(1, lot.nb_pages)

class FullView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()
        # A faire

class ZoneTexteItem(QGraphicsPathItem):
    def __init__(self, path, scene, parent=None):
        super().__init__(path, parent)

        self.w_scene = 0
        self.h_scene = 0
        self.scene = scene
        self.get_max_scene()

        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def itemChange(self, change, value):

        if change == QGraphicsPathItem.GraphicsItemChange.ItemPositionChange:
            self.get_max_scene()
            rectangle_forme = self.path().boundingRect()
            rectangle_scene = rectangle_forme.translated(value)

            if (rectangle_scene.left() < 0 or rectangle_scene.right() > self.w_scene
                    or rectangle_scene.top() < 0 or rectangle_scene.bottom() > self.h_scene):
                return self.pos()
        return super().itemChange(change, value)

    def get_max_scene(self):
        self.w_scene = self.scene.width()
        self.h_scene = self.scene.height()

    def copy(self):
        new_zone = ZoneTexteItem(self.path(), self.scene)

        new_zone.setPen(self.pen())
        new_zone.setBrush(self.brush())

        new_zone.setTransform(self.transform())
        new_zone.setRotation(self.rotation())
        new_zone.setScale(self.scale())

        new_zone.setPos(self.pos() + QPointF(10,10))

        return new_zone

class ZoneTexte:
    def __init__(self, scene_rectangle, lien_tableau):
        self.scene_rectangle = scene_rectangle
        self.lien_tableau = lien_tableau

    def copy(self):
        new_zone = ZoneTexte(self.scene_rectangle.copy(),self.lien_tableau)
        return new_zone

    def changer_lien(self, new_lien: int, new_brush, new_pen):
        self.lien_tableau = new_lien
        self.scene_rectangle.setBrush(new_brush)
        self.scene_rectangle.setPen(new_pen)

class OngletAjoutLot(QFrame):
    def __init__(self, parent: FenetreArchive):
        super().__init__()
        self.parent = parent
        self.setObjectName("OngletAjoutLot")

        # Widgets
        self.combobox_lots = QComboBox()
        self.combobox_lots.currentTextChanged.connect(self.combobox_lots.setToolTip)

        self.btn_charger = QPushButton("Charger le lot")
        self.btn_charger.clicked.connect(self.charger_lot)
        self.wigdet_download = WidgetDownload(self)

        # Disposition
        self.disposition_h = QHBoxLayout(self)
        self.disposition_h.addStretch(1)

        self.disposition_v = QVBoxLayout(self)
        self.disposition_v.setSpacing(10)
        self.disposition_v.addStretch(1)

        self.disposition_v.addWidget(SvgWidget("icones/open.svg", 100), alignment=Qt.AlignmentFlag.AlignCenter)
        self.disposition_v.addWidget(QLabel("Lots sauvegardés localement :", self))
        self.disposition_v.addWidget(self.combobox_lots)
        self.disposition_v.addWidget(self.btn_charger)

        self.disposition_v.addWidget(QLabel("Télécharger un lot :", self))
        self.disposition_v.addWidget(self.wigdet_download)

        self.disposition_v.addStretch(2)

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
        self.parent = parent 

        # Widgets
        self.line_edit = QLineEdit(parent=self, placeholderText="url")
        self.line_edit.textChanged.connect(self.line_edit.setToolTip)

        self.btn_download = QPushButton("", self)
        self.btn_download.setIcon(icone_cross)
        self.btn_download.setObjectName("Download")


        self.btn_download.clicked.connect(self.download_url)

        # Disposition
        self.disposition = QHBoxLayout(self)
        self.disposition.addWidget(self.line_edit)
        self.disposition.addWidget(self.btn_download)

    def download_url(self):
        self.btn_download.setEnabled(False)
        print("-"*50)
        gestion_processus.download_lot(self.line_edit.text())

def creation_brush_pen_zone(r, v, b):
    return QBrush(QColor(r, v, b, 100)), QPen(QColor(r,v,b), 2)