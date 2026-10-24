from tkinter.ttk import Treeview

from playwright.sync_api import sync_playwright
import requests

from pathlib import Path

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

def download_lot(url_lot: str):
    if not is_valide(url_lot):
        return False, f"L'url : '{url_lot}' n'est pas valide ou n'existe pas"

    try:
        existant, nom_lot = ouverture_navigateur(url_lot)

    except Exception as e:
        return False, f"Erreur pendant le téléchargement du lot : '{nom_lot}' \n {e}"
    if existant:
        return False, f"Le lot : '{nom_lot}' existe déjà : \n {url_lot=}"
    return True, f"Téléchargement reussie du lot : '{nom_lot}'"

def ouverture_navigateur(url_lot: str):

    with sync_playwright() as playwright:
        with playwright.firefox.launch(headless=False) as navigateur:
            contexte = navigateur.new_context()
            page = contexte.new_page()
            print("Ouverture de la page... ")
            page.goto(url_lot, wait_until='load')
            page_visio = ouvre_visionneuse(page, contexte)

            nb_pages, nom_lot = preparation_page(page_visio)
            existant, chemin_lot = creer_dossier(nom_lot)
            if existant:
                return True, nom_lot
            print("Téléchargement de la page 1...")
            save_img(page_visio, chemin_lot, 1)
            for n_page in range(2, nb_pages+1):
                appuie_bouton("//button[@title='Suivant' and not(contains(@class, 'disabled'))]", page_visio)
                print(f"Téléchargement de la page {n_page}...")
                save_img(page_visio, chemin_lot, n_page)
            page_visio.close()
            page.close()
    return False, nom_lot

def ouvre_visionneuse(page, contexte):
    with contexte.expect_page() as page_visio_info:
        lien_visionneuse = page.get_by_role("link", name="Tout afficher")
        lien_visionneuse.wait_for(state="visible", timeout=10000)
        lien_visionneuse.click()
    page_visio = page_visio_info.value
    print("Ouverture de la visionneuse...")
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

def creer_dossier(nom_lot):
    nom_dossier = nom_lot.replace("/", "~")
    chemin_lot = Path("Lots_ArchLate") / nom_dossier
    if chemin_lot.is_dir():
        return True, ""
    print(f"Création du dossier : {nom_dossier}...")
    chemin_lot.mkdir()

    return False, chemin_lot

def save_img(page_visio, chemin_lot, n_page):
    with page_visio.expect_download() as info_img:
        appuie_bouton("//button[@title='Télécharger le média' and not(contains(@class, 'disabled'))]", page_visio)
        chemin_fichier = (chemin_lot / f"{n_page}.jpg")

        info_img.value.save_as(chemin_fichier.resolve())

if __name__ == '__main__':
    url = "https://archives.calvados.fr/ark:/52329/2637kfglmnz5"
    print(is_valide(url))
    print(download_lot(url)[1])