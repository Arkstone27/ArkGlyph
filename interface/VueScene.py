from PySide6.QtWidgets import (QGridLayout, QSpinBox, QGraphicsScene, QGraphicsView, QTableWidget, QPushButton,
                               QGraphicsPathItem, QMenu)
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QCursor, QPixmap, QPainterPath

import pandas as pd
from time import time

from interface.traitement_style import icones, couleurs_zones
from download.Lot import Lot

def create_fake_data():
    dico = {f"Test {i}": ["t"*j for j in range(100)] for i in range(6)}

    return pd.DataFrame.from_dict(dico)

class VueScene(QGraphicsView):
    def __init__(self, sidebar):
        super().__init__()

        self.sidebar = sidebar

        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setAcceptDrops(True)

        # Variables
        self.last_zoom = time()
        self.scene: SceneLot = SceneLot(None, None, True)

        # Zones de textes
        self.point_depart = None
        self.point_fin = None
        self.rectangle_actuel = None

        # Widgets
        self.spin_box = SpinBoxPages(self)
        self.spin_box.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.btn_tableau = QPushButton()
        self.btn_tableau.setIcon(icones["table"])
        self.btn_tableau.setIconSize(QSize(20,20))
        self.btn_tableau.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Menu déroulant
        self.menu_deroulant = QMenu(self)
        self.action_dupliquer = self.menu_deroulant.addAction("Dupliquer (D)")

        self.action_supprimer = self.menu_deroulant.addAction("Supprimer (S)")

        self.menu_deroulant.addSeparator()
        self.menu_types = MenuTypes(self)
        self.menu_deroulant.addMenu(self.menu_types)

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

    def afficher_page_entiere(self):
        rectangle = self.scene.itemsBoundingRect()# Recupére le rectangle englobant tous les elements (le plus gros étant la page)

        if not rectangle.isNull():
            self.fitInView(rectangle, Qt.AspectRatioMode.KeepAspectRatio) # Conserve le ratio de la page

            self.scene.etat_zoom = 0
            self.update_position()

    def update_lot(self, scene_lot):
        self.scene = scene_lot
        self.setScene(scene_lot)
        self.last_zoom = time()

        self.action_dupliquer.triggered.connect(self.scene.duplication_zone_texte)
        self.action_supprimer.triggered.connect(self.scene.remove_zone_texte)

        if scene_lot.transformation is not None:
            self.setTransform(scene_lot.transformation)
            self.centerOn(self.scene.centre)
        else:
            self.afficher_page_entiere()

        self.spin_box.update_lot(scene_lot)

    def resizeEvent(self, event):
        if (time() - self.last_zoom) > 0.2:
            self.afficher_page_entiere()
        self.last_zoom = time()

    def wheelEvent(self, event):
        facteur_zoom = 1.15
        self.last_zoom = time()

        if event.angleDelta().y() > 0:
            self.scale(facteur_zoom, facteur_zoom)
            self.scene.etat_zoom += 1

        elif self.scene.etat_zoom != 0:
            self.scale(1 / facteur_zoom, 1 / facteur_zoom)
            self.scene.etat_zoom -= 1

        self.update_position()
        super().wheelEvent(event)

    def mousePressEvent(self, event):
        point_click = self.mapToScene(event.position().toPoint()) # Convertit les coos de la fenêtre en coos de la scène
        if event.button() == Qt.MouseButton.RightButton and self.point_dans_scene(point_click):
            item_dessous = self.itemAt(event.pos())

            if isinstance(item_dessous, ZoneTexteItem):
                item_dessous.setSelected(True)

            else:
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
                    lien_tableau = self.sidebar.widget_types.indice_selected

                    brush, pen = couleurs_zones[lien_tableau%len(couleurs_zones)]
                    self.rectangle_actuel.setPen(pen)
                    self.rectangle_actuel.setBrush(brush)

                    self.scene.addItem(self.rectangle_actuel)

                else:
                    self.rectangle_actuel.setPath(path) # Mise à jour

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.rectangle_actuel:
            rectangle = self.rectangle_actuel.boundingRect()
            if rectangle.width() < 30 or rectangle.height() < 30: # On retire les zones trop petites
                self.scene.removeItem(self.rectangle_actuel)
                return

            lien_tableau = self.sidebar.widget_types.indice_selected
            brush, pen = couleurs_zones[lien_tableau%len(couleurs_zones)]
            self.rectangle_actuel.setBrush(brush)

            self.scene.zones_textes.append(ZoneTexte(self.rectangle_actuel, lien_tableau))
        elif event.button() == Qt.MouseButton.LeftButton:
            self.update_position()

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace, Qt.Key.Key_S):
            self.scene.remove_zone_texte()
        elif event.key() == Qt.Key.Key_D:
            self.scene.duplication_zone_texte()

        super().keyPressEvent(event)

    def update_position(self):
        self.scene.transformation = self.transform()
        self.scene.centre = self.mapToScene(self.viewport().rect().center())

    def changer_page(self, indice):
        self.scene.changer_page(indice)

    def point_dans_scene(self, point):
        x, y = point.x(), point.y()

        return 0 <= x <= self.scene.w and 0 <= y <= self.scene.h

    def contextMenuEvent(self, event):
        item_dessous = self.itemAt(event.pos())
        if isinstance(item_dessous, ZoneTexteItem): 
            self.menu_deroulant.exec(event.globalPos())

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
        if event.mimeData().hasText() and event.mimeData().text().isdigit():
            indice_type = int(event.mimeData().text())
            position_drop = event.position().toPoint()
            item_dessous = self.itemAt(position_drop)

            if isinstance(item_dessous, ZoneTexteItem):
                self.scene.changer_lien_zone(indice_type, item_dessous)

            event.acceptProposedAction()

    def changer_lien_zone(self, indice_type: int):
        self.scene.changer_lien_zone(indice_type)

