import pytest
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from power_hour_creator.ui.power_hour_list import PowerHourListView


@pytest.fixture
def item_model():
    model = QStandardItemModel()
    items = [str(i) for i in range(4)]
    for index, item in enumerate(items):
        model.setItem(index, 0, QStandardItem(item))
        model.setItem(index, 1, QStandardItem('Name'))
    return model


@pytest.fixture
def power_hour_list_view(qtbot, item_model):
    view = PowerHourListView()
    qtbot.add_widget(view)
    view.setModel(item_model)
    return view


class MockSettings:
    def __init__(self, settings={}):
        self._settings = settings

    def value(self, key, default):
        return self._settings.get(key, default)

    def setValue(self, key, value):
        self._settings[key] = value


def test_apply_settings_sets_the_index_from_settings(power_hour_list_view):
    index = 2
    settings = MockSettings({'power_hour_list_view/row': index})
    power_hour_list_view.apply_settings(settings)
    assert power_hour_list_view.currentIndex().row() == index


def test_apply_settings_sets_row_to_zero_if_stored_index_out_of_bounds(power_hour_list_view, item_model):
    index = item_model.rowCount()
    settings = MockSettings({'power_hour_list_view/row': index})
    power_hour_list_view.apply_settings(settings)
    assert power_hour_list_view.currentIndex().row() == 0

