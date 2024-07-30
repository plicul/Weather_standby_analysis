import random
import logging

from PySide6 import QtWidgets, QtCore

from consts.types import SeaData, Operation
from functions.CampaignResultGeneration import simulateCampaign
from model.CampaignModel import CampaignModel
from model.CampaignResultModel import CampaignResultModel
from model.LimitModel import LimitModel
from model.OperationModel import OperationModel
from model.OperationResultModel import OperationResultModel
from model.SeaDataModel import SeaDataModel

logger = logging.getLogger("logger")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Campaigns!")
        self.button2 = QtWidgets.QPushButton("Operations!")
        self.text = QtWidgets.QLabel("",
                                     alignment=QtCore.Qt.AlignCenter)

        self.name = "Simulation Functions"

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button2)

        self.button.clicked.connect(self.simulateCampaigns)
        self.button2.clicked.connect(self.generateOperationResults)

        self.seaDataModel = SeaDataModel()
        self.operationModel = OperationModel()
        self.limitModel = LimitModel()
        self.operationResultModel = OperationResultModel()
        self.campaignModel = CampaignModel()
        self.campaignResultModel = CampaignResultModel()

    @QtCore.Slot()
    def simulateCampaigns(self):
        #importLimitFromExcel(self.model2)

        #operationList: list[Operation] = self.operationModel.getAllOperations(self.limitModel)
        #for operation in operationList:
        #    try:
        #        self.operationResultModel.generateOperationResults(self.model.getAllRows(), operation)
        #    except Exception as e:
        #        logger.error(f"Error Generating Operation Results: {e}")
        #        print(e)

        # Todo select which campaign to simulate
        campaign_id = 1
        campaign = self.campaignModel.getCampaign(campaign_id)

        if not campaign:
            self.text.setText("Campaign not found.")
            return

        # Define the list of SeaDataDate objects (this could be based on your actual requirements)
        dates = self.seaDataModel.getSeaDataDateRange()

        # Simulate the campaign
        success = simulateCampaign(campaign, dates, self.campaignResultModel, self.operationResultModel)

        if success:
            self.text.setText("Campaign simulation completed successfully!")
        else:
            self.text.setText("Campaign simulation failed.")

    @QtCore.Slot()
    def generateOperationResults(self):
        #importLimitFromExcel(self.model2)

        operationList: list[Operation] = self.operationModel.getAllOperations(self.limitModel)
        for operation in operationList:
            try:
                self.operationResultModel.generateOperationResults(self.seaDataModel.getAllRows(), operation)
            except Exception as e:
                logger.error(f"Error Generating Operation Results: {e}")
                print(e)

    def update(self):
        pass