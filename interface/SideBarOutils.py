from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QWidget, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, QSize, QMimeData, QRect, QPoint
from PySide6.QtGui import QCursor, QDrag, QPixmap, QPainter

from interface.traitement_style import icones, couleurs_hexs, IconLabel, Icon
from interface.gestion_processus import gestion_processus

class SideBarOutils(QFrame):
    def __init__(self, fenetre_principale):
        super().__init__()
        self.setObjectName("SideBarOutils")
        self.fenetre_principale = fenetre_principale

        # Variables
        self.visible = True

        # Widgets
        self.label_titre = IconLabel(icones["logo"], "ArchLate", 20, "Titre")
        self.icon_titre = Icon(icones["logo"], 20)

        self.btn_show_hide = QPushButton()
        self.btn_show_hide.clicked.connect(self.switch_visible)

        self.btn_show_hide.setIcon(icones["hide"])
        self.btn_show_hide.setIconSize(QSize(20, 20))
        self.btn_show_hide.setObjectName("Trans")
        self.btn_show_hide.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.label_outils = IconLabel(icones["outils"], "Outils", 20, "Titre")

        self.label_download = QLabel("Téléchargement")
        self.widget_download = WidgetDownload(self)

        self.label_types = QLabel("Types")
        self.widget_types = WidgetTypes(self)

        # Styles
        self.label_download.setObjectName("Titre")
        self.label_types.setObjectName("Titre")

        # Disposition
        self.disposition = QVBoxLayout(self)
        self.disposition.setSpacing(0)

        self.disposition.addWidget(self.label_titre)
        self.disposition.addWidget(self.icon_titre)
        self.disposition.addSpacing(15)

        self.disposition.addWidget(self.label_outils)
        self.disposition.addSpacing(10)

        self.disposition.addWidget(self.label_download)
        self.disposition.addWidget(self.widget_download)
        self.disposition.addSpacing(10)

        self.disposition.addWidget(self.label_types)
        self.disposition.addWidget(self.widget_types)

        self.disposition.addStretch(1)
        self.disposition.addWidget(self.btn_show_hide, 1, Qt.AlignmentFlag.AlignRight)

        self.switch_visible()

    def switch_visible(self):
        self.visible = not self.visible

        if self.visible:
            self.btn_show_hide.setIcon(icones["show"])
            self.setFixedWidth(250)

            for widget in (self.label_titre, self.label_outils, self.label_download, self.widget_download, self.label_types, self.widget_types):
                widget.show()
            self.icon_titre.hide()
        else:
            self.btn_show_hide.setIcon(icones["hide"])
            self.setFixedWidth(54)

            for widget in (self.label_titre, self.label_outils, self.label_download, self.widget_download, self.label_types, self.widget_types):
                widget.hide()
            self.icon_titre.show()


class WidgetDownload(QWidget):
    def __init__(self, sidebar: SideBarOutils):
        super().__init__()
        self.sidebar = sidebar 

        # Widgets
        self.line_edit = QLineEdit(parent=self, placeholderText="url")
        self.line_edit.textChanged.connect(self.line_edit.setToolTip)

        self.btn_download = QPushButton("", self)
        self.btn_download.setIcon(icones["global-search"])
        self.btn_download.setIconSize(QSize(20,20))
        self.btn_download.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_download.clicked.connect(self.download_url)

        # Disposition
        self.disposition = QHBoxLayout(self)
        self.disposition.addWidget(self.line_edit)
        self.disposition.addWidget(self.btn_download)

    def set_actif(self, actif: bool):
        self.btn_download.setEnabled(actif)

    def download_url(self):
        self.set_actif(False)
        print("-"*50)
        gestion_processus.download_lot(self.line_edit.text())

