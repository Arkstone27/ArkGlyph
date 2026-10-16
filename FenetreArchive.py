from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QLabel, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QPixmap

class FenetreArchive(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        # Widgets
        self.tabs = QTabWidget(self, movable=True, tabsClosable=True)

        self.onglet1 = OngletLot(self)
        self.tabs.addTab(self.onglet1, "Onglet1")

        self.onglet2 = QLabel("Test onglet2")
        self.tabs.addTab(self.onglet2, "Onglet2")

        # Disposition
        self.disposition =QVBoxLayout(self)
        self.disposition.addWidget(self.tabs)

class OngletLot(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()

        # Scene
        self.scene = QGraphicsScene()
        self.scene.addPixmap(QPixmap("archives/image_test.jpg"))

        self.setScene(self.scene)

        print(self.alignment())