import os

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog

from power_hour_creator import config
from power_hour_creator.media import CreatePowerHourService
from power_hour_creator.ui.forms.power_hour_export_dialog import \
    Ui_PowerHourExportDialog


class PowerHourCreationThread(QThread):

    progress = pyqtSignal(int)
    new_track_downloading = pyqtSignal(object)
    power_hour_created = pyqtSignal()
    finished = pyqtSignal()
    track_download_progress = pyqtSignal(object, object)
    all_media_downloaded = pyqtSignal()
    error = pyqtSignal(object)

    def __init__(self, parent, power_hour):
        super().__init__(parent)
        self._power_hour = power_hour
        self.service = None
        self._is_cancelled = False

    def run(self):
        self.service = CreatePowerHourService(
            power_hour=self._power_hour,
            progress_listener=self
        )

        self.service.execute()

        if not (self._is_cancelled or self.service.did_error):
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

    def on_all_media_downloaded(self):
        self.all_media_downloaded.emit()

    def on_service_error(self, message):
        self.error.emit(message)

    def cancel_export(self):
        self._is_cancelled = True
        self.service.cancel()


class CreatePowerHourDialog(QDialog, Ui_PowerHourExportDialog):

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

    def _setup_progress_bar(self):
        self.overallProgressBar.setMaximum(len(self._power_hour.tracks))

    def show_new_downloading_track(self, track):
        self.currentSongLabel.setText("Downloading: {}".format(track.title))
        self.currentSongProgressBar.reset()

    def show_track_download_progress(self, downloaded_bytes, total_bytes):
        if self.currentSongProgressBar.maximum() != total_bytes:
            self.currentSongProgressBar.setMaximum(total_bytes)

        self.currentSongProgressBar.setValue(downloaded_bytes)

    def show_final_processing_spinner(self):
        self.currentSongLabel.hide()
        self.currentSongProgressBar.hide()
        self.overallProgressLabel.setText('Merging tracks into power hour. This may take awhile...')
        self._turn_bar_into_spinner(self.overallProgressBar)

    def _turn_bar_into_spinner(self, progress_bar):
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)


def create_power_hour_in_background(power_hour,
                                    parent_widget,
                                    export_progress_view):
    thread = PowerHourCreationThread(parent_widget, power_hour)
    progress_dialog = CreatePowerHourDialog(parent_widget, power_hour)
    progress_dialog.cancelButton.clicked.connect(thread.cancel_export)

    thread.progress.connect(progress_dialog.overallProgressBar.setValue)
    thread.new_track_downloading.connect(progress_dialog.show_new_downloading_track)
    thread.track_download_progress.connect(progress_dialog.show_track_download_progress)
    thread.all_media_downloaded.connect(progress_dialog.show_final_processing_spinner)
    thread.error.connect(export_progress_view._show_worker_error)
    thread.finished.connect(progress_dialog.close)
    thread.power_hour_created.connect(export_progress_view._show_power_hour_created)
    thread.finished.connect(thread.deleteLater)

    progress_dialog.show()
    thread.start()


def get_power_hour_export_path(parent, is_video):
    return PowerHourOutputLocator(export_is_video=is_video, parent=parent).get_save_file_name()


class PowerHourOutputLocator:
    default_vid_dir = {
        'darwin': '~/Movies',
        'windows': '~/Videos',
        'linux': '~/Videos'
    }

    def __init__(self, export_is_video, parent, settings=config.get_persistent_settings()):
        self._export_is_video = export_is_video
        self._parent = parent
        self._settings = settings

    def get_save_file_name(self):
        path, _ = QFileDialog.getSaveFileName(
            self._parent,
            'Export Power Hour',
            os.path.expanduser(self._directory),
            self._file_description,
        )

        self._store_directory_if_present(path)

        return path

    @property
    def _directory(self):
        return self._settings.value(self._last_dir_settings_key, self._default_dir)

    @property
    def _last_dir_settings_key(self):
        prefix = 'exporting'
        if self._export_is_video:
            return f'{prefix}/last_video_dir'
        else:
            return f'{prefix}/last_audio_dir'

    @property
    def _default_dir(self):
        if self._export_is_video:
            return self.default_vid_dir[config.OS]
        else:
            return '~/Music'

    @property
    def _file_description(self):
        if self._export_is_video:
            return f'Video (*.{config.VIDEO_FORMAT})'
        else:
            return f'Audio (*.{config.AUDIO_FORMAT})'

    def _store_directory_if_present(self, path):
        if path:
            self._settings.setValue(
                self._last_dir_settings_key,
                os.path.dirname(path)
            )
