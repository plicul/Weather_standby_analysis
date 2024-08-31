from PySide6 import QtCore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QPolarChart
from PySide6.QtCore import QDateTime, Qt, QDate, QTime
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QComboBox, QLabel)

from consts.types import Limit
from model.LimitModel import LimitModel
from model.SimpleOperationResultModel import SimpleOperationResultModel


class LimitPolarChart(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.series = None
        self.model = LimitModel()
        self.limits = self.model.getAllLimits()

        self.name = "Limit Polar Chart"

        self.dropdown = QComboBox(self)
        self.dropdown.addItems([lim.name for lim in self.limits])
        #self.dropdown.currentIndexChanged.connect(self.onCampaignChanged())
        #self.dropdown.currentTextChanged.connect(self.onCampaignChanged())
        self.dropdown.setCurrentIndex(0)
        self.dropdown.activated.connect(self.onCampaignChanged)

        self.chart = QPolarChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)

        self.angularAxis = QValueAxis(self.chart)
        self.angularAxis.setRange(0, 360)
        self.angularAxis.setTickCount(9)
        self.angularAxis.setLabelFormat("%.1f")
        self.angularAxis.setShadesVisible(True)
        self.angularAxis.setShadesBrush(QBrush(QColor(249, 249, 255)))
        self.angularAxis.setLabelFormat("%.1f")
        self.chart.addAxis(self.angularAxis, QPolarChart.PolarOrientationAngular)

        self.radialAxis = QValueAxis()
        self.radialAxis.setTickCount(9)
        self.radialAxis.setLabelFormat("%d")
        self.radialAxis.setRange(0,20)
        self.chart.addAxis(self.radialAxis, QPolarChart.PolarOrientationRadial)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        self.chart_view.setInteractive(True)

        self.main_layout = QHBoxLayout()
        self.control_layout = QHBoxLayout()
        self.control_layout.addWidget(QLabel("Select Limit:"))
        self.control_layout.addWidget(self.dropdown)

        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(4)

        self.chart_view.setSizePolicy(size)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.addWidget(self.chart_view)
        self.setLayout(self.main_layout)
    def update(self):
        newLimits: list[Limit] = self.model.getAllLimits()
        if len(newLimits) != len(self.limits):
            self.limits: list[Limit] = newLimits
            self.dropdown.clear()
            self.dropdown.addItems([lim.name for lim in self.limits])

    @QtCore.Slot()
    def onCampaignChanged(self, a):
        self.clearChart()
        limitId = self.limits[a].id
        self.add_series(limitId)
    def add_series(self, limitId):
        allResults: Limit = self.model.selectLimit(limitId)
        periodList = list(set(cmp.wavePeriod for cmp in allResults.values))
        self.radialAxis.setRange(0, max([res.waveHeight for res in allResults.values]) + 3)


        try:
            for per in periodList:
                self.series = QLineSeries()
                self.series.setName(f"Period: {per}")
                for result in [res for res in allResults.values if res.wavePeriod == per]:
                    x = result.waveDir  # Direction in degrees (0-360)
                    y = result.waveHeight  # Height in the same unit as radial axis
                    self.series.append(x, y)

                # Attach the series to the angular and radial axes
                self.chart.addSeries(self.series)
                self.series.attachAxis(self.angularAxis)
                self.series.attachAxis(self.radialAxis)
        except Exception as e:
            print(f"Error while adding series: {e}")

    def clearChart(self):
        self.chart.removeAllSeries()
        #axes = self.chart.axes()
        #for axis in axes:
         #   self.chart.removeAxis(axis)
