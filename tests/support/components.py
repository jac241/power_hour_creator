from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from tests.features.models import trigger_menu_action, TracklistTestModel, \
    TableViewHelper, ListViewHelper


class MainWindowComponent(object):
    def __init__(self, main_window):
        self.main_window = main_window

    def export_power_hour(self, export_path):
        self._open_file_menu()
        trigger_menu_action(
            action_name='&Export Current Tracklist',
            menu=self.main_window.menuFile
        )

    def import_power_hour(self, import_path):
        self._open_file_menu()
        trigger_menu_action(
            action_name='&Import Tracklist',
            menu=self.main_window.menuFile
        )

    def add_power_hour(self):
        self._open_file_menu()
        trigger_menu_action(
            action_name='&New Power Hour',
            menu=self.main_window.menuFile
        )

    def _open_file_menu(self):
        QTest.keyClick(self.main_window, 'F', Qt.AltModifier)

    @property
    def create_ph_button_enabled(self):
        return self.main_window.createPowerHourButton.isEnabled()


class PowerHourListComponent(object):
    def __init__(self, ph_list_view):
        self._ph_list_view = ph_list_view
        self._helper = ListViewHelper(ph_list_view)

    @property
    def power_hour_names(self):
        model = self._ph_list_view.model()
        for row in range(model.rowCount()):
            yield model.index(row, 1).data(Qt.DisplayRole)

    @property
    def num_power_hours(self):
        return self._ph_list_view.model().rowCount()

    def delete_power_hour(self, index):
        self._helper.select_row(index)
        trigger_menu_action(
            '&Delete',
            self.open_context_menu_at(position=self.row_pos(index))
        )

    @property
    def power_hour_is_selected(self):
        index = self._ph_list_view.selectedIndexes()[0]
        return index and index.row() < self.num_power_hours

    def row_pos(self, row):
        return self._helper.row_pos(row)

    def open_context_menu_at(self, position):
        return self._helper.open_context_menu_at(position)