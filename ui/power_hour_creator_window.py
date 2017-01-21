from .forms.mainwindow import Ui_mainWindow
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QLineEdit,\
    QTableWidgetItem, QFileDialog
import os
from youtube_dl import YoutubeDL


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
                                                os.path.expanduser('~/Music'))
        if file_name:
            DownloadVideosService(self.tracklist.urls).execute()


class DownloadVideosService:
    def __init__(self, urls):
        self.urls = urls

    def execute(self):
        for track in self.tracklist.tracks:
            opts = {
                'postprocess_args': 'trim={}:{}'.format(track.start_time,
                                                        track.start_time + 60),
                'extract_audio': 'mp3'
            }
            with YoutubeDL(opts) as ydl:
                ydl.download(track.url)
