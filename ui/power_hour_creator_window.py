from .forms.mainwindow import Ui_mainWindow
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QLineEdit, QTableWidgetItem


class PowerHourCreatorWindow(QMainWindow, Ui_mainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setup_grid()
        self.setup_add_track_button()

    def setup_grid(self):
        self.tracklist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def setup_add_track_button(self):
        self.addTrackButton.clicked.connect(self.tracklist.add_track)
