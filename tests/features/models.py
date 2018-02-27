import os
from collections import namedtuple

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QLineEdit, QApplication
from decimal import Decimal

from power_hour_creator import config
from power_hour_creator.ui.tracklist import TracklistModel
from tests.config import SUPPORT_PATH

Track = namedtuple('Track', 'url length')
remote_tracks = [
    Track('https://www.youtube.com/watch?v=EK_voX9LaPA', 105),
    Track('https://www.youtube.com/watch?v=JzkvgqTcmmY', 110)
]
remote_videos = [
    Track('https://www.youtube.com/watch?v=XSVunk2LUAo', 202),
    Track('https://www.youtube.com/watch?v=JzkvgqTcmmY', 110)
]
local_videos = [
    Track(
        url=os.path.join(SUPPORT_PATH, 'videos', "cc_roller_coaster.mp4"),
        length=32
    )
]


def get_local_video():
    return local_videos[0]


class TracklistTestModel:
    def __init__(self, tracklist):
        self._tracks = []
        self.tracklist = tracklist
        self._table = TableViewHelper(view=tracklist)

    def add_track(self, track=get_local_video(), full_song=False, pos=None):
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
        return self._table.cell_pos(row, column)

    def row_pos(self, row):
        return self._table.row_pos(row)

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
        tracks = (TestTrack(t) for t in self.tracks)
        for track in tracks:
            if track.full_song:
                length += track.length
            else:
                length += min(config.track_length, track.length - track.start_time)
        return account_for_rounding(length)

    @property
    def tracks(self):
        return self.tracklist.model().tracks

    def add_track_below(self, row):
        self._table.select_row(row)

        trigger_menu_action(
            'Insert Track &Below',
            self._table.open_context_menu_on_row(row)
        )

    @property
    def row_count(self):
        return self.tracklist.model().rowCount()

    def delete_track(self, row):
        self._table.select_row(row)
        menu = self._table.open_context_menu_at(self._table.row_pos(row))
        trigger_menu_action('&Delete Selected Tracks', menu)

    def add_local_song_through_context_menu(self, row=1):
        self._table.select_row(row)

        trigger_menu_action(
            'Browse for local &video file',
            self._table.open_context_menu_on_row(row)
        )

    def open_context_menu_at(self, position):
        return self._table.open_context_menu_at(position)


class ItemViewHelper:
    def __init__(self, view):
        self.view = view

    def open_context_menu_at(self, position):
        self.view.show_context_menu(position)
        return QApplication.activePopupWidget()

    def open_context_menu_on_row(self, row):
        pos = self.row_pos(row)
        self.view.show_context_menu(pos)
        return QApplication.activePopupWidget()

    def select_row(self, row):
        pos = self.row_pos(row)
        QTest.mouseClick(self.view.viewport(), Qt.LeftButton, pos=pos)

    def row_pos(self, row):
        raise NotImplementedError


class TableViewHelper(ItemViewHelper):
    def cell_pos(self, row, column):
        return QPoint(
            self.view.columnViewportPosition(column),
            self.view.rowViewportPosition(row)
        )

    def row_pos(self, row, column=0):
        return self.cell_pos(row, column)


class ListViewHelper(ItemViewHelper):
    def row_pos(self, row):
        item = self.view.model().index(row, 0)
        row_rect = self.view.visualRect(item)
        return row_rect.center()


def account_for_rounding(length):
    return length - 1


def tracklist_cell_pos(context, row, column):
    tracklist = context.main_window.tracklist

    return QPoint(
        tracklist.columnViewportPosition(column),
        tracklist.rowViewportPosition(row)
    )


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


def trigger_menu_action(action_name, menu):
    # https://stackoverflow.com/questions/16536286/qt-ui-testing-how-to-simulate-a-click-on-a-qmenubar-item-using-qtest
    for action in menu.actions():
        if action.text() == action_name:
            action.trigger()
            menu.hide()
            break
    else:
        raise RuntimeError(
            f'Action "{action_name}" not found in {menu.objectName()}')
