from playwright.sync_api import sync_playwright
import requests

from pathlib import Path
from Lot import creation_json

def is_valide(url: str):
    try:
        reponse = requests.head(url, timeout=5, allow_redirects=True)
        return 200 <= reponse.status_code < 300
    except requests.RequestException:
        return False

def appuie_bouton(xpath_bouton: str, page):
    prefixe_xpath = 'xpath='

    locator = page.locator(prefixe_xpath + xpath_bouton)
    locator.wait_for(state="visible", timeout=5000)

    locator.click()

def download_lot(url_lot: str, signaux):
    if not is_valide(url_lot):
        signaux.fin.emit(False, f"L'url : '{url_lot}' n'est pas valide ou n'existe pas")
        return
    try:
        existant, nom_lot = ouverture_navigateur(url_lot, signaux)

    except Exception as e:
        signaux.fin.emit(False, f"Erreur pendant le téléchargement du lot : \n {e}")
        return
    if existant:
        signaux.fin.emit(False, f"Le lot : '{nom_lot}' existe déjà : \n {url_lot=}")
    else:
        signaux.fin.emit(True, f"Téléchargement reussie du lot : '{nom_lot}'")

def ouverture_navigateur(url_lot: str, signaux):

    with sync_playwright() as playwright:
        with playwright.firefox.launch(headless=True) as navigateur:
            contexte = navigateur.new_context()
            page = contexte.new_page()

            signaux.status.emit("Ouverture de la page... ", 0)
            page.goto(url_lot, wait_until='load')

            signaux.status.emit("Ouverture de la visionneuse...", 0)
            if page.content()[27] == "c":
                page_visio = ouvre_visionneuse(page, contexte)
            else:
                page_visio = page

            nb_pages, nom_lot = preparation_page(page_visio)
            existant, chemin_lot = creer_dossier(nom_lot, signaux)
            if existant:
                return True, nom_lot

            signaux.status.emit(f"Téléchargement de la page 1/{nb_pages}...", 0)
            save_img(page_visio, chemin_lot, 1)
            for n_page in range(2, nb_pages+1):
                appuie_bouton("//button[@title='Suivant' and not(contains(@class, 'disabled'))]", page_visio)
                signaux.status.emit(f"Téléchargement de la page {n_page}/{nb_pages}...", 0)
                save_img(page_visio, chemin_lot, n_page)
            page_visio.close()
            page.close()

            creation_json(chemin_lot, url_lot)
    return False, nom_lot

def ouvre_visionneuse(page, contexte):
    with contexte.expect_page() as page_visio_info:
        lien_visionneuse = page.get_by_role("link", name="Tout afficher")
        lien_visionneuse.wait_for(state="visible", timeout=10000)
        lien_visionneuse.click()
    page_visio = page_visio_info.value
    page_visio.wait_for_load_state()

    return page_visio

def preparation_page(page_visio):
    # Initialisation
    appuie_bouton("//input[@value='Accepter']", page_visio)
    appuie_bouton("//button[@title='Premier' and not(contains(@class, 'disabled'))]", page_visio)

    # Nombre de pages (images)
    texte_count = page_visio.locator("xpath=//span[contains(@class, 'page-count')]").text_content()
    nb_pages = int(texte_count[2:])

    # Nom du lot
    texte_year = page_visio.locator("xpath=//span[contains(@class, 'record-title')]").text_content()
    texte_reference = page_visio.locator("xpath=//span[contains(@class, 'reference-code')]").text_content()
    nom_lot = f"{texte_year} - {texte_reference}"

    return nb_pages, nom_lot

def creer_dossier(nom_lot, signaux):
    nom_dossier = nom_lot.replace("/", "~").replace(":", "#")
    chemin_lot = Path("Lots_ArchLate") / nom_dossier
    if chemin_lot.is_dir():
        return True, ""
    signaux.status.emit(f"Création du dossier : {nom_dossier}...", 0)
    chemin_lot.mkdir()

    return False, chemin_lot

def save_img(page_visio, chemin_lot, n_page):
    with page_visio.expect_download() as info_img:
        appuie_bouton("//button[@title='Télécharger le média' and not(contains(@class, 'disabled'))]", page_visio)
        chemin_fichier = (chemin_lot / f"{n_page}.jpg")

        info_img.value.save_as(chemin_fichier.resolve())

def creation_dossier_lots():
    chemin_lots = Path("Lots_ArchLate")

    if chemin_lots.is_dir() :
        return
    chemin_lots.mkdir()

creation_dossier_lots()

if __name__ == '__main__':
    url = "https://archives.calvados.fr/ark:/52329/2637kfglmnz5"
    # url = "https://archives.calvados.fr/ark:/52329/7mjpxsw1b3vc/9be33799-7f59-4169-b614-9f2f9c91cf53"
    print(is_valide(url))