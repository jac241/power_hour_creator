from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from tests.features.models import trigger_menu_action, TracklistTestModel

class MainWindowComponent(object):
    def __init__(self, main_window):
        self.main_window = main_window

    def export_power_hour(self, export_path):
        QTest.keyClick(self.main_window, 'F', Qt.AltModifier)
        trigger_menu_action(
            action_name='&Export Current Tracklist',
            menu=self.main_window.menuFile
        )

    def import_power_hour(self, import_path):
        QTest.keyClick(self.main_window, 'F', Qt.AltModifier)
        trigger_menu_action(
            action_name='&Import Tracklist',
            menu=self.main_window.menuFile
        )

    @property
    def create_ph_button_enabled(self):
        return self.main_window.createPowerHourButton.isEnabled()


class PowerHourListComponent(object):
    def __init__(self, ph_list_view):
        self._ph_list_view = ph_list_view

    @property
    def power_hour_names(self):
        model = self._ph_list_view.model()
        for row in range(model.rowCount()):
            yield model.index(row, 1).data(Qt.DisplayRole)

