import pytest
from PyQt5.QtWidgets import QApplication
import sys

from power_hour_creator import config
from power_hour_creator.boot import bootstrap_app_environment
from power_hour_creator.ui.main_window import build_main_window
from tests.support.components import *
from tests.features.environment import delete_export_files, clean_database


@pytest.yield_fixture(scope='function')
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


@pytest.fixture
def main_window_component(main_window):
    return MainWindowComponent(main_window)


@pytest.fixture
def tracklist_component(main_window):
    return TracklistTestModel(main_window.tracklist)


@pytest.fixture
def phs_list_component(main_window):
    return PowerHourListComponent(main_window.powerHoursListView)

