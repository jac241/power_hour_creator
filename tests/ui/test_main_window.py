from hamcrest import assert_that, contains_string

from power_hour_creator.ui.main_window import build_main_window
from tests.ui.support import QtTestCase


class TestMainWindow(QtTestCase):
    def setUp(self):
        super().setUp()

        self.uut = build_main_window(self.qapp)

    def test_should_show_start_time_validation_errors(self):
        error = {
            'code': 'start_time_too_late',
            'start_time': '0:45'
        }

        self.uut.track_error_dispatcher.track_invalid.emit(error)

        assert_that(self.uut.statusBar.currentMessage(),
                    contains_string('Error'))
        assert_that(self.uut.statusBar.currentMessage(),
                    contains_string('0:45'))
