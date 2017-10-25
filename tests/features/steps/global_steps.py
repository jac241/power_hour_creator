from behave import *

from power_hour_creator import config
from tests.features.models import remote_tracks, remote_videos, local_videos
from behave import *

from power_hour_creator import config
from tests.features.models import remote_tracks, remote_videos, local_videos


@when('I add {num_tracks} tracks to a power hour')
def step_impl(context, num_tracks):
    for track_num in range(int(num_tracks)):
        add_remote_song_to_tracklist(context)


def add_remote_song_to_tracklist(context, full_song=False, video=False, pos=False):
    tracks = remote_videos if video else remote_tracks
    add_song_to_tracklist(context, tracks=tracks, full_song=full_song, pos=pos)


def add_song_to_tracklist(context, tracks=remote_tracks, full_song=False, pos=None):
    track = tracks[context.num_tracks % len(tracks)]
    context.last_track_added = track
    context.tracklist_test_model.add_track(track, full_song, pos)

    # viewport = context.main_window.tracklist.viewport()
    #
    # # current_row = pos or context.num_tracks + 1
    # current_row = pos or context.tracklist_test_model.number_of_tracks()
    # url_cell_pos = tracklist_cell_pos(context, row=current_row, column=TracklistModel.Columns.url)
    #
    # QTest.mouseClick(viewport, Qt.LeftButton, pos=url_cell_pos)
    #
    #
    # QTest.keyClicks(viewport.focusWidget(), track.url)
    # QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)
    #
    # if full_song:
    #     full_song_cell_pos = tracklist_cell_pos(context, row=current_row, column=TracklistModel.Columns.full_song)
    #     QTest.mouseClick(viewport, Qt.LeftButton, pos=full_song_cell_pos)
    #     QTest.keyClick(viewport.focusWidget(), Qt.Key_Down)

    context.num_tracks += 1
    context.prhr_length += track.length if full_song or (track.length < config.track_length) else config.track_length


def add_local_song_to_tracklist(context):
    add_song_to_tracklist(context, tracks=local_videos)


