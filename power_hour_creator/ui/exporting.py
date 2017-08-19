from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QDialog

from power_hour_creator.media import PowerHourExportService
from power_hour_creator.ui.forms.power_hour_export_dialog import \
    Ui_PowerHourExportDialog


class PowerHourExportThread(QThread):

    progress = pyqtSignal(int)
    new_track_downloading = pyqtSignal(object)
    power_hour_created = pyqtSignal()
    finished = pyqtSignal()
    track_download_progress = pyqtSignal(object, object)
    error = pyqtSignal(object)

    def __init__(self, parent, power_hour):
        super().__init__(parent)
        self._power_hour = power_hour
        self.service = None
        self._is_cancelled = False

    def run(self):
        self.service = PowerHourExportService(
            power_hour=self._power_hour,
            progress_listener=self
        )

        self.service.execute()

        if not self._is_cancelled:
            self.power_hour_created.emit()

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

    def cancel_export(self):
        self._is_cancelled = True
        self.service.cancel_export()


class ExportPowerHourDialog(QDialog, Ui_PowerHourExportDialog):

    DOT_BLINK_TIME_IN_MS = 250

    def __init__(self, parent, power_hour):
        QDialog.__init__(self, parent, Qt.WindowTitleHint)
        Ui_PowerHourExportDialog.__init__(self)
        self._power_hour = power_hour

        self.setupUi(self)
        self._setup_signals()
        self._setup_progress_bar()

    def setupUi(self, ui):
        super().setupUi(ui)
        self.cancellingLabel.hide()
        self.setWindowTitle('Exporting: {}'.format(self._power_hour.name))

    def _setup_progress_bar(self):
        self.overallProgressBar.setMaximum(len(self._power_hour.tracks))

    def _setup_signals(self):
        self.cancelButton.clicked.connect(self._cancelling_export)

    def _cancelling_export(self):
        self._hide_progress_widgets()
        self._show_cancelling_widgets()

    def _hide_progress_widgets(self):
        self.currentSongLabel.hide()
        self.currentSongProgressBar.hide()
        self.overallProgressBar.hide()
        self.overallProgressLabel.hide()

    def _show_cancelling_widgets(self):
        self.cancellingLabel.show()
        timer = QTimer(self)
        timer.timeout.connect(self._update_cancelling_progress)
        timer.start(self.DOT_BLINK_TIME_IN_MS)

    def _update_cancelling_progress(self):
        text = self.cancellingLabel.text()
        num_dots = 0
        for c in text:
            if c == '.':
                num_dots += 1

        dots = ('.' * ((num_dots + 1) % 4))
        self.cancellingLabel.setText(text.replace('.', '') + dots)

    def show_new_downloading_track(self, track):
        self.currentSongLabel.setText("Downloading: {}".format(track.title))
        self.currentSongProgressBar.reset()

    def show_track_download_progress(self, downloaded_bytes, total_bytes):
        if self.currentSongProgressBar.maximum() != total_bytes:
            self.currentSongProgressBar.setMaximum(total_bytes)

        self.currentSongProgressBar.setValue(downloaded_bytes)