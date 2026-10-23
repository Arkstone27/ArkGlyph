from pathlib import Path

from PySide6.QtGui import QPixmap

class Lot:
    def __init__(self, chemin_lot: Path):
        self.chemin_lot = chemin_lot
        self.chemins_pages = list(self.chemin_lot.glob("*.jpg"))
        self.chemins_pages.sort(key=lambda chemin_page: int(chemin_page.stem))

        self.nb_pages = len(self.chemins_pages)
        self.nom = remplacer(self.chemin_lot.name)

def remplacer(nom_lot):
    return nom_lot.replace("~", "/")

def get_lots_saved():
    chemin_lots = Path("Lots_ArchLate")
    chemins_lot = [chemin_lot for chemin_lot in chemin_lots.iterdir() if chemin_lot.is_dir()]

    return chemins_lot, [remplacer(chemin_lot.name) for chemin_lot in chemins_lot]

if __name__ == '__main__':
    chemins_lot, noms_lots = get_lots_saved()
    print(chemins_lot, noms_lots)

    lot_1 = Lot(chemins_lot[0])
    print(lot_1.chemins_pages[0].resolve())
    print(lot_1.nom)
