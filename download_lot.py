from playwright.sync_api import sync_playwright
import time

def appuie_bouton(xpath_bouton: str, page):
    prefixe_xpath = 'xpath='

    page.wait_for_selector(prefixe_xpath + xpath_bouton, timeout=5000)
    input_element = page.query_selector(prefixe_xpath + xpath_bouton)

    if input_element:
        input_element.click()
        return True
    return False

def lancer_playwright(url: str):
    with sync_playwright() as playwright:
        with playwright.firefox.launch(headless=False) as navigateur:
            page = navigateur.new_page(java_script_enabled=True)
            page.goto(url, wait_until='load')

            reussite = appuie_bouton("//input[@value='Accepter']", page)

            # reussite = appuie_bouton("//button[@title='Télécharger le média']", page)
            reussite = appuie_bouton("//button[@title='Suivant']", page)
            time.sleep(1)
            reussite = appuie_bouton("//button[@title='Suivant']", page)

            time.sleep(10)
            page.close()

if __name__ == '__main__':
    url = "https://archives.calvados.fr/ark:/52329/n3k0sc9271m4/37608725-c493-48cc-bd5e-1e7bfd10aeaa"

    lancer_playwright(url)