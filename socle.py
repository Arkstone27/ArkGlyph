from time import perf_counter
import plotly.express as px

from PIL import Image
from PySide6.QtWidgets import QFileDialog, QApplication
import sys

import math
import numpy as np
from numba import njit

@njit
def fonction_base(somme):
    return somme

class Pixels:
    def __init__(self, data, mode_couleur="RGB"):
        self.data = data.astype(float)
        self.mode_couleur = mode_couleur

    @classmethod
    def img_to_pixels(cls, img):
        data = np.array(img).astype(float)

        return cls(data, img.mode)

    @classmethod
    def creation_vide(cls, dimensions=(32,32), couleur=(255,255,255), mode_couleur="RGB"):
        img = Image.new("RGB", dimensions, (255, 255, 255))

        return cls.img_to_pixels(img)

    def conversion_img(self):
        if self.mode_couleur == "B":
            img_data = self.data * 255
            mode_couleur = "L"
        else:
            img_data = np.clip(self.data, 0, 255)
            mode_couleur = self.mode_couleur

        img_data = img_data.astype(np.uint8)
        return Image.fromarray(img_data, mode=mode_couleur)

    def appliquer(self, fonction):
        new_data = appliquer_fast(self.data, fonction)

        return Pixels(new_data, self.mode_couleur)

    def convolution(self, noyau, fonction=fonction_base):
        new_data = convolution_fast(self.data, noyau, fonction)

        return Pixels(new_data, self.mode_couleur)

    def show(self):
        fig = px.imshow(self.conversion_img(), color_continuous_scale='gray')
        fig.show()

def ouvrir_image(image_test=True):
    if image_test:
        chemin = "archives/image_test.jpg"
    else:
        app = QApplication(sys.argv)
        chemin = QFileDialog.getOpenFileName(None, "Selectionner une image", "", "Images (*.png *.jpg *.jpeg)")[0]

    img = Image.open(chemin)

    if img.mode == "RGBA":
        plan = Image.new("RGB", img.size, (255,255,255))
        plan.paste(img, mask=img.split()[3])

        return Pixels.img_to_pixels(plan)

    return Pixels.img_to_pixels(img)

@njit # On fait une compilation just in time
def appliquer_fast(data, fonction):
    """
    fonction: une fonction décoré avec @njit
    """
    dimensions = data.shape
    w, h = dimensions[0], dimensions[1]
    new_data = np.empty(dimensions)

    for x in range(w):
        for y in range(h):
            new_data[x, y] = fonction(data[x, y])
    return new_data

@njit
def calcul_somme(fenetre, noyau):
    somme = 0.0
    w, h = fenetre.shape[0], fenetre.shape[1]

    for x in range(w):
        for y in range(h):
            somme += fenetre[x, y]*noyau[x, y]
    return somme

@njit
def convolution_fast(data, noyau, fonction=fonction_base):
    dimensions = np.array(data.shape)
    w, h = dimensions[0], dimensions[1]
    new_data = data.copy()

    decalage_x = noyau.shape[0] // 2
    decalage_y = noyau.shape[1] // 2

    for x in range(decalage_x, w - decalage_x):
        for y in range(decalage_y, h-decalage_y):
            fenetre = data[x-decalage_x:x+decalage_x+1, y-decalage_y:y+decalage_y+1]

            somme = calcul_somme(fenetre, noyau)
            new_data[x, y] = fonction(somme)

    return new_data

def mesure_vitesse(fonction, arguments: tuple):
    debut = perf_counter()
    resultat_fonction = fonction(*arguments)

    temps = perf_counter() - debut
    print(f"Le temps d'éxecution est de : {temps}s")

def afficher_fonction(fonction):
    intervalle = [x/10 for x in range(-1000,1000)]

    figure = px.line(x=intervalle, y=[fonction(x) for x in intervalle])
    figure.write_html("graphiques\\graphe_fonction.html")

if __name__ == '__main__':
    facteur = 6
    afficher_fonction(lambda x: math.exp((-x*x)/(facteur*2))/((2*math.pi)**0.5*facteur))

    pixels = ouvrir_image(False)
    pixels.show()
