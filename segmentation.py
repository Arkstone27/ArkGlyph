import numpy as np

from socle import *
from numba import njit

@njit
def teinte_gris(couleur):
    return couleur[0]*0.299 + couleur[1]*0.587 + couleur[2]*0.114

def conversion_gris(pixels):
    pixels_gris = pixels.appliquer(teinte_gris)
    pixels_gris.data = pixels_gris.data[:,:,0].astype(np.int8)
    pixels_gris.mode_couleur = "L"

    return pixels_gris

def flou_classique(pixels, rayon: int):
    longueur_noyau = rayon*2+1
    noyau = np.ones((longueur_noyau, longueur_noyau))

    taille_noyau = longueur_noyau*longueur_noyau
    @njit
    def division_flou(somme):
        return somme / taille_noyau

    pixels_flou = pixels.convolution(noyau, division_flou)

    return pixels_flou

voisins = [(x, y) for x in range(3) for y in range(3)]
voisins.remove((1,1))
voisins = tuple(voisins)

@njit
def calcul_distance_loki(fenetre, voisins=voisins):
    centre = fenetre[1, 1]
    somme = 0

    for x, y in voisins:
        somme += centre - fenetre[x, y]

    return somme

@njit
def loki_fast(data_pad, dimensions):
    w, h = dimensions
    data_loki = np.empty(dimensions, np.int16)

    for x in range(w):
        for y in range(h):
            somme = calcul_distance_loki(data_pad[x:x+3, y:y+3])
            data_loki[x, y] = somme

    return data_loki

def afficher_loki(data_loki):
    w, h = data_loki.shape
    distance_min = data_loki.min()
    diviseur = data_loki.max() - distance_min

    @njit
    def normaliser(distance_loki):
        return (distance_loki - distance_min) / diviseur * 255

    data_loki = appliquer_fast(data_loki, normaliser).astype(np.uint8) < 90
    Pixels(data_loki, "B").show()

def conversion_loki(pixels):
    """
    Chaque pixel à pour valeur sa différence avec ses voisins (pas la distance)
    """
    data_pad = np.pad(pixels.data, 1, "edge")
    data_loki = loki_fast(data_pad, pixels.data.shape)

    afficher_loki(data_loki)

if __name__ == '__main__':
    pixels = ouvrir_image()
    pixels = conversion_gris(pixels)
    pixels = flou_classique(pixels, 1)

    conversion_loki(pixels)
