import sys
import logging

from PySide6 import QtWidgets

from gui.AvgWaitPerMonthCmp import AvgWaitPerMonthCmp
from gui.AvgWaitPerYearCmp import AvgWaitPerYearCmp
from gui.TotalWaitPerMonthCmp import TotalWaitPerMonthCmp
from gui.TotalWaitPerYearCmp import TotalWaitPerYearCmp
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
    totalWaitPerYearCmp = TotalWaitPerYearCmp()
    avgWaitPerYearCmp = AvgWaitPerYearCmp()
    totalWaitPerMonthCmp = TotalWaitPerMonthCmp()
    avgWaitPerMonthCmp = AvgWaitPerMonthCmp()
    widgets = [homeWidget, seaDataWidget, widget, campaignFlowChartWidget, campaignOperationPieChart,
               totalWaitPerYearCmp, avgWaitPerYearCmp, totalWaitPerMonthCmp,avgWaitPerMonthCmp]

    window = MainWindow(widgets)
    window.show()

    sys.exit(app.exec())
