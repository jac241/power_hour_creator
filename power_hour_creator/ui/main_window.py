import os
import subprocess

from PyQt5.QtCore import QObject, pyqtSignal, QSize, QPoint, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QSpacerItem, QSizePolicy

from alchemy_test import TrackRepository, TracklistModel, Track
from power_hour_creator import config
from power_hour_creator.media import PowerHour
from power_hour_creator.resources import image_path
from power_hour_creator.ui.creation import create_power_hour_in_background, \
    get_power_hour_export_path
from power_hour_creator.ui.tracklist_export import export_tracklist_to_file
from power_hour_creator.ui.power_hour_list import PowerHourModel
from power_hour_creator.ui.tracklist import TrackDelegate
from power_hour_creator.ui.tracklist_import import import_tracklist_from_file
from power_hour_creator.ui.about_dialog import AboutDialog
from .forms.mainwindow import Ui_mainWindow

ERROR_DISPLAY_TIME_IN_MS = 5000
CREATED_DISPLAY_TIME_IN_MS = 10000


class MainWindow(QMainWindow, Ui_mainWindow):

    def __init__(self, power_hour_model, tracklist_model, tracklist_delegate,
                 track_error_dispatcher):
        super().__init__()
        self.power_hour_model = power_hour_model
        self.tracklist_model = tracklist_model
        self.tracklist_delegate = tracklist_delegate
        self.track_error_dispatcher = track_error_dispatcher
        self._settings = config.get_persistent_settings()
        self._export_thread = None

        self.setupUi(self)
        self._setup_power_hour_list_view()
        self._setup_tracklist()
        self._connect_create_power_hour_button()
        self._connect_track_errors()
        self._enable_create_power_hour_button_when_tracks_present()
        self._connect_help_menu()
        self._connect_file_menu()
        self._connect_power_hour_list_view()
        self.setWindowIcon(QIcon(image_path('Beer-80.png')))
        self._restore_view_settings()

    def _setup_power_hour_list_view(self):
        self.powerHoursListView.setModel(self.power_hour_model)
        self.powerHoursListView.setModelColumn(1)

        self.power_hour_model.rowsInserted.connect(self.powerHoursListView.select_new_power_hour)

    def _setup_tracklist(self):
        self._setup_tracklist_model()
        self._setup_tracklist_delegate()

    def _setup_tracklist_model(self):
        self.tracklist.setModel(self.tracklist_model)
        self.tracklist.hideColumn(0)  # id
        self.tracklist.hideColumn(1)  # position
        self.tracklist.hideColumn(7)  # power_hour_id

        column_indices = Track.column_indices
        # self.tracklist.setHeaderData(column_indices['url'], Qt.Horizontal, "URL")
        # self.tracklist.setHeaderData(column_indices['title'], Qt.Horizontal, "Title")
        # self.tracklist.setHeaderData(column_indices['length'], Qt.Horizontal, "Duration")
        # self.tracklist.setHeaderData(column_indices['start_time'], Qt.Horizontal, "Start Time")
        # self.tracklist.setHeaderData(column_indices['full_song'], Qt.Horizontal, "Full Song?")

    def _setup_tracklist_delegate(self):
        self.tracklist.setItemDelegate(self.tracklist_delegate)

    def _connect_create_power_hour_button(self):
        self.createPowerHourButton.clicked.connect(self._export_power_hour)

    def _connect_track_errors(self):
        self.tracklist_model\
            .error_downloading\
            .connect(self._show_error_downloading)

        self.track_error_dispatcher\
            .track_invalid\
            .connect(self._show_track_error)

    def _show_error_downloading(self, url, error_message):
        self.statusBar.showMessage(
            f'Error downloading "{url}": {error_message}',
            ERROR_DISPLAY_TIME_IN_MS
        )

    def _show_track_error(self, error):
        if error['code'] == 'start_time_too_late':
            self.statusBar.showMessage(
                f"Error: Start time {error['start_time']} is greater than the track's length",
                ERROR_DISPLAY_TIME_IN_MS
            )
        elif error['code'] == 'start_time_format_bad':
            self.statusBar.showMessage(
                f"Error: Start time \"{error['start_time']}\" is not in a usable format",
                ERROR_DISPLAY_TIME_IN_MS
            )

    def _enable_create_power_hour_button_when_tracks_present(self):
        # self.tracklist_model\
        #     .new_power_hour_selected\
        #     .connect(self._try_to_enable_create_button)

        self.tracklist_model\
            .dataChanged\
            .connect(self._try_to_enable_create_button)

        self._try_to_enable_create_button()

    def _try_to_enable_create_button(self):
        self.createPowerHourButton.setEnabled(self.tracklist_model.is_valid_for_export())

    def _show_worker_error(self, message):
        show_error_message_box(parent=self, message=message)

    def _export_power_hour(self):
        power_hour_path = get_power_hour_export_path(
            parent=self,
            is_video=self._is_video_power_hour()
        )

        if power_hour_path:

            power_hour = PowerHour(
                tracks=self.tracklist_model.tracks,
                path=power_hour_path,
                is_video=self._is_video_power_hour(),
                name=self._current_power_hour_name()
            )

            create_power_hour_in_background(
                power_hour=power_hour,
                parent_widget=self,
                export_progress_view=self
            )

    def _is_video_power_hour(self):
        return self.videoCheckBox.checkState()

    def _show_power_hour_created(self):
        self.statusBar.showMessage("Power hour created!", CREATED_DISPLAY_TIME_IN_MS)

    def _connect_help_menu(self):
        def show_logs():
            show_log_folder_in_file_browser()

        def show_about_dialog():
            dialog = AboutDialog()
            dialog.exec_()

        self.actionShow_logs.triggered.connect(show_logs)
        self.actionAbout_Power_Hour_Creator.triggered.connect(show_about_dialog)

    def _connect_file_menu(self):
        def new_power_hour():
            power_hour_id = self.power_hour_model.add_power_hour()
            self.tracklist_model.add_tracks_to_new_power_hour(power_hour_id)
            self.tracklist_model.show_tracks_for_power_hour(power_hour_id)

        def export_current_tracklist():
            ph = PowerHour(
                tracks=self.tracklist_model.tracks,
                name=self._current_power_hour_name()
            )

            export_tracklist_to_file(parent_widget=self, power_hour=ph)

        def import_tracklist():
            import_tracklist_from_file(
                parent_widget=self,
                phs_list_model=self.power_hour_model,
                tracklist_model=self.tracklist_model
            )

        self.actionNew_Power_Hour.triggered.connect(new_power_hour)
        self.action_Export_Current_Tracklist.triggered.connect(export_current_tracklist)
        self.action_Import_Tracklist.triggered.connect(import_tracklist)

    def _connect_power_hour_list_view(self):
        def show_power_hour_name(new_index, _=None):
            ph_name = new_index.data()
            self.powerHourNameLabel.setText(ph_name)

        def show_renamed_power_hour_name(top_left_index, _):
            current_selection = self.powerHoursListView.selectionModel().selectedIndexes()
            if top_left_index in current_selection:
                show_power_hour_name(top_left_index)

        def show_this_power_hours_tracks(new_index, _):
            ph_id = new_index.sibling(new_index.row(), 0).data()
            self.tracklist_model.show_tracks_for_power_hour(ph_id)

        self.powerHoursListView.selectionModel().currentRowChanged.connect(show_power_hour_name)
        self.powerHoursListView.selectionModel().currentRowChanged.connect(show_this_power_hours_tracks)
        self.powerHoursListView.selectionModel().currentRowChanged.connect(self.tracklist.scrollToTop)
        self.powerHoursListView.selectionModel().currentRowChanged.connect(self._try_to_enable_create_button)

        self.powerHoursListView.model().dataChanged.connect(show_renamed_power_hour_name)

    def _current_power_hour_name(self):
        return self.powerHourNameLabel.text()

    def closeEvent(self, event):
        self._write_view_settings()

        event.accept()

    def _write_view_settings(self):
        self._settings.setValue('main_window/maximized', self.isMaximized())
        self._store_size_and_pos_unless_maximized()
        self._settings.setValue('splitter', self.splitter.saveState())

        self.tracklist.write_settings(self._settings)
        self.powerHoursListView.write_settings(self._settings)

    def _store_size_and_pos_unless_maximized(self):
        # https://stackoverflow.com/questions/74690/how-do-i-store-the-window-size-between-sessions-in-qt
        if not self.isMaximized():
            self._settings.setValue('main_window/size', self.size())
            self._settings.setValue('main_window/pos', self.pos())

    def _restore_view_settings(self):
        settings = self._settings

        self.resize(settings.value('main_window/size', QSize(800, 600)))
        self.move(settings.value('main_window/pos', QPoint(0, 0)))

        if settings.contains('splitter'):
            self.splitter.restoreState(settings.value('splitter'))

        self.tracklist.apply_settings(settings)
        self.powerHoursListView.apply_settings(settings)

    def show_with_last_full_screen_setting(self):
        if self._settings.value('main_window/maximized') == 'true':
            self.showMaximized()
        else:
            self.show()


