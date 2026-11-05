from socle import *
import plotly.graph_objects as go

from numba import njit
import numpy as np

@njit
def teinte_gris(couleur):
    return couleur[0]*0.299 + couleur[1]*0.587 + couleur[2]*0.114

def conversion_gris(pixels):
    pixels_gris = pixels.appliquer(teinte_gris)
    pixels_gris.data = pixels_gris.data[:,:,0].astype(np.uint8)
    pixels_gris.mode_couleur = "L"

    return pixels_gris

@njit
def histogramme_vertical_fast(data):
    w, h = data.shape

    histogramme = np.zeros(h, dtype=np.float64)
    for y in range(h):
        for x in range(w):
            histogramme[y] += data[x, y]
    for y in range(h):
        histogramme[y] = np.sqrt(histogramme[y])
    histogramme -= histogramme.min()
    return histogramme


def histogramme_vertical(pixels: Pixels):
    histogramme = histogramme_vertical_fast(pixels.data)
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


if __name__ == '__main__':
    pixels = ouvrir_image(False)
    pixels  = conversion_gris(pixels)

    histogramme = histogramme_vertical(pixels)
    afficher_histogramme(histogramme)

    pixels.show()
