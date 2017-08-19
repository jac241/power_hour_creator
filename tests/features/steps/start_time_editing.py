from PyQt5.QtCore import Qt

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QLineEdit
from behave import *
from hamcrest import *

from power_hour_creator.ui.tracklist import DisplayTime, TracklistModel

use_step_matcher("re")


@then("I should see the start time in the correct format")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    start_time_text = \
        context.tracklist_test_model.track_start_time(track_index=1)

    assert_that(start_time_text, is_("00:00"))


@step("I set the track's start time to something equal to the track length")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    track = context.tracklist_test_model.last_track_added()
    context.bad_start_time = DisplayTime(track.length + 1).as_time_str()
    context.tracklist_test_model.set_track_start_time(1, context.bad_start_time)


@then("there should be an error that the start time is invalid")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(
        context.main_window.statusBar.currentMessage(),
        is_("Error: Start time {} is greater than the track's length".format(context.bad_start_time))
    )


@step("the track's start time should be set blank")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    start_time = context.tracklist_test_model.track_start_time(track_index=1)
    assert_that(start_time, is_(''))