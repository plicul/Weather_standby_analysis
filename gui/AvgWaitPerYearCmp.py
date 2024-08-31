from PySide6 import QtCore
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QBarSeries, QBarSet, \
    QBarCategoryAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QHBoxLayout, QSizePolicy,
                               QWidget, QComboBox, QVBoxLayout,
                               QLabel)

from consts.types import CampaignResult
from model.CampaignModel import CampaignModel
from model.CampaignResultModel import CampaignResultModel


class AvgWaitPerYearCmp(QWidget):
    def __init__(self):
        super().__init__()

        self.model = CampaignResultModel()
        self.campaignModel = CampaignModel()
        self.name = "Average Wait Per Year Chart"
        self.campaigns: list[int] = self.campaignModel.getAllCampaignIds()

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        #self.addSeries(self.campaigns[0])

        self.dropdown = QComboBox(self)
        self.dropdown.addItems([str(cmp) for cmp in self.campaigns])
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

    @QtCore.Slot()
    def onCampaignChanged(self, a):
        b = a
        self.clearChart()
        selectedCampaignId = int(self.dropdown.currentText())
        self.addSeries(selectedCampaignId)

    def update(self):
        newCampaigns= self.campaignModel.getAllCampaignIds()
        if len(newCampaigns) != len(self.campaigns):
            self.campaigns: list[CampaignResult] = newCampaigns
            self.dropdown.clear()
            self.dropdown.addItems([str(cmp.id) for cmp in self.campaigns])

    def addSeries(self, selectedCampaignId):
        data = self.model.calcAvgWaitTimePerYear(selectedCampaignId)

        set = QBarSet("Average Wait Time")

        series = QBarSeries()

        bars = {}
        for dataVal in data:
            bars[dataVal[0]] = set # QBarSet(dataVal[0])
            bars[dataVal[0]].append(dataVal[1]*3)
        #bars["prevOp"] = QBarSet("")
        #bars["finish"].setColor('#1E3A5F')  #Dark Blue

        years = []
        for year, bar_set in bars.items():
            #bar_set.hovered.connect(self.handle_hovered)
            series.append(bar_set)
            years.append(year)

        self.chart.addSeries(series)

        axisX = QBarCategoryAxis()
        axisX.append(years)
        axisX.setTitleText("Year")
        self.chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setTitleText("Average Wait Time (h)")
        axisY.setTickInterval(1)
        axisY.setTickCount(10)
        self.chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        self.chart.setTitle("Average Wait Time Per Year")
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
