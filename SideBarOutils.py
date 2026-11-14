from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor

from traitement_style import icones, IconLabel

class SideBarOutils(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("SideBarOutils")
        self.setMaximumWidth(300)
        self.setMinimumWidth(50)

        # Widgets
        self.label_titre = IconLabel(icones["logo"], "ArchLate", 20, "Titre")

        self.btn_close = QPushButton()
        self.btn_close.setIcon(icones["hide"])
        self.btn_close.setIconSize(QSize(20,20))
        self.btn_close.setObjectName("Trans")
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

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
        
        self.disposition_titre = QHBoxLayout()
        self.disposition_titre.addWidget(self.label_titre)
        self.disposition_titre.addStretch(1)
        self.disposition_titre.addWidget(self.btn_close)
        self.disposition.addLayout(self.disposition_titre)
        self.disposition.addSpacing(15)

        self.disposition.addWidget(self.label_outils)
        self.disposition.addSpacing(10)

        self.disposition.addWidget(self.label_download)
        self.disposition.addWidget(self.widget_download)
        self.disposition.addSpacing(10)

        self.disposition.addWidget(self.label_type)

        self.disposition.addStretch(1)
        self.setLayout(self.disposition)

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

