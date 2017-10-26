import simplejson as json
import os
import sys
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from decimal import Decimal

from PyQt5.QtWidgets import QApplication

from power_hour_creator import config
import power_hour_creator.ui.tracklist_export
from power_hour_creator.boot import bootstrap_app_environment
from power_hour_creator.ui.main_window import build_main_window
from power_hour_creator.ui.power_hour_list import DEFAULT_PR_HR_NAME
from tests.config import SUPPORT_PATH
from tests.features.environment import delete_export_files, clean_database
from tests.features.models import TracklistTestModel, get_local_video
from tests.ui.test_power_hour_list import MockSettings


@pytest.yield_fixture
def ph_app():
    app = QApplication(sys.argv)
    config.phc_env = 'test'
    bootstrap_app_environment()

    yield app

    delete_export_files()
    clean_database()
    del app


@pytest.fixture
def main_window(ph_app, qtbot):
    mw = build_main_window()
    mw.show()
    qtbot.add_widget(mw)
    return mw


class MainWindowComponent(object):
    def __init__(self, main_window):
        self.main_window = main_window

    def export_power_hour(self, export_path):
        self.trigger_menu_action(
            action_name='&Export Current Tracklist',
            menu=self.main_window.menuFile
        )

    def trigger_menu_action(self, action_name, menu):
        # https://stackoverflow.com/questions/16536286/qt-ui-testing-how-to-simulate-a-click-on-a-qmenubar-item-using-qtest
        QTest.keyClick(self.main_window, 'F', Qt.AltModifier)
        for action in menu.actions():
            if action.text() == action_name:
                QTest.keyClick(menu, Qt.Key_Enter)
                break
            QTest.keyClick(menu, Qt.Key_Down)
        else:
            raise RuntimeError(
                f'Action "{action_name}" not found in {menu.objectName()}')

    def import_power_hour(self, import_path):
        self.trigger_menu_action(
            action_name='&Import Tracklist',
            menu=self.main_window.menuFile
        )

@pytest.fixture
def main_window_component(main_window):
    return MainWindowComponent(main_window)


@pytest.fixture
def tracklist_component(main_window):
    return TracklistTestModel(main_window.tracklist)


def test_exporting_power_hour_creates_json_file(
        main_window_component,
        tracklist_component,
        monkeypatch):
    export_path = os.path.join(SUPPORT_PATH, 'exports', 'test.json')

    monkeypatch.setattr(
        target=power_hour_creator.ui.tracklist_export,
        name='get_tracklist_export_path',
        value=lambda parent_widget: (export_path, '')
    )

    tracklist_component.add_track(get_local_video(), full_song=True)
    tracklist_component.set_track_start_time(1, 15.45)
    main_window_component.export_power_hour(export_path)

    with open(export_path, 'r') as f:
        ph_json = json.load(f, use_decimal=True)

    track = tracklist_component.tracks[0]

    assert ph_json == {
        'name': DEFAULT_PR_HR_NAME,
        'tracks': [{
            'url': track.url,
            'title': 'cc_roller_coaster.mp4',
            'length': 32,
            'full_song': 1,
            '_start_time': Decimal(15.45),
        }]
    }


class PowerHourListComponent(object):
    def __init__(self, ph_list_view):
        self._ph_list_view = ph_list_view

    @property
    def power_hour_names(self):
        model = self._ph_list_view.model()
        for row in range(model.rowCount()):
            yield model.index(row, 1).data(Qt.DisplayRole)


@pytest.fixture
def phs_list_component(main_window):
    return PowerHourListComponent(main_window.powerHoursListView)


def test_importing_power_hour_creates_a_power_hour(
        main_window_component,
        phs_list_component,
        tracklist_component,
        monkeypatch):
    import_path = os.path.join(SUPPORT_PATH, 'tester.json')

    monkeypatch.setattr(
        target=power_hour_creator.ui.tracklist_import,
        name='get_import_path',
        value=lambda parent_widget: (import_path, '')
    )

    main_window_component.import_power_hour(import_path)
    assert 'Tester' in phs_list_component.power_hour_names
    assert len(tracklist_component.tracks) == 3