def show_error_message_box(parent, message):
    msg_box = QMessageBox(parent)
    msg_box.setText('An error occured during power hour creation.')
    msg_box.setDetailedText(message)

    _force_message_box_to_be_wider(msg_box)
    msg_box.exec_()


def _force_message_box_to_be_wider(msg_box):
    # No easy or sensible way to set QMessageBox width, have to use this hack
    # http://www.qtcentre.org/threads/22298-QMessageBox-Controlling-the-width
    spacer = QSpacerItem(msg_box.parent().width() / 2, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
    box_layout = msg_box.layout()
    box_layout.addItem(spacer, box_layout.rowCount(), 0, 1, box_layout.columnCount())


class TrackErrorDispatch(QObject):
    track_invalid = pyqtSignal(dict)


def build_main_window():
    tracklist_model = TracklistModel()
    track_error_dispatcher = TrackErrorDispatch()
    return MainWindow(
        power_hour_model=PowerHourModel(),
        tracklist_model=tracklist_model,
        tracklist_delegate=TrackDelegate(
            track_error_dispatcher=track_error_dispatcher
        ),
        track_error_dispatcher=track_error_dispatcher
    )


def show_log_folder_in_file_browser():
    if config.OS == 'windows':
        os.startfile(config.APP_DIRS.user_log_dir, 'explore')
    elif config.OS == 'darwin':
        subprocess.check_call(['open', config.APP_DIRS.user_log_dir])


