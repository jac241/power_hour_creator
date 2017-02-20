import time
from behave import *
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QPoint
from unittest.mock import Mock
from hamcrest import *
import os
from power_hour_creator.ui.power_hour_creator_window import ExportPowerHourDialog


track_url = 'https://soundcloud.com/fsoe-excelsior/sodality-floe-running'

# @when("I add 2 tracks to a power hour")
# def step_impl(context):
#     """
#     :type context: behave.runner.Context
#     """
#     tracklist = context.main_window.tracklist
#     viewport = tracklist.viewport()
#     for track_num in range(2):
#         add_track_to_power_hour(track_num, tracklist, viewport)
#

def add_track_to_power_hour(track_num, tracklist, viewport):
    url_cell_pos = QPoint(tracklist.columnViewportPosition(0),
                          tracklist.rowViewportPosition(track_num + 1))
    QTest.mouseClick(viewport, Qt.LeftButton, pos=url_cell_pos)
    QTest.mouseDClick(viewport, Qt.LeftButton, pos=url_cell_pos)
    QTest.keyClicks(viewport.focusWidget(), track_url)
    QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)


@step("I create a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    context.export_path = os.path.join(context.support_path, 'exports/test.aac')

    context.main_window.get_export_path = Mock()
    context.main_window.get_export_path.return_value = context.export_path

    QTest.mouseClick(context.main_window.createPowerHourButton, Qt.LeftButton)


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


def tracklist_cell_pos(context, row, column):
    tracklist = context.main_window.tracklist

    return QPoint(
        tracklist.columnViewportPosition(column),
        tracklist.rowViewportPosition(row)
    )


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