from ArkMage.image import ouvrir_image, Pixels
from ArkMage.commun import conversion_gris

import plotly.graph_objects as go

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
