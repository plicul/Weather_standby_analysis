import random
import logging

from PySide6 import QtWidgets, QtCore

from consts.types import SeaData, Operation
from model.LimitModel import LimitModel
from model.OperationModel import OperationModel
from model.OperationResultModel import OperationResultModel
from model.SeaDataModel import SeaDataModel

logger = logging.getLogger("logger")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()


        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

        self.model = SeaDataModel()

        self.operationModel = OperationModel()
        self.limitModel = LimitModel()
        self.operationResultModel = OperationResultModel()

    @QtCore.Slot()
    def magic(self):
        #importLimitFromExcel(self.model2)

        operationList: list[Operation] = self.operationModel.getAllOperations(self.limitModel)
        for operation in operationList:
            try:
                self.operationResultModel.generateOperationResults(self.model.getAllRows(), operation)
            except Exception as e:
                logger.error(f"Error Generating Operation Results: {e}")
                print(e)
