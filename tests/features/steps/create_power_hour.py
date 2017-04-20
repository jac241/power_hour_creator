import time

from PyQt5.QtWidgets import QApplication
from behave import *
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QPoint
from unittest.mock import Mock
from hamcrest import *
import os
import re

from power_hour_creator.ui.power_hour_creator_window import ExportPowerHourDialog
from power_hour_creator.ui.tracklist import DisplayTime, Tracklist, \
    DEFAULT_NUM_TRACKS
from power_hour_creator.media import TRACK_LENGTH, MediaFile

from tests.features.steps.global_steps import add_song_to_tracklist, tracklist_cell_pos


track_url = 'https://soundcloud.com/fsoe-excelsior/sodality-floe-running'
new_ph_name = "My Power Hour"


@step("I create a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    context.export_path = os.path.join(context.support_path, 'exports/test.m4a')

    context.main_window.get_power_hour_path = Mock()
    context.main_window.get_power_hour_path.return_value = context.export_path

    QTest.mouseClick(context.main_window.createPowerHourButton, Qt.LeftButton)


def assert_power_hour_is_correct_length(context):
    assert_that(duration(context.export_path), greater_than_or_equal_to(context.prhr_length))


@then("that power hour should have been created")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    wait_for_power_hour_creation(context)

    assert_that(os.path.exists(context.export_path), is_(True))
    assert_power_hour_is_correct_length(context)


def wait_for_power_hour_creation(context):
    def export_dialog_visible():
        export_dialog = next((w for w in context.app.topLevelWidgets() if
                              type(w) is ExportPowerHourDialog), None)
        return export_dialog.isVisible()

    start = time.time()
    while export_dialog_visible():
        if time.time() - start > 300:
            break
        QTest.qWait(100)


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
    from power_hour_creator.media import ffmpeg_exe

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


@when("I add 2 videos to a video power hour with one full song")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    add_song_to_tracklist(context, video=True)
    add_song_to_tracklist(context, full_song=True, video=True)


@step("I create a video power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.main_window.videoCheckBox.setCheckState(Qt.Checked)

    context.export_path = os.path.join(context.support_path, 'exports/test.mp4')

    context.main_window.get_power_hour_path = Mock()
    context.main_window.get_power_hour_path.return_value = context.export_path

    QTest.mouseClick(context.main_window.createPowerHourButton, Qt.LeftButton)


def assert_power_hour_is_a_video(context):
    info = MediaFile.read_info(context.export_path)
    assert_that(info['streams'][0]['codec_type'], is_('video'))


@then("that video power hour should have been created")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    wait_for_power_hour_creation(context)

    assert_that(os.path.exists(context.export_path), is_(True))
    assert_power_hour_is_correct_length(context)
    assert_power_hour_is_a_video(context)


@when("I right click on the url of a row")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    viewport = context.main_window.tracklist.viewport()
    QTest.qWait(1000)
    url_cell_pos = tracklist_cell_pos(context, row=1, column=Tracklist.Columns.url)

    # Right click doesn't work for some reason...
    # QTest.mouseClick(viewport, Qt.RightButton, pos=url_cell_pos)

    context.tracklist._build_custom_menu(url_cell_pos)


@step("I add a track to the power hour at row {pos}")
def step_impl(context, pos):
    """
    :type context: behave.runner.Context
    """
    add_song_to_tracklist(context, pos=int(pos))


@step("I choose to insert a row {direction} row {pos} with the context menu")
def step_impl(context, direction, pos):
    """
    :type context: behave.runner.Context
    """
    menu = open_context_menu_at(context, row=int(pos), column=Tracklist.Columns.url)

    QTest.keyClick(menu, Qt.Key_Down)
    if direction == 'below':
        QTest.keyClick(menu, Qt.Key_Down)

    QTest.keyClick(menu, Qt.Key_Enter)


@then("the row count should have increased")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.tracklist.rowCount(),
                greater_than(DEFAULT_NUM_TRACKS))


@step("the second track should be above the first")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    first_track = context.tracklist.tracks[0]
    assert_that(first_track.url, is_(context.last_track_added.url))


@step("there should be {num_tracks} tracks in the power hour")
def step_impl(context, num_tracks):
    """
    :type context: behave.runner.Context
    """
    assert_that(len(context.tracklist.tracks), is_(int(num_tracks)))


def open_context_menu_at(context, row, column):
    viewport = context.main_window.tracklist.viewport()
    url_cell_pos = tracklist_cell_pos(context, row=row, column=column)

    QTest.mouseClick(viewport, Qt.LeftButton, pos=url_cell_pos)
    # Right click doesn't work for some reason...
    # QTest.mouseClick(viewport, Qt.RightButton, pos=url_cell_pos)

    context.tracklist._build_custom_menu(url_cell_pos)

    return QApplication.activePopupWidget()


@step("I choose to delete the tracks at row {pos}")
def step_impl(context, pos):
    """
    :type context: behave.runner.Context
    """
    viewport = context.tracklist.viewport()

    menu = open_context_menu_at(context, row=int(pos), column=Tracklist.Columns.title)
    for _ in range(3):
        QTest.keyClick(menu, Qt.Key_Down)
    QTest.keyClick(menu, Qt.Key_Enter)
    QTest.qWait(1000)


@when("I create a new power hour from the file menu")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    QTest.keyPress(context.main_window, Qt.Key_N, Qt.ControlModifier)
    QTest.qWait(500)


@step("I change that power hour's name")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    ph_list_view = context.main_window.powerHoursListView

    # Can't figure out how to click on a qlistview...
    # ph_list_view.edit(ph_list_view.model().index(0,0))
    #
    # QTest.keyClicks(viewport.focusWidget(), new_ph_name)
    # QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)

    model = ph_list_view.model()
    index = model.index(1, 1)
    model.setData(index, new_ph_name)
    model.submitAll()
    QTest.qWait(2000)



@then("I should see the new power hour name above the tracklist")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.powerHourNameLabel.text(), is_(new_ph_name))