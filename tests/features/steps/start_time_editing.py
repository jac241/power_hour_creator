from PyQt5.QtCore import Qt

from PyQt5.QtTest import QTest
from behave import *
from hamcrest import *

from power_hour_creator.ui.tracklist import DisplayTime

use_step_matcher("re")


@then("I should see the start time in the correct format")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    tracklist = context.main_window.tracklist
    columns = tracklist.Columns
    start_time_text = DisplayTime(tracklist.item(1, columns.start_time).text())
    assert_that(start_time_text.as_time_str(), is_("00:30"))
