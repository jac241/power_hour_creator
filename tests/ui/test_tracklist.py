from unittest import TestCase

from power_hour_creator.ui.tracklist import DisplayTime


class TestDisplayTime(TestCase):
    def setUp(self):
        super().setUp()

    def test_as_time_str_should_return_the_time_in_the_correct_format(self):
        time = DisplayTime(181)
        self.assertEqual(time.as_time_str(), '03:01')

    def test_as_time_str_should_return_the_same_string_if_passed_a_time_string(self):
        time = DisplayTime('15:45')
        self.assertEqual(time.as_time_str(), '15:45')

    def test_as_time_str_should_return_a_blank_string_if_passed_invalid_time(self):
        time = DisplayTime('aab')
        self.assertEqual(time.as_time_str(), '')

    def test_as_seconds_should_generate_seconds_from_time_str(self):
        time = DisplayTime('04:10')
        self.assertEqual(time.as_seconds(), 250)

    def test_as_seconds_should_generate_seconds_if_only_seconds_given(self):
        time = DisplayTime('300')
        self.assertEqual(time.as_seconds(), 300)

    def test_as_seconds_should_return_an_empty_string_if_there_are_letters(self):
        time = DisplayTime('aab')
        self.assertEqual(time.as_seconds(), '')

    def test_as_seconds_should_return_an_empty_string_if_the_time_is_empty(self):
        time = DisplayTime('')
        self.assertEqual(time.as_seconds(), '')
