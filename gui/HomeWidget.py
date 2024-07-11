from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QVBoxLayout


class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QtWidgets.QLabel("Welcome to the Weather Standby Analysis Application")
        layout.addWidget(label)
        self.setLayout(layout)