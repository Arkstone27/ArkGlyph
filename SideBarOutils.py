from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor

from traitement_style import icones, IconLabel, Icon

class SideBarOutils(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("SideBarOutils")

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

        self.label_type = QLabel("Type")

        # Styles
        self.label_download.setObjectName("Titre")
        self.label_type.setObjectName("Titre")

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

        self.disposition.addWidget(self.label_type)

        self.disposition.addStretch(1)
        self.disposition.addWidget(self.btn_show_hide, 1, Qt.AlignmentFlag.AlignRight)

        self.switch_visible()

    def switch_visible(self):
        self.visible = not self.visible

        if self.visible:
            self.btn_show_hide.setIcon(icones["show"])
            self.setFixedWidth(250)

            for widget in (self.label_titre, self.label_outils, self.label_download, self.widget_download, self.label_type):
                widget.show()
            self.icon_titre.hide()
        else:
            self.btn_show_hide.setIcon(icones["hide"])
            self.setFixedWidth(50)

            for widget in (self.label_titre, self.label_outils, self.label_download, self.widget_download, self.label_type):
                widget.hide()
            self.icon_titre.show()


class WidgetDownload(QWidget):
    def __init__(self, parent: SideBarOutils):
        super().__init__()
        self.parent = parent 

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

    def download_url(self):
        return 
        self.btn_download.setEnabled(False)
        print("-"*50)
        gestion_processus.download_lot(self.line_edit.text())

