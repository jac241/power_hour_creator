from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QLineEdit

from power_hour_creator.ui.tracklist import TracklistModel


class TracklistTestModel:
    def __init__(self, context):
        self._tracks = []
        self._context = context

    def add_track(self, track):
        self._tracks.append(track)

    def last_track_added(self):
        return self._tracks[-1]

    def number_of_tracks(self):
        return len(self._tracks)

    def set_track_start_time(self, track_num, start_time):
        cell = tracklist_cell_pos(self._context,
                                  row=int(track_num),
                                  column=TracklistModel.Columns.start_time)

        QTest.mouseClick(
            self._context.tracklist.viewport(),
            Qt.LeftButton,
            pos=cell
        )

        QTest.keyClicks(
            self._context.tracklist.viewport().focusWidget(),
            str(start_time)
        )

        QTest.keyClick(
            self._context.tracklist.viewport().focusWidget(),
            Qt.Key_Return
        )

    def track_start_time(self, track_index):
        return self._cell_text(row=track_index,
                               column=TracklistModel.Columns.start_time)

    def _cell_text(self, row, column):
        tracklist = self._context.main_window.tracklist

        delegate = tracklist.itemDelegate()
        editor = QLineEdit()
        delegate.setEditorData(editor, tracklist.model().index(row, column))

        return editor.text()


def tracklist_cell_pos(context, row, column):
    tracklist = context.main_window.tracklist

    return QPoint(
        tracklist.columnViewportPosition(column),
        tracklist.rowViewportPosition(row)
    )