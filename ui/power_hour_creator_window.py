import os

from PyQt5.QtWidgets import QMainWindow, QHeaderView, QFileDialog

from phc.media_handling import DownloadMediaService
from .forms.mainwindow import Ui_mainWindow


class PowerHourCreatorWindow(QMainWindow, Ui_mainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._setup_grid_appearance()
        self._connect_add_track_button()
        self._connect_create_power_hour_button()

    def _setup_grid_appearance(self):
        self.tracklist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _connect_add_track_button(self):
        self.addTrackButton.clicked.connect(self.tracklist.add_track)

    def _connect_create_power_hour_button(self):
        self.createPowerHourButton.clicked.connect(self._export_power_hour)

    def _export_power_hour(self):
        file_name = QFileDialog.getSaveFileName(self, "Export Power Hour",
                                                os.path.expanduser('~/Music'),
                                                "Audio (*.mp3)")[0]
        if not file_name.lower().endswith('.mp3'):
            file_name += '.mp3'

        if file_name:
            DownloadMediaService(self.tracklist.tracks, file_name).execute()
