import os
from collections import namedtuple
from PyQt5.QtCore import QPoint
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt
from behave import *

from power_hour_creator.config import ROOT_DIR
from power_hour_creator.media import TRACK_LENGTH
from power_hour_creator.ui.tracklist import TracklistModel
from tests.features.environment import SUPPORT_PATH

Track = namedtuple('Track', 'url length')
remote_tracks = [
    Track('https://soundcloud.com/dan-weniger/dead-winter', 136),
    Track('https://www.youtube.com/watch?v=JzkvgqTcmmY', 110)
]

remote_videos = [
    Track('https://www.youtube.com/watch?v=XSVunk2LUAo', 202),
    Track('https://www.youtube.com/watch?v=JzkvgqTcmmY', 110)
]

local_videos = [
    Track(
        url=os.path.join(SUPPORT_PATH, 'videos', "Beagle fires back at Kessel - 'I'm deeply hurt'.mp4"),
        length=77
    )
]


@when('I add {num_tracks} tracks to a power hour')
def step_impl(context, num_tracks):
    for track_num in range(int(num_tracks)):
        add_remote_song_to_tracklist(context)


def add_remote_song_to_tracklist(context, full_song=False, video=False, pos=False):
    tracks = remote_videos if video else remote_tracks
    add_song_to_tracklist(context, tracks=tracks, full_song=full_song, pos=pos)


def add_song_to_tracklist(context, tracks=remote_tracks, full_song=False, pos=None):
    viewport = context.main_window.tracklist.viewport()

    current_row = pos or context.num_tracks + 1
    url_cell_pos = tracklist_cell_pos(context, row=current_row, column=TracklistModel.Columns.url)

    QTest.mouseClick(viewport, Qt.LeftButton, pos=url_cell_pos)

    track = tracks[context.num_tracks % len(tracks)]
    context.last_track_added = track

    QTest.keyClicks(viewport.focusWidget(), track.url)
    QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)

    if full_song:
        full_song_cell_pos = tracklist_cell_pos(context, row=current_row, column=TracklistModel.Columns.full_song)
        QTest.mouseClick(viewport, Qt.LeftButton, pos=full_song_cell_pos)
        QTest.keyClick(viewport.focusWidget(), Qt.Key_Down)

    context.num_tracks += 1
    context.prhr_length += track.length if full_song else TRACK_LENGTH


def add_local_song_to_tracklist(context):
    add_song_to_tracklist(context, tracks=local_videos)


def tracklist_cell_pos(context, row, column):
    tracklist = context.main_window.tracklist

    return QPoint(
        tracklist.columnViewportPosition(column),
        tracklist.rowViewportPosition(row)
    )
