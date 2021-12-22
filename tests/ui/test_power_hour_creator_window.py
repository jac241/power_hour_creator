import pytest

from power_hour_creator.media import PowerHour
from power_hour_creator.ui.creation import CreatePowerHourDialog


@pytest.fixture
def power_hour():
    return PowerHour(tracks=[], path="~", is_video=True, name="MyPowerHour")


@pytest.fixture
def create_power_hour_dialog(qtbot, power_hour):

    dlg = CreatePowerHourDialog(parent=None, power_hour=power_hour)
    qtbot.add_widget(dlg)
    return dlg


def test_init_should_set_title_from_power_hour(create_power_hour_dialog):
    assert create_power_hour_dialog.windowTitle() == "Exporting: MyPowerHour"
