import tkinter as tk
from tkinter import simpledialog, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import time
import sys  # Importez sys pour utiliser sys.exit()

def recherche_wikipedia(term, historiqueUrls, motsVisites):
    driver = webdriver.Chrome()
    driver.get(f"https://fr.wikipedia.org/wiki/{term}")
    historiqueUrls.append(driver.current_url)

    try:
        while not "/Philosophie" in driver.current_url:
            links_found = False
            for i in range(1, 4):  # Essayez les paragraphes 1 à 3
                paragraph_links = driver.find_elements(By.XPATH, f'//*[@id="mw-content-text"]/div[1]/p[{i}]//a')
                print(paragraph_links)
                if paragraph_links == []:
                    driver.back()
                    links_found = True
                    break
                for link in paragraph_links:
                    href = link.get_attribute('href')
                    # Vérifie si le href contient 'wikipedia.org/wiki', n'inclut pas 'wiktionary', ':' et '.'
                    if href and "wikipedia.org/wiki" in href and "wiktionary" not in href and '.ogg' not in href:
                        if link.text and link.text not in motsVisites:
                            motsVisites.add(link.text)
                            print(f"Clique sur : {link.text}")
                            link.click()
                            time.sleep(1)  # Attendez pour que la page charge
                            historiqueUrls.append(driver.current_url)
                            links_found = True
                            break  # Sortez de la boucle interne après avoir cliqué sur un lien
                if links_found:
                    break  # Sortez de la boucle externe si un lien a été cliqué
            if not links_found:
                print("Aucun nouveau lien trouvé. Arrêt du script.")
                break  # Arrêtez le script si aucun lien n'a été trouvé dans les paragraphes vérifiés
    finally:
        driver.quit()

def afficher_resultats(historiqueUrls, motsVisites):
    result_window = tk.Tk()
    result_window.title("Résultats de la recherche Wikipedia")

    # Gérer la fermeture de la fenêtre pour terminer le programme
    result_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10)

    for url in historiqueUrls:
        text_area.insert(tk.INSERT, url + '\n')
    text_area.insert(tk.INSERT, f"\nNombre total de pages visitées : {len(historiqueUrls)}")
    text_area.insert(tk.INSERT, f"\nMots visités : {', '.join(motsVisites)}")

    result_window.mainloop()

def demande_et_recherche():
    root = tk.Tk()
    root.withdraw()  # Ne pas afficher la fenêtre racine
    term = simpledialog.askstring("Recherche Wikipedia", "Entrez un terme à rechercher :")
    if term:
        historiqueUrls = []
        motsVisites = set()
        recherche_thread = threading.Thread(target=recherche_wikipedia, args=(term, historiqueUrls, motsVisites), daemon=True)
        recherche_thread.start()
        root.after(100, lambda: recherche_thread.join() if not recherche_thread.is_alive() else root.after(100, lambda: afficher_resultats(historiqueUrls, motsVisites)))
        root.mainloop()

if __name__ == "__main__":
    demande_et_recherche()
