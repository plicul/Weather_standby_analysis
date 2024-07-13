import sys
import logging

from PySide6 import QtWidgets

from gui.CampaignFlowChartWidget import CampaignFlowChartWidget
from gui.HomeWidget import HomeWidget
from gui.SeaDataTableView import SeaDataTableViewWidget
from gui.MainWindow import MainWindow
from gui.MyWidget import MyWidget
from db import connectToDatabase

logging.basicConfig(filename="app.log", level=logging.DEBUG)
logger = logging.getLogger("logger")

if __name__ == "__main__":
    #seaDataToExcel()
    app = QtWidgets.QApplication([])
    if not connectToDatabase():
        sys.exit(1)


    #widget.resize(800, 600)
    #widget.show()
    widget = MyWidget()
    seaDataWidget = SeaDataTableViewWidget()
    homeWidget = HomeWidget()
    campaignFlowChartWidget = CampaignFlowChartWidget()
    widgets = [seaDataWidget, homeWidget, widget, campaignFlowChartWidget]

    window = MainWindow(widgets)
    window.show()

    sys.exit(app.exec())