class SpinBoxPages(QSpinBox):
    def __init__(self, vue_scene: VueScene):
        super().__init__()
        self.setObjectName("Pages")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vue_scene = vue_scene

        self.valueChanged.connect(lambda indice: self.vue_scene.changer_page(indice - 1))

    def update_lot(self, scene):
        self.setSuffix(f"/{scene.lot.nb_pages}")
        
        if scene.lot.nb_pages < self.value():
            self.setValue(scene.indice_page+1)
            self.setRange(1, scene.lot.nb_pages)
        else:
            self.setRange(1, scene.lot.nb_pages)
            self.setValue(scene.indice_page+1)       
        self.scene = scene

class SceneLot(QGraphicsScene): 
    def __init__(self, lot: Lot, vue_scene: VueScene, vide=False):
        super().__init__()
        if vide:
            return
        # Variables
        self.lot, self.vue_scene = lot, vue_scene
        self.data = create_fake_data()

        self.indice_page = 0
        self.page = QPixmap(self.lot.get_chemins_pages()[self.indice_page])

        self.page_item = self.addPixmap(self.page)
        self.etat_zoom, self.transformation, self.centre = 0, None, None
        self.w, self.h = self.width(), self.height()

        # Initialisation des zones de textes
        self.zones_textes = list()

    def changer_page(self, new_indice):
        if self.indice_page == new_indice:
            return
        self.indice_page = new_indice

        self.page = QPixmap(self.lot.chemins_pages[self.indice_page])
        self.page_item.setPixmap(self.page)

        if self.page.width() > self.w or self.page.height() > self.h:
            self.vue_scene.afficher_page_entiere()
        self.w, self.h = self.width(), self.height()

    def remove_zone_texte(self):
        new_zones = list()
        for zone_texte in self.zones_textes:
            if zone_texte.scene_rectangle.isSelected():
                self.removeItem(zone_texte.scene_rectangle)
                del zone_texte
            else:
                new_zones.append(zone_texte)
        self.zones_textes = new_zones

    def duplication_zone_texte(self):
        for zone_texte in self.zones_textes:
            if zone_texte.scene_rectangle.isSelected():
                self.zones_textes.append(zone_texte.copy())
                self.addItem(self.zones_textes[-1].scene_rectangle)

    def changer_lien_zone(self, lien_tableau: int, scene_rectangle=None):
        for zone_texte in self.zones_textes:
            if zone_texte.scene_rectangle == scene_rectangle or (scene_rectangle is None and zone_texte.scene_rectangle.isSelected()):
                zone_texte.changer_lien(lien_tableau, *couleurs_zones[lien_tableau%len(couleurs_zones)])
                break


class ZoneTexteItem(QGraphicsPathItem):
    def __init__(self, path, scene, parent=None):
        super().__init__(path, parent)

        self.w_scene = 0
        self.h_scene = 0
        self.scene: QGraphicsScene = scene
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
        self.update_tooltip()

    def copy(self):
        new_zone = ZoneTexte(self.scene_rectangle.copy(),self.lien_tableau)
        return new_zone

    def update_tooltip(self):
        self.scene_rectangle.setToolTip(f"{self.lien_tableau}")

    def changer_lien(self, new_lien: int, new_brush, new_pen):
        self.lien_tableau = new_lien

        self.scene_rectangle.setBrush(new_brush)
        self.scene_rectangle.setPen(new_pen)
        self.update_tooltip()

class MenuTypes(QMenu):
    def __init__(self, vue_scene: VueScene):
        super().__init__()
        self.setTitle("Choisir le type")

        self.vue_scene = vue_scene
        self.update_types(self.vue_scene.sidebar.widget_types.noms_type)
    
    def update_types(self, noms_type: list[str]):
        self.clear()

        for indice_type, nom_type in enumerate(noms_type):
            action = self.addAction(nom_type)
            action.triggered.connect(lambda checked=False, idx=indice_type: self.vue_scene.changer_lien_zone(idx))
        

class InfosProcess:
    pass

class Tableau(QTableWidget):
    def __init__(self):
        super().__init__()

        

