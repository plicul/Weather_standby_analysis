import random
import logging

from PySide6 import QtWidgets, QtCore
import xarray as xr

from consts.types import SeaData, Operation
from functions.CampaignResultGeneration import simulateCampaign
from functions.utils import importLimitFromExcel
from model.CampaignModel import CampaignModel
from model.CampaignResultModel import CampaignResultModel
from model.LimitModel import LimitModel
from model.OperationModel import OperationModel
from model.OperationResultModel import OperationResultModel
from model.SeaDataModel import SeaDataModel
from model.SimpleOperationResultModel import SimpleOperationResultModel

logger = logging.getLogger("logger")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Campaign Result Generation")
        self.button2 = QtWidgets.QPushButton("Operation Result Generation")
        self.button3 = QtWidgets.QPushButton("Simple Operation Result Generation")
        self.text = QtWidgets.QLabel("",
                                     alignment=QtCore.Qt.AlignCenter)

        self.name = "Simulation Functions"

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.button3)

        self.button.clicked.connect(self.simulateCampaigns)
        self.button2.clicked.connect(self.generateOperationResults)
        self.button3.clicked.connect(self.generateSimpleOperationResults)

        self.seaDataModel = SeaDataModel()
        self.operationModel = OperationModel()
        self.limitModel = LimitModel()
        self.operationResultModel = OperationResultModel()
        self.simpleOperationResultModel = SimpleOperationResultModel()
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

        campaignsList = self.campaignModel.getAllCampaignIds()
        for campaignId in campaignsList:
            campaign = self.campaignModel.getCampaign(campaignId)
            if not campaign:
                self.text.setText("Campaign not found.")
                continue

            # Define the list of SeaDataDate objects (this could be based on your actual requirements)
            dates = self.seaDataModel.getSeaDataDateRange()

            # Simulate the campaign
            success = simulateCampaign(campaign, dates, self.campaignResultModel, self.operationResultModel, self.operationModel)

            if success:
                self.text.setText("Campaign simulation completed successfully!")
            else:
                self.text.setText("Campaign simulation failed.")

    @QtCore.Slot()
    def generateOperationResults(self):
        #importLimitFromExcel(self.limitModel)
        #DS = xr.open_dataset("ncfile.nc")
        #DS.to_dataframe().to_csv("sea_databruh.csv")
        #pass
        #return
        operationList: list[Operation] = self.operationModel.getAllOperations(self.limitModel)
        for operation in operationList:
            try:
                self.operationResultModel.generateOperationResults(self.seaDataModel.getAllRows(), operation)
            except Exception as e:
                logger.error(f"Error Generating Operation Results: {e}")
                print(e)

    @QtCore.Slot()
    def generateSimpleOperationResults(self):
        operationList: list[Operation] = self.operationModel.getAllOperations(self.limitModel)
        for operation in operationList:
            try:
                self.simpleOperationResultModel.generateOperationResults(self.seaDataModel.getAllRows(), operation)
            except Exception as e:
                logger.error(f"Error Generating Operation Results: {e}")
                print(e)

    def update(self):
        pass