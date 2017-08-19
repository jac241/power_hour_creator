import os
import re
import time
from unittest.mock import Mock

import psutil
from PyQt5.Qt import Qt, QPoint
from PyQt5.QtCore import QModelIndex
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from behave import *
from hamcrest import *
from youtube_dl import DownloadError

from power_hour_creator.media import MediaFile
from power_hour_creator.ui.exporting import ExportPowerHourDialog
from power_hour_creator.ui.tracklist import DisplayTime, \
    DEFAULT_NUM_TRACKS, TracklistModel
from tests.features.environment import close_app, launch_app
from tests.features.steps.global_steps import add_remote_song_to_tracklist, \
    tracklist_cell_pos, add_local_song_to_tracklist, local_videos

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
    wait_for_progress_dialog_to_go_away(context)

    assert_that(os.path.exists(context.export_path), is_(True))
    assert_power_hour_is_correct_length(context)

def wait_for_progress_dialog_to_go_away(context):
    start = time.time()
    while export_dialog_visible(context):
        if time.time() - start > 300:
            break
        QTest.qWait(100)


def export_dialog_visible(context):
    export_dialog = get_export_dialog(context)
    return export_dialog.isVisible()


def get_export_dialog(context):
    return next((w for w in context.app.topLevelWidgets() if
                 type(w) is ExportPowerHourDialog), None)


@step("I should see the power hour created message")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that('created', is_in(context.main_window.statusBar.currentMessage()))


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
        column=TracklistModel.Columns.start_time
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
                              column=TracklistModel.Columns.start_time)
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
    from power_hour_creator.resources import ffmpeg_exe

    cmd = [
        ffmpeg_exe(),
        '-i', file,
        '-f', 'null', '-'
    ]

    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return DisplayTime(get_duration(output)).as_decimal()


def get_duration(output):
    return re.search("Duration: ..:(.*)\...,", output.decode()).group(1)


@step("I add a full song to the power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    add_remote_song_to_tracklist(context, full_song=True)


@when("I add 2 videos to a video power hour with one full song")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    add_remote_song_to_tracklist(context, video=True)
    add_remote_song_to_tracklist(context, full_song=True, video=True)


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
    wait_for_progress_dialog_to_go_away(context)

    assert_that(os.path.exists(context.export_path), is_(True))
    assert_power_hour_is_correct_length(context)
    assert_power_hour_is_a_video(context)


@when("I right click on the url of a row")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    viewport = context.main_window.tracklist.viewport()
    url_cell_pos = tracklist_cell_pos(context, row=1, column=TracklistModel.Columns.url)

    # Right click doesn't work for some reason...
    # QTest.mouseClick(viewport, Qt.RightButton, pos=url_cell_pos)

    context.tracklist._build_custom_menu(url_cell_pos)


@step("I add a track to the power hour at row {pos}")
def step_impl(context, pos):
    """
    :type context: behave.runner.Context
    """
    add_remote_song_to_tracklist(context, pos=int(pos))


@step("I choose to insert a row {direction} row {pos} with the context menu")
def step_impl(context, direction, pos):
    """
    :type context: behave.runner.Context
    """
    menu = open_context_menu_at(context, row=int(pos), column=TracklistModel.Columns.url)

    QTest.keyClick(menu, Qt.Key_Down)
    if direction == 'below':
        QTest.keyClick(menu, Qt.Key_Down)

    QTest.keyClick(menu, Qt.Key_Enter)


@then("the row count should have increased")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.tracklist_model.rowCount(),
                greater_than(DEFAULT_NUM_TRACKS))


@step("the second track should be above the first")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    first_track = context.main_window.tracklist_model.tracks[0]
    assert_that(first_track.url, is_(context.last_track_added.url))


@step("there should be {num_tracks} tracks in the power hour")
def step_impl(context, num_tracks):
    """
    :type context: behave.runner.Context
    """
    assert_that(len(context.main_window.tracklist_model.tracks), is_(int(num_tracks)))


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

    menu = open_context_menu_at(context, row=int(pos), column=TracklistModel.Columns.title)
    for _ in range(3):
        QTest.keyClick(menu, Qt.Key_Down)
    QTest.keyClick(menu, Qt.Key_Enter)


@when("I create a new power hour from the file menu")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    QTest.keyPress(context.main_window, Qt.Key_N, Qt.ControlModifier)


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



@then("I should see the new power hour name above the tracklist")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.powerHourNameLabel.text(), is_(new_ph_name))


@step("I reload the app")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    close_app(context)
    launch_app(context)


@step("I select the power hour I created")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    ph_list_view = context.main_window.powerHoursListView
    ph_list_view.setCurrentIndex(ph_list_view.model().index(1, 1))


@then("I should still see the tracks I added")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    tracks = context.main_window.tracklist_model.tracks
    assert_that(len(tracks), is_(2))
    assert_that(tracks[0].title, is_not(''))


@when("I remove all the tracks from a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    tracklist_model = context.main_window.tracklist_model
    tracklist_model.beginRemoveRows(QModelIndex(), 0, DEFAULT_NUM_TRACKS-1)
    query = QSqlQuery()
    result = query.exec_("DELETE FROM tracks")
    tracklist_model.endRemoveRows()
    tracklist_model.select()
    QTest.qWait(500)


@step("I add a new track to the power hour with the context menu")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.tracklist._build_custom_menu(QPoint(0, 0))
    menu = QApplication.activePopupWidget()
    QTest.keyClick(menu, Qt.Key_Down)
    QTest.keyClick(menu, Qt.Key_Enter)


@then("there should be a track in the power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.tracklist_model.rowCount(), is_(1))


@when("there's an error downloading track info")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    mock = Mock()
    context.expected_message = "Here's the message"
    mock.side_effect = DownloadError(context.expected_message)
    context.main_window.tracklist_model._show_track_details = mock
    add_remote_song_to_tracklist(context)


@then("I should see a message in the status bar")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    message = context.main_window.statusBar.currentMessage()
    assert_that(message, contains_string(context.last_track_added.url))
    assert_that(message, contains_string(context.expected_message))


@step("I click cancel")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    wait_for(export_dialog_visible, context)
    wait_for(lambda: len(psutil.Process().children()) > 0)

    dialog = get_export_dialog(context)
    dialog.cancelButton.click()


@then("I should see that the export is cancelling")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    dialog = get_export_dialog(context)
    assert_that(dialog.cancellingLabel.isVisible(), is_(True))

    wait_for_progress_dialog_to_go_away(context)


@then("that power hour should have been cancelled")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pnames = map(lambda p: p.name(), psutil.Process().children())
    for pname in pnames:
        assert_that("ffmpeg", not_(is_in(pname)))

    assert_that(os.path.exists(context.export_path), is_(False))


def wait_for(f, *fargs, **fkwargs):
    while not f(*fargs, **fkwargs):
        QTest.qWait(100)


@step("I should not see the power hour created message")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.main_window.statusBar.currentMessage(), is_(''))


@when("I add a local video to a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    add_local_song_to_tracklist(context)


@then("I should see that track's info")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    model = context.tracklist.model()
    track = model.tracks[0]
    file = local_videos[0]
    assert_that(track.url, is_(file.url))
    assert_that(track.title, is_(os.path.split(file.url)[1]))
    assert_that(track.length, is_(str(file.length)))
