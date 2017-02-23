from collections import namedtuple

import os

from pprint import pprint

from PyQt5.QtWidgets import QMainWindow, QHeaderView, QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

from power_hour_creator import config
from power_hour_creator.media_handling import DownloadMediaService
from .forms.mainwindow import Ui_mainWindow
from .forms.power_hour_export_dialog import Ui_PowerHourExportDialog


PowerHour = namedtuple('PowerHour', 'tracks file_name')


class PowerHourCreatorWindow(QMainWindow, Ui_mainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._setup_grid_appearance()
        self._connect_add_track_button()
        self._connect_create_power_hour_button()
        self._connect_track_errors()
        self._enable_create_power_hour_button_when_tracks_present()
        self._connect_help_menu()

    def _setup_grid_appearance(self):
        self.tracklist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _connect_add_track_button(self):
        self.addTrackButton.clicked.connect(self.tracklist.add_track)

    def _connect_create_power_hour_button(self):
        self.createPowerHourButton.clicked.connect(self._export_power_hour)

    def _connect_track_errors(self):
        self.tracklist.invalid_url.connect(self._show_invalid_url)
        self.tracklist.error_downloading.connect(self._show_error_downloading)

    def _enable_create_power_hour_button_when_tracks_present(self):
        self.tracklist.itemChanged.connect(self._try_to_enable_create_button_on_tracklist_change)

    def _try_to_enable_create_button_on_tracklist_change(self):
        tracks_present = len(self.tracklist.tracks) > 0
        self.createPowerHourButton.setEnabled(tracks_present)

    def _show_invalid_url(self, url):
        self.statusBar.showMessage('URL "{}" is invalid'.format(url))

    def _show_error_downloading(self, url):
        self.statusBar.showMessage('Error downloading "{}"'.format(url))

    def _show_worker_error(self, message):
        msg = QMessageBox(self)
        msg.setText('Error occured')
        msg.setDetailedText(message)
        msg.show()

    def _export_power_hour(self):
        file_name = self.get_export_path()
        if file_name:
            file_name = self._ensure_file_has_correct_ext(file_name)

            power_hour = PowerHour(self.tracklist.tracks, file_name)
            thread = PowerHourExportThread(self, power_hour)
            progress_dialog = ExportPowerHourDialog(self, power_hour)

            thread.progress.connect(progress_dialog.overallProgressBar.setValue)
            thread.new_track_downloading.connect(progress_dialog.show_new_downloading_track)
            thread.track_download_progress.connect(progress_dialog.show_track_download_progress)
            thread.finished.connect(progress_dialog.close)
            thread.finished.connect(self._show_finished_status)
            thread.error.connect(self._show_worker_error)

            progress_dialog.show()
            thread.start()


    def _ensure_file_has_correct_ext(self, file_name):
        if not file_name.lower().endswith('.aac'):
            file_name += '.aac'
        return file_name

    def get_export_path(self):
        return QFileDialog.getSaveFileName(self, "Export Power Hour",
                                           os.path.expanduser('~/Music'),
                                           "Audio (*.aac)")[0]

    def _show_finished_status(self):
        self.statusBar.showMessage("Power hour created!", 5000)

    def _connect_help_menu(self):
        def show_logs():
            os.startfile(config.APP_DIRS.user_log_dir, 'explore')
        self.actionShow_logs.triggered.connect(show_logs)


class ExportPowerHourDialog(QDialog, Ui_PowerHourExportDialog):
    def __init__(self, parent, power_hour):
        QDialog.__init__(self, parent)
        Ui_PowerHourExportDialog.__init__(self)
        self.setupUi(self)

        self._power_hour = power_hour

        self._setup_signals()
        self._setup_progress_bar()

    def _setup_progress_bar(self):
        self.overallProgressBar.setMaximum(len(self._power_hour.tracks))

    def _setup_signals(self):
        self.cancelButton.clicked.connect(self.close)

    def show_new_downloading_track(self, track):
        self.currentSongLabel.setText("Downloading: {}".format(track.title))
        self.currentSongProgressBar.reset()

    def show_track_download_progress(self, downloaded_bytes, total_bytes):
        if self.currentSongProgressBar.maximum() != total_bytes:
            self.currentSongProgressBar.setMaximum(total_bytes)

        self.currentSongProgressBar.setValue(downloaded_bytes)


class PowerHourExportThread(QThread):

    progress = pyqtSignal(int)
    new_track_downloading = pyqtSignal(object)
    finished = pyqtSignal()
    track_download_progress = pyqtSignal(object, object)
    error = pyqtSignal(object)

    def __init__(self, parent, power_hour):
        super().__init__(parent)
        self._power_hour = power_hour

    def run(self):
        service = DownloadMediaService(
            self._power_hour.tracks,
            self._power_hour.file_name,
            new_track_downloading_callback=self.handle_new_track_downloading,
            download_progress_callback=self.handle_download_progress,
            error_callback=self.handle_service_error)

        service.execute()

        self.finished.emit()

    def handle_new_track_downloading(self, download_number, track):
        self.progress.emit(download_number)
        self.new_track_downloading.emit(track)

    def handle_download_progress(self, info):
        total_bytes = 1
        if 'total_bytes_estimate' in info:
            total_bytes = info['total_bytes_estimate']
        elif 'total_bytes' in info:
            total_bytes = info['total_bytes']
        self.track_download_progress.emit(info['downloaded_bytes'], total_bytes)

    def handle_service_error(self, message):
        self.error.emit(message)

