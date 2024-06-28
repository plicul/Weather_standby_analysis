import sys
import logging

from PySide6 import QtWidgets

from MyWidget import MyWidget
from db import connectToDatabase
from utils import seaDataToExcel

logging.basicConfig(filename="app.log", level=logging.DEBUG)
logger = logging.getLogger("logger")


if __name__ == "__main__":
    seaDataToExcel()
    app = QtWidgets.QApplication([])
    if not connectToDatabase():
        sys.exit(1)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()


    sys.exit(app.exec())
