import time
from behave import *
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QPoint
from unittest.mock import Mock
from hamcrest import *
import os
import re

from power_hour_creator.ui.power_hour_creator_window import ExportPowerHourDialog
from power_hour_creator.ui.tracklist import DisplayTime
from power_hour_creator.media_handling import TRACK_LENGTH

from tests.features.steps.global_steps import add_song_to_tracklist, tracklist_cell_pos


track_url = 'https://soundcloud.com/fsoe-excelsior/sodality-floe-running'


@step("I create a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    context.export_path = os.path.join(context.support_path, 'exports/test.m4a')

    context.main_window.get_export_path = Mock()
    context.main_window.get_export_path.return_value = context.export_path

    QTest.mouseClick(context.main_window.createPowerHourButton, Qt.LeftButton)


def assert_power_hour_is_correct_length(context):
    assert_that(duration(context.export_path), greater_than_or_equal_to(context.prhr_length))


@then("that power hour should have been created")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    def export_dialog_visible():
        export_dialog = next((w for w in context.app.topLevelWidgets() if type(w) is ExportPowerHourDialog), None)
        return export_dialog.isVisible()

    start = time.time()
    while export_dialog_visible():
        if time.time() - start > 120:
            break
        QTest.qWait(100)

    assert_that(os.path.exists(context.export_path), is_(True))
    assert_power_hour_is_correct_length(context)


@step("I click around the tracklist start times")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    tracklist = context.main_window.tracklist
    viewport = tracklist.viewport()

    blank_start_time_cell = tracklist_cell_pos(
        context,
        row=5,
        column=tracklist.Columns.start_time
    )

    another_cell = tracklist_cell_pos(context, row=5, column=0)

    QTest.mouseClick(viewport, Qt.LeftButton, pos=blank_start_time_cell)
    QTest.mouseClick(viewport, Qt.LeftButton, pos=another_cell)


@step("I set track {}'s start time to {}")
def step_impl(context, track_num, start_time):
    """
    :type context: behave.runner.Context
    :type track_num: str
    :type start_time: str
    """
    cell = tracklist_cell_pos(context,
                              row=int(track_num),
                              column=context.tracklist.Columns.start_time)
    QTest.mouseClick(context.tracklist.viewport(), Qt.LeftButton, pos=cell)

    QTest.keyClicks(context.tracklist.viewport().focusWidget(), start_time)
    QTest.keyClick(context.tracklist.viewport().focusWidget(), Qt.Key_Return)


@when("I forget to add a track to the power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@then("I should not be able to create a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.createPowerHourButton.isEnabled(), is_(False))


def duration(file):
    import subprocess
    from power_hour_creator.media_handling import ffmpeg_exe

    cmd = [
        ffmpeg_exe(),
        '-i', file,
        '-f', 'null', '-'
    ]

    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return DisplayTime(get_duration(output)).as_seconds()


def get_duration(output):
    return re.search("Duration: ..:(.*)\...,", output.decode()).group(1)


@step("I add a full song to the power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    add_song_to_tracklist(context, full_song=True)
