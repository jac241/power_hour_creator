from unittest import TestCase
from unittest.mock import MagicMock, Mock

from PyQt5.QtCore import QAbstractItemModel, QModelIndex
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit
from PyQt5.QtWidgets import QTableWidgetItem
from decimal import Decimal

from power_hour_creator.ui.main_window import TrackErrorDispatch
from power_hour_creator.ui.tracklist import DisplayTime, Tracklist, \
    TrackDelegate
from tests.ui.support import QtTestCase


class TestDisplayTime(TestCase):
    def test_as_time_str_should_return_the_time_in_the_correct_format_if_no_milliseconds(self):
        time = DisplayTime(Decimal(181))
        self.assertEqual(time.as_time_str(), '03:01')

    def test_as_time_str_should_return_the_time_in_the_correct_format_with_milliseconds(self):
        time = DisplayTime('181.05')
        self.assertEqual(time.as_time_str(), '03:01.05')

    def test_as_time_str_should_return_the_same_string_if_passed_a_time_string(self):
        time = DisplayTime('15:45')
        self.assertEqual(time.as_time_str(), '15:45')

    def test_as_time_str_should_return_a_blank_string_if_passed_invalid_time(self):
        time = DisplayTime('aab')
        self.assertEqual(time.as_time_str(), '')

    def test_as_decimal_should_generate_decimal_from_time_str(self):
        time = DisplayTime('04:10.05')
        self.assertEqual(time.as_decimal(), Decimal('250.05'))

    def test_as_decimal_should_generate_decimal_if_only_seconds_given(self):
        time = DisplayTime('300.05')
        self.assertEqual(time.as_decimal(), Decimal('300.05'))

    def test_as_decimal_should_return_an_empty_string_if_there_are_letters(self):
        time = DisplayTime('aab')
        self.assertEqual(time.as_decimal(), '')

    def test_as_decimal_should_return_an_empty_string_if_the_time_is_empty(self):
        time = DisplayTime('')
        self.assertEqual(time.as_decimal(), '')

# class TestTrackDelegate(QtTestCase):
#     def setUp(self):
#         super().setUp()
#
#         self.uut = TrackDelegate(
#             track_error_dispatcher=TrackErrorDispatch()
#         )

