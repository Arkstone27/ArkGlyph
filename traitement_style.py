from pathlib import Path
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QFontDatabase ,QIcon

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
    with open("stylecopie.qss", "r") as f:
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
chemins_icones = (Path("resources") / "dark-icons").glob("*.svg")

for chemin_icone in chemins_icones:
    icones[chemin_icone.name.replace(".svg", "")] = QIcon(str(chemin_icone))

class IconLabel(QWidget):

    def __init__(self, icon: QIcon, texte: str, height: int, nom: str="texte"):
        super().__init__()

        pixmap = icon.pixmap(height, height)
        label_pixmap = QLabel()
        label_pixmap.setPixmap(pixmap)

        label = QLabel(texte)
        label.setObjectName(nom)

        disposition = QHBoxLayout(self)
        disposition.setContentsMargins(0, 0, 0, 0)

        disposition.addWidget(label_pixmap)
        disposition.addWidget(label)
        disposition.addStretch(1)
