from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDateTime, Qt, QDate, QTime
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget)

from model.SeaDataModel import SeaDataModel


class SeaDataTableViewWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.series = None
        self.model = SeaDataModel()

        self.name = "Sea Data"

        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.add_series("Wave Height")

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        #self.chart_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #self.chart_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.chart_view.setInteractive(True)

        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        self.setLayout(self.main_layout)


    def add_series(self, name):
        # Create QLineSeries
        self.series = QLineSeries()
        self.series.setName(name)
        while self.model.canFetchMore():
            self.model.fetchMore()
        c = self.model.rowCount()
        timestamps = []
        for i in range(c):
            year = (self.model.index(i, 0).data())

            month = (self.model.index(i, 1).data())
            day = (self.model.index(i, 2).data())
            hour = (self.model.index(i, 3).data())

            #month = "0" + month if len(month) == 1 else month
            #day = "0" + day if len(day) == 1 else day
            #hour = "0" + hour if len(hour) == 1 else hour

            #t = year + "-" + month + "-" + day + " " + hour
            date_fmt = "yyyy-MM-dd HH"

            xValue = QDateTime()
            xValue.setDate(QDate(year, month, day))
            xValue.setTime(QTime(hour, 0))


            #date_fmt = "yyyy"

            if True:
                x = xValue
                #x = QDateTime().fromString(str(t), date_fmt).toSecsSinceEpoch()
                y = float(self.model.index(i, 4).data())

                if x is not None and y > 0:
                    self.series.append(x.toMSecsSinceEpoch(), y)
                    timestamps.append(x)

        self.chart.addSeries(self.series)

        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(10)
        self.axis_x.setFormat("yyyy-MM-dd HH")
        self.axis_x.setTitleText("Date")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        #if timestamps:
       #     min_time = min(timestamps)
       #     max_time = max(timestamps)
        #    self.axis_x.setRange(QDateTime.fromSecsSinceEpoch(min_time), QDateTime.fromSecsSinceEpoch(max_time))
        self.series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Wave Height")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        color_name = self.series.pen().color().name()
        self.model.color = f"{color_name}"