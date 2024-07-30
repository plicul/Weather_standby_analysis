import sys
import logging

from PySide6 import QtWidgets

from gui.TotalWaitPerYearCmp import AvgWaitPerYearCmp
from gui.CampaignFlowChartWidget import CampaignFlowChartWidget
from gui.CampaignOperationPieChart import CampaignOperationPieChart
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
    campaignOperationPieChart = CampaignOperationPieChart()
    avgWaitPerYearCmp = AvgWaitPerYearCmp()
    widgets = [homeWidget, seaDataWidget, widget, campaignFlowChartWidget, campaignOperationPieChart,avgWaitPerYearCmp]

    window = MainWindow(widgets)
    window.show()

    sys.exit(app.exec())
