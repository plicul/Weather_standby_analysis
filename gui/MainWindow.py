from PySide6 import QtWidgets
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QStackedWidget
import logging

logger = logging.getLogger("logger")

class MainWindow(QMainWindow):
    def __init__(self, widgets):
        super().__init__()
        self.setWindowTitle("Weather Standby Analysis")

        # Initialize QStackedWidget
        self.stacked_widget = QStackedWidget()

        self.widget_dict = {}

        for widget in widgets:
            widget_name = widget.name
            self.stacked_widget.addWidget(widget)
            self.widget_dict[widget_name] = widget

        # Set the default central widget to QStackedWidget
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.widget_dict.get("HomeWidget"))

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("Menu")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # Add actions to switch between widgets
        for widget_name in self.widget_dict.keys():
            action = QAction(widget_name, self)
            action.triggered.connect(lambda checked, wn=widget_name: self.switch_widget(wn))
            self.file_menu.addAction(action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setFixedSize(geometry.width() * 0.7, geometry.height() * 0.7)

    @Slot()
    def switch_widget(self, widget_name):
        new_widget = self.widget_dict.get(widget_name)
        if new_widget:
            if new_widget.update is not None:
                new_widget.update()
            self.stacked_widget.setCurrentWidget(new_widget)
