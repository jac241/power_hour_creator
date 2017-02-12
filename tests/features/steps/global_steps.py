from PyQt5.QtCore import QPoint
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt
from behave import *

track_urls = [
    'https://soundcloud.com/fsoe-excelsior/sodality-floe-running',
    'https://www.youtube.com/watch?v=tGuNdkyvfSc'
]


@when('I add {num_tracks} tracks to a power hour')
def step_impl(context, num_tracks):
    tracklist = context.main_window.tracklist
    viewport = tracklist.viewport()
    for track_num in range(int(num_tracks)):
        url_cell_pos = QPoint(tracklist.columnViewportPosition(0),
                              tracklist.rowViewportPosition(track_num + 1))
        QTest.mouseClick(viewport, Qt.LeftButton, pos=url_cell_pos)
        # QTest.mouseDClick(viewport, Qt.LeftButton, pos=url_cell_pos)
        track_url = track_urls[track_num % 2]
        QTest.keyClicks(viewport.focusWidget(), track_url)
        QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)
