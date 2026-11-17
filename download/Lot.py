from pathlib import Path
import json

from PIL import Image
import numpy as np

class Lot:
    def __init__(self, chemin_lot: Path):
        self.chemin_lot = chemin_lot
        self.chemins_pages = None

        self.nb_pages = len(list(self.chemin_lot.glob("*.jpg")))
        self.nom = remplacer(self.chemin_lot.name)
        self.get_data_json()

    def get_data_json(self):
        with open(self.chemin_lot / "data.json", "r", encoding="utf-8") as fichier:
            data = json.load(fichier)

        self.width_max, self.height_max = data["width_max"], data["height_max"]
        self.url = data["url"]
        if data["page_data"] is None:
            self.page_data = None
        else:
            self.page_data = np.array([(data["page_data"] >> i) & 1 for i in range(self.nb_pages)], dtype=bool)
        self.lot_process = self.width_max is not None # Si le lot à déjà été traité
   
    def get_chemins_pages(self):
        if self.chemins_pages is None:
            self.chemins_pages = list(self.chemin_lot.glob("*.jpg"))
            self.chemins_pages.sort(key=lambda chemin_page: int(chemin_page.stem))
        return self.chemins_pages

def post_traitement(lot):
    width_max, height_max = 0, 0
    page_data = np.ones(lot.nb_pages, dtype=bool)

    # Recherche des dimensions maximales
    for chemin_page in lot.chemins_pages:
        img = Image.open(chemin_page)
        w, h = img.size

        if w > width_max:width_max = w
        if h > height_max:height_max = h

    # Disqualification des images 2x plus petite que le max
    nb_pixels = (width_max*height_max) / 2
    for indice, chemin_page in enumerate(lot.chemins_pages):
        img = Image.open(chemin_page)
        w, h = img.size

        if w*h < nb_pixels:
            page_data[indice] = False

    packed_byte_array = np.packbits(page_data.astype(np.uint8))
    page_data_int = int.from_bytes(packed_byte_array, byteorder="big")

    creation_json(lot.chemin_lot, lot.url, width_max, height_max, page_data_int)
    lot.get_data_json()

def remplacer(nom_lot):
    return nom_lot.replace("~", "/").replace("#", ":")

def get_lots_saved(lots_show: list[Lot]):
    chemins_lot_show = [lot.chemin_lot for lot in lots_show]

    chemins_lot = [chemin_lot for chemin_lot in chemin_lots.iterdir() if (chemin_lot.is_dir() and not chemin_lot in chemins_lot_show)]
    lots = [Lot(chemin_lot) for chemin_lot in chemins_lot]
    return lots + lots_show

def creation_json(chemin_lot: Path, url_lot: str, width_max=None, height_max=None, page_data=None):
    data = {
        "width_max": width_max,
        "height_max": height_max,
        "url": url_lot,
        "page_data": page_data # Les pages à lire
    }

    with open(chemin_lot / "data.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier, indent=4, ensure_ascii=False)

chemin_lots = Path("Lots_ArchLate")


if __name__ == '__main__':
    chemins_lot, noms_lots = get_lots_saved(list())
    print(chemins_lot, noms_lots, "\n")

    if  chemins_lot:
        creation_json(chemins_lot[0], "www.test.com")

        lot_1 = Lot(chemins_lot[0])
        print(lot_1.chemins_pages[0].resolve(), "\n")
        print(lot_1.chemins_pages, "\n")

        post_traitement(lot_1)
        print(lot_1.nom, lot_1.page_data, lot_1.width_max, lot_1.height_max)


