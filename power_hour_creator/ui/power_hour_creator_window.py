import os

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QFileDialog, QDialog, \
    QMessageBox

from power_hour_creator import config
from power_hour_creator.media import CreatePowerHourService, PowerHour
from .forms.mainwindow import Ui_mainWindow
from .forms.power_hour_export_dialog import Ui_PowerHourExportDialog


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
        self._connect_file_menu()

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
        is_video = self.videoCheckBox.checkState()
        power_hour_path = self.get_power_hour_path(is_video=is_video)
        if power_hour_path:
            power_hour = PowerHour(self.tracklist.tracks, power_hour_path, is_video)
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

    def get_power_hour_path(self, is_video):
        if is_video:
            return QFileDialog.getSaveFileName(self, "Export Power Hour",
                                               os.path.expanduser('~/Videos'),
                                               "Video (*.mp4)")[0]
        else:
            return QFileDialog.getSaveFileName(self, "Export Power Hour",
                                               os.path.expanduser('~/Music'),
                                               "Audio (*.m4a)")[0]

    def _show_finished_status(self):
        self.statusBar.showMessage("Power hour created!", 5000)

    def _connect_help_menu(self):
        def show_logs():
            os.startfile(config.APP_DIRS.user_log_dir, 'explore')
        self.actionShow_logs.triggered.connect(show_logs)

    def _connect_file_menu(self):
        def new_power_hour():
            self.powerHoursListView.add_power_hour()

        self.actionNew_Power_Hour.triggered.connect(new_power_hour)


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
        service = CreatePowerHourService(
            power_hour=self._power_hour,
            progress_listener=self)

        service.execute()

        self.finished.emit()

    def on_new_track_downloading(self, download_number, track):
        self.progress.emit(download_number)
        self.new_track_downloading.emit(track)

    def on_download_progress(self, info):
        total_bytes = 1
        if 'total_bytes_estimate' in info:
            total_bytes = info['total_bytes_estimate']
        elif 'total_bytes' in info:
            total_bytes = info['total_bytes']
        self.track_download_progress.emit(info['downloaded_bytes'], total_bytes)

    def on_service_error(self, message):
        self.error.emit(message)

