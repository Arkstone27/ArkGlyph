from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Settings de la fenetre
        self.setWindowTitle("ArchLate")
        self.setMinimumSize(QSize(400,300))

        # Widgets dans la fenetre
        label =  QLabel("Hello")

        # Placement des widgets
        self.setCentralWidget(label) 

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()