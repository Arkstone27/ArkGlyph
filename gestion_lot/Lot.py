from pathlib import Path
import json

from time import time, localtime
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
        self.date_download = data["date_download"]
        self.url = data["url"]
        self.date_download = data["date_download"]

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

def clean_date(date_download): # A refaire
    date_actuel = localtime()
    date = localtime(date_download)

    if date_actuel.tm_year != date.tm_year:
        return f"{date_actuel.tm_year - date.tm_year}a"
    elif date_actuel.tm_mon != date.tm_mon:
        return f"{date_actuel.tm_mon - date.tm_mon}m"
    elif date_actuel.tm_mday != date.tm_mday:
        return f"{date_actuel.tm_mday - date.tm_mday}j"
    elif date_actuel.tm_hour != date.tm_hour:
        return f"{date_actuel.tm_hour - date.tm_hour}h"
    elif date_actuel.tm_min != date.tm_min:
        return f"{date_actuel.tm_min - date.tm_min}min"
    return f"{date_actuel.tm_sec - date.tm_sec}s"


def clean_url(url: str):
    idx_debut = url.find("//") + 1
    url = url[idx_debut+1:]
    idx_fin_slash = url.find("/")
    idx_debut_slash = url[::-1].find("/")
    
    if idx_fin_slash == -1 or url.count("/") == 1:
        return url
    return f"{url[:idx_fin_slash]}/.../{url[-idx_debut_slash:]}"

def clean_nom(lot: Lot):
    nom = lot.nom
    indice_tiret = len(nom) - nom[::-1].find("-")

    if len(nom[:indice_tiret]) < 12:
        return nom
    return f"{nom[:6]}... -{nom[indice_tiret:]}"

def trie_lots(lots: list[Lot], type_trie: str):
    reverse = True
    if type_trie == "pages":
        key = lambda lot: lot.nb_pages
        
    elif type_trie == "nom":
        key = lambda lot: lot.nom
        reverse = False
    else:
        key = lambda lot: lot.date_download
    lots.sort(key=key, reverse=reverse)

def get_lots_saved(lots_show: list[Lot], type_trie: str="nb_pages"):
    chemins_lot_show = [lot.chemin_lot for lot in lots_show]

    chemins_lot = [chemin_lot for chemin_lot in chemin_lots.iterdir() if (chemin_lot.is_dir() and not chemin_lot in chemins_lot_show)]
    lots = [Lot(chemin_lot) for chemin_lot in chemins_lot] + lots_show
    trie_lots(lots, type_trie)
    return lots

def creation_json(chemin_lot: Path, url_lot: str, width_max=None, height_max=None, page_data=None):
    data = {
        "width_max": width_max,
        "height_max": height_max,
        "url": url_lot,
        "page_data": page_data, # Les pages à lire
        "date_download": time()
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


