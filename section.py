import numpy as np
from numba.cuda.nvvmutils import declare_atomic_add_float32

from socle import *
from numba import njit

@njit
def teinte_gris(couleur):
    return couleur[0]*0.299 + couleur[1]*0.587 + couleur[2]*0.114

def conversion_gris(pixels):
    pixels_gris = pixels.appliquer(teinte_gris)
    pixels_gris.data = pixels_gris.data[:,:,0].astype(np.uint8)
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

@njit
def meme_section(teinte_1, teinte_2):
    return np.abs(teinte_1 - teinte_2) < 6

@njit
def calcul_bords(data):
    dimensions = data.shape
    w, h = data.shape
    data_sections = np.empty(dimensions, dtype=np.int64)

    id_groupe = 0
    data_sections[0, 0] = id_groupe

    for x in range(1, w):
        if meme_section(data[x, 0], data[x - 1, 0]):
            data_sections[x, 0] = data_sections[x - 1, 0]
        else:
            id_groupe += 1
            data_sections[x, 0] = id_groupe

    for y in range(1, h):
        if meme_section(data[0, y], data[0, y - 1]):
            data_sections[0, y] = data_sections[0, y - 1]
        else:
            id_groupe += 1
            data_sections[0, y] = id_groupe

    return data_sections, id_groupe

@njit
def simplification_sections(data_sections, equivalences, id_groupe):
    w, h = data_sections.shape

    for section in np.arange(id_groupe):
        section_actuel = section

        while section_actuel != equivalences[section_actuel]:
            section_actuel = equivalences[section_actuel]
        equivalences[section] = section_actuel

    for x in range(w):
        for y in range(h):
            data_sections[x, y] = equivalences[data_sections[x, y]]

@njit
def calcul_sections(data):
    w, h = data.shape
    data_sections, id_groupe = calcul_bords(data)
    equivalences = np.arange(w*h)

    for x in range(1,w):
        for y in range(1, h):
            teinte = data[x, y]

            teinte_haut, section_haut = data[x, y - 1], data_sections[x, y - 1]
            teinte_gauche, section_gauche = data[x - 1, y], data_sections[x - 1, y]

            meme_1 = meme_section(teinte_haut, teinte)
            meme_2 = meme_section(teinte_gauche, teinte)
            if section_haut != section_gauche and meme_1 and meme_2:

                racine_gauche = section_gauche
                while racine_gauche != equivalences[racine_gauche]:
                    racine_gauche = equivalences[racine_gauche]

                racine_haut = section_haut
                while racine_haut != equivalences[racine_haut]:
                    racine_haut = equivalences[racine_haut]

                if racine_haut > racine_gauche:
                    equivalences[racine_haut] = racine_gauche
                    section_haut = racine_gauche
                else:
                    equivalences[racine_gauche] = racine_haut
                    section_gauche = racine_haut

            if meme_1:
                data_sections[x, y] = section_haut
            elif meme_2:
                data_sections[x, y] = section_gauche
            else:
                id_groupe += 1
                data_sections[x, y] = id_groupe

    simplification_sections(data_sections, equivalences, id_groupe)
    return data_sections

@njit
def dessin_sections(affectations):
    dimensions = affectations.shape
    w, h = dimensions
    new_data = np.empty(dimensions, dtype=np.uint8)

    couleurs_sections = np.random.rand(affectations.max()+1) * 255
    couleurs_sections = couleurs_sections.astype(np.uint8)

    for x in range(w):
        for y in range(h):
            new_data[x, y] = couleurs_sections[affectations[x, y]]

    return new_data

def afficher_sections(affectations):
    Pixels(dessin_sections(affectations), "L").show()


def segmentation(pixels):
    data_sections = calcul_sections(pixels.data.astype(np.int16))
    print(data_sections)
    afficher_sections(data_sections)

if __name__ == '__main__':
    pixels = ouvrir_image()

    pixels = conversion_gris(pixels)
    pixels = flou_classique(pixels, 2)
    pixels.show()

    segmentation(pixels)

