from collections import defaultdict
from operator import itemgetter

from PySide6 import QtCore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QBarSeries, QBarSet, \
    QCategoryAxis, QHorizontalStackedBarSeries, QBarCategoryAxis, QPieSeries, QPieSlice
from PySide6.QtCore import QDateTime, Qt, QDate, QTime, QRectF
from PySide6.QtGui import QPainter, QBrush, QColor, QCursor, QPen
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QGraphicsRectItem, QGraphicsScene, QToolTip, QComboBox, QVBoxLayout,
                               QLabel)

from consts.types import CampaignResultValue, SeaDataDate, CampaignResult, Campaign
from model.CampaignModel import CampaignModel
from model.CampaignResultModel import CampaignResultModel
from model.SeaDataModel import SeaDataModel
from utils import calcSeaDataDif


class CampaignOperationPieChart(QWidget):
    def __init__(self):
        super().__init__()

        self.campaignResultModel = CampaignResultModel()
        self.campaignModel = CampaignModel()
        self.name = "Campaign Operation Pie Chart"
        self.campaigns: list[int] = self.campaignModel.getAllCampaignIds()

        self.dropdown = QComboBox(self)
        self.dropdown.addItems([str(cmpId) for cmpId in self.campaigns])
        self.dropdown.setCurrentIndex(0)
        self.dropdown.activated.connect(self.onCampaignChanged)

        self.totalWait, self.totalWork = 0, 0

        self.chart = QChart()
        self.chart.setTitle('Campaign Operation Wait/Work Pie Chart')

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.addSeries(int(self.campaigns[0]))

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
        newCampaigns: list[int | None] = self.campaignModel.getAllCampaignIds()
        if len(newCampaigns) != len(self.campaigns):
            self.campaigns: list[int | None] = newCampaigns
            self.dropdown.clear()
            self.dropdown.addItems([str(cmp.id) for cmp in self.campaigns])

    @QtCore.Slot()
    def onCampaignChanged(self, a):
        self.clearChart()
        selectedCampaignId = int(self.dropdown.currentText())
        self.addSeries(selectedCampaignId)

    def addSeries(self, campaignId: int):
        self.totalWait, self.totalWork = self.campaignResultModel.getTotalWaitTotalWork(
            campaignId)  #dropdown sa campaign
        if self.totalWait is None or self.totalWork is None:
            return

        series = QPieSeries()

        series.append('Wait : ', self.totalWait)
        series.append('Work : ', self.totalWork)

        series.setLabelsVisible()
        series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)

        #slice = series.slices()[1]
        #slice.setExploded()
        #slice.setLabelVisible()
        #slice.setPen(QPen(Qt.darkGreen, 2))
        #slice.setBrush(Qt.green)

        for slice in series.slices():
            slice.setLabel((slice.label() + "{:.1f}%".format(100 * slice.percentage())))

        self.chart.addSeries(series)
