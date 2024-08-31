from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDateTime, Qt, QDate, QTime
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QListWidget, QListWidgetItem)

from model.SimpleOperationResultModel import SimpleOperationResultModel


class TotalUnoperableDaysMonthly(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.series = None
        self.model = SimpleOperationResultModel()

        self.name = "Total Unoperable Slots Per Month"

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        self.chart_view.setInteractive(True)

             # Add the QListWidget to your UI, e.g., in the __init__ method
        self.operation_list = QListWidget(self)
        self.operation_list.setSelectionMode(QListWidget.MultiSelection)

        # Populate the QListWidget with operation IDs
        self.allResults = self.model.getTotalUnoperableSlotsPerMonth()
        for operation_id in self.allResults.keys():
            item = QListWidgetItem(f"Operation {operation_id}")
            item.setData(Qt.UserRole, operation_id)  # Store the operation ID
            item.setCheckState(Qt.Unchecked)  # Start with all unchecked
            self.operation_list.addItem(item)
        self.operation_list.itemChanged.connect(self.update_chart)

        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)
        self.main_layout.addWidget(self.operation_list)
        self.axisSet = False

        self.setLayout(self.main_layout)
    def clearChart(self):
        self.chart.removeAllSeries()
        self.chart.removeAxis(self.chart.axisY())
        self.chart.removeAxis(self.chart.axisX())

    def update_chart(self):
        self.clearChart()
        self.add_series("Unoperable Days")
    def get_selected_operations(self):
        selected_operations = []
        for index in range(self.operation_list.count()):
            item = self.operation_list.item(index)
            if item.checkState() == Qt.Checked:
                selected_operations.append(item.data(Qt.UserRole))
        return selected_operations
    def add_series(self, name):
        self.clearChart()

        sel = self.get_selected_operations()
        filtered_results = dict(filter(lambda item: item[0] in sel, self.allResults.items()))

        if not filtered_results:
            return
        seriesList = []
        for operation_id, values in filtered_results.items():
            series = QLineSeries()
            series.setName(f"{operation_id}")

            for entry in values:
                date = entry[0]
                unoperable_days = entry[1] / 24
                series.append(date.toMSecsSinceEpoch(), unoperable_days)
            seriesList.append(series)
            self.chart.addSeries(series)

        # Create and configure the X-axis (time)
        axis_x = QDateTimeAxis()
        axis_x.setTickCount(10)
        axis_x.setFormat("MMM yyyy")
        axis_x.setTitleText("Date")
        self.chart.addAxis(axis_x, Qt.AlignBottom)

        # Create and configure the Y-axis (unoperable days)
        axis_y = QValueAxis()
        axis_y.setTickCount(10)
        axis_y.setLabelFormat("%.2f")
        axis_y.setMin(0)
        axis_y.setMax(32)
        axis_y.setTitleText("Unoperable Days per Month")
        self.chart.addAxis(axis_y, Qt.AlignLeft)

        for series in seriesList:
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

    def update(self):
        pass
