from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QLineEdit
from decimal import Decimal

from power_hour_creator import config
from power_hour_creator.ui.tracklist import TracklistModel


class TracklistTestModel:
    def __init__(self, tracklist):
        self._tracks = []
        self.tracklist = tracklist

    def add_track(self, track, full_song, pos):
        self._tracks.append(track)

        viewport = self.tracklist.viewport()

        current_row = pos or self.number_of_tracks()
        url_cell_pos = self.cell_pos(track_num=current_row,
                                     column=TracklistModel.Columns.url)

        QTest.mouseClick(viewport, Qt.LeftButton, pos=url_cell_pos)

        QTest.keyClicks(viewport.focusWidget(), track.url)
        QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)

        if full_song:
            full_song_cell_pos = self.cell_pos(
                track_num=current_row,
                column=TracklistModel.Columns.full_song
            )

            QTest.mouseClick(viewport, Qt.LeftButton, pos=full_song_cell_pos)
            QTest.keyClick(viewport.focusWidget(), Qt.Key_Down)

    def last_track_added(self):
        return self._tracks[-1]

    def number_of_tracks(self):
        return len(self._tracks)

    def set_track_start_time(self, track_num, start_time):
        cell = self.cell_pos(track_num, TracklistModel.Columns.start_time)

        viewport = self.tracklist.viewport()
        QTest.mouseClick(viewport, Qt.LeftButton, pos=cell)
        QTest.keyClicks(viewport.focusWidget(), str(start_time))
        QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)

    def cell_pos(self, track_num, column):
        row = int(track_num)

        return QPoint(
            self.tracklist.columnViewportPosition(column),
            self.tracklist.rowViewportPosition(row)
        )

    def track_start_time(self, track_index):
        return self._cell_text(row=track_index,
                               column=TracklistModel.Columns.start_time)

    def _cell_text(self, row, column):
        delegate = self.tracklist.itemDelegate()
        editor = QLineEdit()
        delegate.setEditorData(editor, self.tracklist.model().index(row, column))

        return editor.text()

    @property
    def power_hour_length(self):
        length = 0
        tracks = (TestTrack(t) for t in self.tracklist.model().tracks)
        for track in tracks:
            if track.full_song:
                length += track.length
            else:
                length += min(config.track_length, track.length - track.start_time)
        return account_for_rounding(length)


def account_for_rounding(length):
    return length - 1


class TestTrack:
    def __init__(self, track):
        self.track = track

    @property
    def full_song(self):
        return self.track.full_song

    @property
    def length(self):
        return Decimal(self.track.length)

    @property
    def start_time(self):
        return self.track.start_time


def tracklist_cell_pos(context, row, column):
    tracklist = context.main_window.tracklist

    return QPoint(
        tracklist.columnViewportPosition(column),
        tracklist.rowViewportPosition(row)
    )