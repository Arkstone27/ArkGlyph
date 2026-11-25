from ArkMage.commun import conversion_gris
from ArkMage.image import ouvrir_image, Pixels
from ArkMage.resize import conservation_ratio, resize_simple
from ArkMage.rotation import rotation_fast
from ArkMage.scaling import meilleur_winsorisation
from ArkMage.stats_data import Stats_Data

from pathlib import Path

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
    figure.write_html("histo.html")

@njit
def calcul_variance(data):
    histogramme = histogramme_vertical_fast(data)

    return np.var(histogramme)

@njit
def find_best_rotation(data, angle_max=10.0):
    angle_best, variance_max = 0.0, 0.0
    angle = - angle_max

    while angle < angle_max:
        variance = calcul_variance(rotation_fast(data, angle))

        if variance > variance_max:
            variance_max = variance
            angle_best = angle

        angle += 0.2

    return angle_best

def correction_rotation(data, data_fullsize):
    angle = find_best_rotation(data)
    data = rotation_fast(data_fullsize, angle)
    histogramme = histogramme_vertical_fast(data)
    afficher_histogramme(histogramme)

    return data

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
    pixels.data = pixels.data[80:-80, :, :]
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
    # pixels.sauvegarde(chemin)


if __name__ == '__main__':
    preparation_img("")