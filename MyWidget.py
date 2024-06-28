import random
import logging

from PySide6 import QtWidgets, QtCore

from consts.types import SeaData
from model.LimitModel import LimitModel
from model.SeaDataModel import SeaDataModel

logger = logging.getLogger("logger")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

        self.model = SeaDataModel()

        self.model2 = LimitModel()

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))
        # Example: Inserting a random row into the database when the button is clicked

        newSeaData = SeaData(
            year=2024,
            month=random.randint(1, 12),
            day=random.randint(1, 28),
            hour=random.randint(0, 23),
            waveHeight=random.randint(1, 10),
            waveDir=random.randint(0, 360),
            wavePeriod=2
        )
        success = self.model.insertRowData(newSeaData)

        if success:
            logger.info("New row inserted successfully")
        else:
            logger.error("Failed to insert new row")

        selected_data = self.model.selectRow(0)
        logger.info(f"Selected first row data: {selected_data}")

        limit = self.model2.selectLimit(1)
        logger.info(f"Selected Limit: {limit}")
        print(limit)
