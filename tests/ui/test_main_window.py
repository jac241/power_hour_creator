import pytest

from power_hour_creator.ui.main_window import build_main_window


@pytest.fixture
def main_window(qtbot):
    mw = build_main_window()
    qtbot.add_widget(mw)
    return mw


def test_main_window_should_show_start_time_validation_errors(main_window):
    error = {
        'code': 'start_time_too_late',
        'start_time': '0:45'
    }

    main_window.track_error_dispatcher.track_invalid.emit(error)

    assert 'Error' in main_window.statusBar.currentMessage()
    assert '0:45' in main_window.statusBar.currentMessage()

