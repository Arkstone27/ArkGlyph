from pathlib import Path
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QFontDatabase ,QIcon, QBrush, QColor, QPen, QPainter
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer

palette = {
    "pbgdark": "#0e0e11",
    "pbgall": "#18181b",
    "pbglight": "#303035",

    "ptextsimple": "#ededee",
    "ptextmuted": "#69696f",
    "pborder": "#232326",
    "pseparator": "#303035",

    "pgradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #303035, stop:1 #18181b)",

    "pprimary": "#6b32f5",
    "psecondary": "#e5ff90",
    "pprimlight": "#7b55fd",
    "pred": "#f36259"
}

def application_palette():
    with open(Path("interface") / "stylecopie.qss", "r") as f:
        _style = f.read()

    for nom_couleur, hexa_couleur in palette.items():
        _style = _style.replace(nom_couleur, hexa_couleur)

    with open("style.qss", "w") as f:
        f.write(_style)

def chargement_fonts():
    chemin_dossier = Path("resources") / "fonts"

    for nom_font in ("JetBrainsMono-Regular.ttf", "JetBrainsMonoNL-Bold.ttf", "JetBrainsMonoNL-Italic.ttf"):
        QFontDatabase.addApplicationFont(str(chemin_dossier / nom_font))

icones = dict()
chemins_icones = (Path("interface") / "resources" /"dark-icons").glob("*.svg")

for chemin_icone in chemins_icones:
    icones[chemin_icone.name.replace(".svg", "")] = QIcon(str(chemin_icone))

def creation_brush_pen_zone(r, v, b):
    return QBrush(QColor(r, v, b, 100)), QPen(QColor(r,v,b), 2)

couleurs = ((67, 48, 117), (103, 48, 117), (48, 62, 117), (48, 97, 117), (117, 48, 97), (48, 117, 102), (117, 48, 62))
couleurs_zones = [creation_brush_pen_zone(*couleur) for couleur in couleurs]
couleurs_hexs = [QColor(*couleur, 100).name()  for couleur in couleurs]

class IconLabel(QWidget):
    def __init__(self, icon: QIcon, texte: str, height: int, nom: str="texte"):
        super().__init__()

        pixmap = icon.pixmap(height, height)
        label_pixmap = QLabel()
        label_pixmap.setPixmap(pixmap)

        self.label = QLabel(texte)
        self.label.setObjectName(nom)

        disposition = QHBoxLayout(self)
        disposition.setContentsMargins(0, 0, 0, 0)

        disposition.addWidget(label_pixmap)
        disposition.addWidget(self.label)
        disposition.addStretch(1)

class Icon(QLabel):
    def __init__(self, icon: QIcon, height: int):
        super().__init__()

        pixmap = icon.pixmap(height, height)
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class IconLabels(QWidget):
    def __init__(self, icons_textes: list[str|QIcon], noms: list[str], height: int):
        super().__init__()
        liste_labels = list()
        for icon_texte, nom in zip(icons_textes, noms):
            label = QLabel()
            if isinstance(icon_texte, str):
                label.setText(icon_texte)
                if "<a href=" in icon_texte:
                    label.setOpenExternalLinks(True) # Support des liens
            else:
                pixmap = icon_texte.pixmap(height, height)
                label.setPixmap(pixmap)

            label.setObjectName(nom)
            liste_labels.append(label)

        # Disposition
        self.disposition = QHBoxLayout(self)

        for label in liste_labels:
            self.disposition.addWidget(label)

        self.disposition.addStretch(1)

class SvgWidget(QWidget):
    def __init__(self, chemin_svg, taille, parent=None):
        super().__init__(parent)

        self.rendu = QSvgRenderer(chemin_svg, self)
        self.rendu.setAspectRatioMode(Qt.KeepAspectRatio)
        self.rendu.repaintNeeded.connect(self.update)

        self.setFixedSize(taille, taille)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.rendu.render(painter, self.rect())
        painter.end()

    def sizeHint(self):
        return self.rendu.defaultSize()