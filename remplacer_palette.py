palette = {
    "@bgdark": "#0e0e11",
    "@bgall": "#18181b",
    "@bglight": "#303035",

    "@textsimple": "#ededee",
    "@textmuted": "#69696f",
    "@border": "#232326",
    "@separator": "#303035",

    "@gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #303035, stop:1 #18181b)",

    "@primary": "#6b32f5",
    "@secondary": "#e5ff90",
    "@primlight": "#7b55fd",
    "@red": "#f36259"
}

with open("stylecopie.qss", "r") as f:
    _style = f.read()

for nom_couleur, hexa_couleur in palette.items():
    _style = _style.replace(nom_couleur, hexa_couleur)

with open("style.qss", "w") as f:
    f.write(_style)