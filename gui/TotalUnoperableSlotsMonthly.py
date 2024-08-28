from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDateTime, Qt, QDate, QTime
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget)

from model.SimpleOperationResultModel import SimpleOperationResultModel


class TotalUnoperableDaysMonthly(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.series = None
        self.model = SimpleOperationResultModel()

        self.name = "Total Unoperable Slots Per Month"

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.add_series("Total Days")

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        self.chart_view.setInteractive(True)

        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        self.setLayout(self.main_layout)

    def add_series(self, name):
        # Create QLineSeries
        self.series = QLineSeries()
        self.series.setName(name)

        allResults: list[list[QDateTime | float]] = self.model.getTotalUnoperableSlotsPerMonth()
        for result in allResults:
            x = result[0]
            y = result[1]
            self.series.append(x.toMSecsSinceEpoch(), y)

        self.chart.addSeries(self.series)

        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(10)
        self.axis_x.setFormat("MMM yyyy")
        self.axis_x.setTitleText("Date")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setMin(0)
        self.axis_y.setTitleText("Unoperable Days per Month")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        color_name = self.series.pen().color().name()
        self.model.color = f"{color_name}"

    def update(self):
        pass
