from ArkMage.commun import conversion_gris
from ArkMage.image import ouvrir_image, Pixels
from ArkMage.resize import conservation_ratio, resize_simple
from ArkMage.rotation import rotation_fast
from ArkMage.scaling import meilleur_winsorisation
from ArkMage.stats_data import Stats_Data

import plotly.graph_objects as go
from time import perf_counter

from numba import njit, prange
import numpy as np

@njit(parallel=True)
def histogramme_vertical_fast(data):
    w, h, n = data.shape

    histogramme = np.zeros(w, dtype=np.float64)
    for x in prange(w):
        for y in range(h):
            histogramme[x] += data[x, y, 0]

    histogramme -= histogramme.min()
    return histogramme

def histogramme_vertical(pixels: Pixels):
    histogramme = histogramme_vertical_fast(pixels.data)
    return histogramme

@njit(parallel=True)
def histogramme_horizontale_fast(data):
    w, h, n = data.shape

    histogramme = np.zeros(h, dtype=np.float64)
    for x in prange(w):
        for y in range(h):
            histogramme[y] += data[x, y, 0]

    histogramme -= histogramme.min()
    return histogramme

def histogramme_horizontale(pixels: Pixels):
    histogramme = histogramme_horizontale_fast(pixels.data)
    return histogramme

def afficher_histogramme(histogramme):
    w = histogramme.shape[0]
    couleurs = ['lightslategray', ] * w

    figure = go.Figure(data=[go.Bar(
        x=list(range(w)),
        y=histogramme,
        marker_color=couleurs
    )])
    figure.write_html("graphiques\\histogramme_vertical.html")
@njit
def somme_erreur(histogramme):
    h = histogramme.shape[0]

    erreur = 0
    for indice in range(1, h):
        erreur += abs(histogramme[indice, 0, 0] - histogramme[indice-1, 0, 0])
    return erreur

def calcul_erreur_orientation(data):
    histogramme = histogramme_vertical_fast(data)
    histogramme = meilleur_winsorisation(Stats_Data(histogramme[:, np.newaxis, np.newaxis].astype(np.float32, copy=False)))

    return somme_erreur(histogramme)

def find_best_rotation(data, nb_test=10):
    angle, ecart = 0.0, 2
    erreur_angle = calcul_erreur_orientation(data)

    for _ in range(nb_test):
        angle_1 = angle + ecart
        erreur_1 = calcul_erreur_orientation(rotation_fast(data, angle_1))

        if erreur_1 > erreur_angle:
            angle, erreur_angle = angle_1, erreur_1
        else:
            angle_2 = angle - ecart
            erreur_2 = calcul_erreur_orientation(rotation_fast(data, angle_2))

            if erreur_2 > erreur_angle:
                angle, erreur_angle = angle_2, erreur_2
        ecart /= 2

    return angle

def correction_rotation(data, data_fullsize):
    angle = find_best_rotation(data)

    return rotation_fast(data_fullsize, angle)

@njit
def coupure_optimale(data):
    w, h, n = data.shape
    return h//2

def coupure_img(data, data_analyse): # Si l'image a 2 pages on coupe au milieu avant de corriger la rotation
    w, h, n_canaux = data.shape
    w_analyse = data_analyse.shape[0]

    indice_coupure_analyse = coupure_optimale(data_analyse)
    indice_coupure = round(indice_coupure_analyse * w/w_analyse)

    data_coupure = np.empty((w, h, n_canaux), dtype=np.float32)
    # Page Gauche
    data_coupure[:, :indice_coupure, :] = correction_rotation(data_analyse[:, :indice_coupure_analyse, :],
                                                      data[:, :indice_coupure, :])
    # Page Droite
    data_coupure[:, indice_coupure:, :] = correction_rotation(data_analyse[:, indice_coupure_analyse:, :],
                                                      data[:, indice_coupure:, :])
    return data_coupure

def preparation_img(chemin):
    pixels = ouvrir_image(chemin)
    debut = perf_counter()
    w, h, n = pixels.data.shape
    pixels_analyse =  conversion_gris(resize_simple(pixels, *conservation_ratio(500, 0, pixels))) # La taille de l'image est réduite

    if w < h:
        data = coupure_img(pixels.data, pixels_analyse.data)
    else:
        data = correction_rotation(pixels_analyse.data, pixels.data)

    pixels = Pixels(data, pixels.mode_couleur)
    print(perf_counter() - debut)
    pixels.show()
    # pixels.sauvegarde(chemin.replace(".jpg", ".jxl"))


if __name__ == '__main__':
    preparation_img("")
    preparation_img("")
