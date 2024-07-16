from collections import defaultdict
from operator import itemgetter

from PySide6 import QtCore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QBarSeries, QBarSet, \
    QCategoryAxis, QHorizontalStackedBarSeries, QBarCategoryAxis
from PySide6.QtCore import QDateTime, Qt, QDate, QTime, QRectF
from PySide6.QtGui import QPainter, QBrush, QColor, QCursor
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QGraphicsRectItem, QGraphicsScene, QToolTip, QComboBox, QVBoxLayout,
                               QLabel)

from consts.types import CampaignResultValue, SeaDataDate, CampaignResult
from model.CampaignResultModel import CampaignResultModel
from model.SeaDataModel import SeaDataModel
from utils import calcSeaDataDif


class CampaignFlowChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.model = CampaignResultModel()
        self.name = "Campaign Flow Chart"
        self.campaigns: list[CampaignResult] = self.model.getAllCampaignResults()

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.addSeries(self.campaigns[0].id) if self.campaigns and len(self.campaigns) > 0 else None

        self.dropdown = QComboBox(self)
        self.dropdown.addItems([str(cmp.id) for cmp in self.campaigns])
        #self.dropdown.currentIndexChanged.connect(self.onCampaignChanged())
        #self.dropdown.currentTextChanged.connect(self.onCampaignChanged())
        self.dropdown.setCurrentIndex(0)
        self.dropdown.activated.connect(self.onCampaignChanged)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        self.chart_view.setInteractive(True)

        self.main_layout = QVBoxLayout()
        self.control_layout = QHBoxLayout()

        self.control_layout.addWidget(QLabel("Select Campaign:"))
        self.control_layout.addWidget(self.dropdown)

        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)

        self.main_layout.addLayout(self.control_layout)
        self.main_layout.addWidget(self.chart_view)
        self.setLayout(self.main_layout)

    def update(self):
        self.campaigns: list[CampaignResult] = self.model.getAllCampaignResults()

    @QtCore.Slot()
    def onCampaignChanged(self, a):
        b = a
        self.clearChart()
        selectedCampaignId = int(self.dropdown.currentText())
        self.addSeries(selectedCampaignId)

    def addSeries(self, selectedCampaignId):
        data = self.model.getCampaignResultValuesForCampaignResult(selectedCampaignId)  #78239

        operationList = []
        grouped_data = defaultdict(list)
        cmpStartDate: SeaDataDate = SeaDataDate(data[0].year, data[0].month, data[0].day, data[0].hour)
        currentOp = data[0].campaignOperationId
        for item in data:
            if item.campaignOperationId != currentOp:
                currentOp = item.campaignOperationId
                if not grouped_data[int(operationList[-1]), "wait"]:
                    grouped_data[int(operationList[-1]), "wait"].append(0)
                if not grouped_data[int(operationList[-1]), "prevOp"]:
                    grouped_data[int(operationList[-1]), "prevOp"].append(0)
                grouped_data[item.campaignOperationId, "prevOp"].append(
                    calcSeaDataDif(cmpStartDate, SeaDataDate(item.year, item.month, item.day, item.hour)))
            if not grouped_data[item.campaignOperationId, item.status]:
                grouped_data[item.campaignOperationId, item.status].append(1)
            else:
                grouped_data[item.campaignOperationId, item.status][0] += 1
            if str(item.campaignOperationId) not in operationList:
                operationList.append(str(item.campaignOperationId))

        series = QHorizontalStackedBarSeries()

        bars = {}
        bars["prevOp"] = QBarSet("")
        bars["wait"] = QBarSet("wait")
        bars["start"] = QBarSet("start")
        bars["work"] = QBarSet("work")
        bars["finish"] = QBarSet("finish")
        bars["prevOp"].setColor("transparent")
        bars["wait"].setColor('#D3D3D3')  #Light Gray
        bars["start"].setColor('#ADD8E6')  #Light Blue
        bars["work"].setColor('#4682B4')  #Blue
        bars["finish"].setColor('#1E3A5F')  #Dark Blue

        #cummulativeSum = 0
        #lastFinish = 0
        #newOpStartFlag = True
        for operation_id, values in grouped_data.items():
            #if newOpStartFlag:
            #    bars["prevOp"].append(lastFinish)
            #    newOpStartFlag = False
            #cummulativeSum += values[0]*3
            bars[operation_id[1]].append(values[0] * 3)
            #if operation_id[1] == "finish":
            #    lastFinish += cummulativeSum
            #    cummulativeSum = 0
            #    newOpStartFlag = True

        for status, bar_set in bars.items():
            #bar_set.hovered.connect(self.handle_hovered)
            series.append(bar_set)

        self.chart.addSeries(series)

        axisX = QValueAxis()
        axisX.setTitleText("Time (h)")
        axisX.setMin(0)
        axisX.setTickInterval(1)
        axisX.setTickCount(10)
        self.chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QBarCategoryAxis()
        axisY.append(operationList)
        axisY.setTitleText("Operation ID")
        self.chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        self.chart.setTitle("Campaign Result Gantt Chart")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

    #def handle_hovered(self, status, index):
    #    if status:
    #        QToolTip.showText(QCursor.pos(), f"Status: {status}, Index: {index}")
    #    else:
    #        QToolTip.hideText()
    def clearChart(self):
        self.chart.removeAllSeries()
        axes = self.chart.axes()
        for axis in axes:
            self.chart.removeAxis(axis)
