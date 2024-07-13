from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QVBoxLayout


class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.name = "Introduction"
        label = QtWidgets.QLabel("Weather Standby Analysis")
        layout.addWidget(label)
        self.setLayout(layout)