class WidgetTypes(QWidget):
    def __init__(self, sidebar: SideBarOutils):
        super().__init__()
        self.sidebar = sidebar

        self.noms_type = []
        self.disposition = QGridLayout(self)
        self.idx_max, self.indice_selected = 0, 0

        self.btn_ajout = QPushButton()
        self.btn_ajout.setIcon(icones["new"])
        self.btn_ajout.setObjectName("Trans")
        self.btn_ajout.clicked.connect(self.ajout_type)
        self.btn_ajout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.update_types()
        self.change_selected(0)

    def update_types(self):
        # Supprime les widget types
        while self.disposition.count():
            item = self.disposition.takeAt(0)
            widget = item.widget()
            if isinstance(widget, WidgetType):
                widget.deleteLater()

        # Créé les widgets types
        self.idx_max =  0
        for nom_type in self.noms_type:
            widget_type = WidgetType(nom_type, couleurs_hexs[self.idx_max%len(couleurs_hexs)], self, self.idx_max)

            self.disposition.addWidget(widget_type, self.idx_max//2, self.idx_max%2)
            self.idx_max += 1

        # Placement du bouton
        self.disposition.addWidget(self.btn_ajout, self.idx_max//2, self.idx_max%2)

    def get_widget(self, indice):
        return self.disposition.itemAtPosition(indice//2, indice%2).widget()

    def ajout_type(self):
        nom_type = f"Type {self.idx_max}"
        widget_type = WidgetType(nom_type, couleurs_hexs[self.idx_max%len(couleurs_hexs)], self, self.idx_max)
        self.disposition.addWidget(widget_type, self.idx_max//2, self.idx_max%2)        
        self.noms_type.append(nom_type)
        self.change_selected(self.idx_max)
        
        self.idx_max += 1
        self.disposition.addWidget(self.btn_ajout, self.idx_max//2, self.idx_max%2)

        if len(self.noms_type) == 14:
            self.btn_ajout.hide()



    def change_selected(self, new_indice):
        ancien = self.get_widget(self.indice_selected)
        if isinstance(ancien, WidgetType): ancien.switch_bordure(False)

        self.indice_selected = new_indice
        new = self.get_widget(new_indice)
        if isinstance(new, WidgetType): new.switch_bordure(True)

    def update_noms(self, indice: int, new_nom: str):
        self.noms_type[indice] = new_nom
        self.sidebar.fenetre_principale.frame_centre.vue_scene.menu_types.update_types(self.noms_type)


class WidgetType(QLineEdit):
    def __init__(self, nom_type: str, couleur: str, widget_types: WidgetTypes, indice: int):
        super().__init__()
        self.widget_types, self.indice = widget_types, indice

        # Style
        self.setObjectName("Type")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.couleur, self.bordure = couleur, f"border: 1px solid {couleur};"
        self.update_style()

        # Infos
        self.setText(nom_type)
        self.setToolTip(nom_type)

        self.textChanged.connect(self.changer_nom_type)

        # Drag
        self.setAcceptDrops(False)
        self.debut_drag = None

    def update_style(self):
        self.setStyleSheet(f"QLineEdit {{ {self.bordure} background-color: {self.couleur}; }} QLineEdit:hover {{border: 1px solid #7b55fd;}}")

    def changer_nom_type(self):
        self.setToolTip(self.text())
        self.widget_types.update_noms(self.indice, self.text())

    def switch_bordure(self, selected: bool):
        if selected:
            self.bordure = "border: 1px solid #7b55fd;"
        else:
            self.bordure = f"border: 1px solid {self.couleur};"
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.widget_types.change_selected(self.indice)

            self.debut_drag = event.position().toPoint()
        
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.debut_drag is None:
            return

        if not(event.buttons() & Qt.MouseButton.LeftButton):
            return

        if (event.position().toPoint() - self.debut_drag).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        drag = QDrag(self)

        mime_data = QMimeData()
        indice_column = str(self.indice)
        mime_data.setText(indice_column)

        drag.setMimeData(mime_data)

        # Affichage du contenu
        w = self.width()
        h = self.height()
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)

        rectangle = QRect(0, 0, w, h)

        painter = QPainter(pixmap)
        self.render(painter, QPoint(0,0), rectangle)
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint() - rectangle.topLeft()) # Point d'accroche

        drag.exec(Qt.DropAction.MoveAction)
        self.debut_drag = None