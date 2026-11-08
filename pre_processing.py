import plotly.graph_objects as go
import plotly.express as px

import numpy as np
from numba import njit

from ArkMage.image import ouvrir_image, Pixels
from ArkMage.commun import conversion_gris
from ArkMage.commun import flou_classique

def calcul_histogramme(data):
    unique, occurrences = np.unique(data, return_counts=True)

    dicogramme = dict(zip(unique, occurrences))
    histogramme = []
    for luma in range(256):
        occurence = dicogramme.get(luma, 0)

        histogramme.append(int(occurence))
    return histogramme

def afficher_histogramme(histogramme, seuil=200):
    couleurs = ['lightslategray', ] * 256
    couleurs[seuil] = 'crimson'

    figure = go.Figure(data=[go.Bar(
        x=list(range(256)),
        y=histogramme,
        marker_color=couleurs
    )])
    figure.write_html("graphiques\\histogramme.html")

def afficher_distribution(liste_distribution):
    figure = px.line(x=list(range(256)), y=liste_distribution)
    figure.write_html("graphiques\\distribution.html")

def calcul_sommes(histogramme):
    liste_sommes, liste_nb = [], []
    nb_avant, somme_avant = 0, 0

    for seuil in range(256):
        nb = histogramme[seuil]
        somme_avant += seuil * nb
        liste_sommes.append(somme_avant)

        nb_avant += nb
        liste_nb.append(nb_avant)
    return liste_sommes, liste_nb

def seuil_otsu(histogramme: list, nb_pixels: int):
    # On cherche le meilleur seuil avec la méthode d'Otsu

    liste_sommes, liste_nb = calcul_sommes(histogramme)
    meilleur_seuil, distribution_meilleur = 0, 0
    distributions = [0]

    for seuil in range(1, 255):
        somme_gauche = liste_sommes[seuil]
        somme_droit  = liste_sommes[-1] - somme_gauche

        nb_gauche = liste_nb[seuil]
        proba_gauche = nb_gauche / nb_pixels

        moyenne_gauche = somme_gauche / nb_gauche if nb_gauche != 0 else 0
        moyenne_droit  = somme_droit / (nb_pixels - nb_gauche) if nb_gauche != nb_pixels else 0

        distribution = proba_gauche * (1-proba_gauche) * (moyenne_gauche - moyenne_droit)**2
        distributions.append(distribution)

        if distribution_meilleur < distribution:
            distribution_meilleur = distribution
            meilleur_seuil = seuil

    distributions.append(0)
    afficher_distribution(distributions)

    return meilleur_seuil

def calcul_seuil(zone):
    histogramme = calcul_histogramme(zone)

    seuil = int(seuil_otsu(histogramme, zone.size))
    afficher_histogramme(histogramme, seuil)
    return seuil

def conversion_binaire(pixels):
    data_255 = (pixels.data * 255).astype(np.uint8)
    seuil = (calcul_seuil(data_255) + data_255.std()) / 255

    data_saillance = calcul_distances(pixels.data[:, :, 0].astype(np.float64)) > 43
    data_seuil = pixels.data[:, :, 0] < seuil

    Pixels(data_seuil, "B").show()

    data_binaire = np.logical_or(data_seuil, data_saillance)
    return Pixels(data_binaire, "B")

@njit
def calcul_distances(data):
    dimensions = data.shape
    w, h = dimensions
    data_distances = np.zeros(dimensions)

    for x in range(1, w):
        for y in range(1, h):
            teinte = data[x, y]

            d1 = np.abs(teinte - data[x - 1, y])
            d2 = np.abs(teinte - data[x, y - 1])
            d3 = np.abs(teinte - data[x - 1, y - 1])

            data_distances[x, y] = (d1 + d2 + d3)

    return data_distances

def saillance(pixels):
    data_saillance = calcul_distances(pixels.data.astype(np.float64))

    return Pixels(data_saillance, "L")

if __name__ == '__main__':
    pixels = ouvrir_image()
    pixels = conversion_gris(pixels)
    pixels = flou_classique(pixels, 1)

    pixels = conversion_binaire(pixels)
    pixels.show()
