from collections import namedtuple

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from phc.media_handling import InvalidURL, MissingURL, DownloadError,\
    FindMediaDescriptionService, Track


class Tracklist(QTableWidget):

    class Columns:
        url = 0
        title = 1
        track_length = 2
        start_time = 3

    def __init__(self, parent):
        super().__init__(parent)
        self._setup_signals()

    def add_track(self):
        self.insertRow(self.rowCount())

    @property
    def tracks(self):
        tracks = []
        for row in range(self.rowCount()):
            url_item = self.item(row, self.Columns.url)
            start_time_item = self.item(row, self.Columns.start_time)
            title_item = self.item(row, self.Columns.title)
            length_item = self.item(row, self.Columns.track_length)
            if url_item and start_time_item:
                url = url_item.text().strip()
                start_time = int(start_time_item.text())
                title = title_item.text() if title_item else ""
                length = length_item.text() if length_item else 0
                if url and start_time:
                    tracks.append(Track(url=url, start_time=start_time, title=title, length=length))
        return tracks

    def _setup_signals(self):
        self.cellChanged.connect(self._handle_cell_change)

    def _handle_cell_change(self, row, column):
        if column == self.Columns.url:
            url = self.item(row, column).text()
            self._update_row_with_video_info(url, row)

    def _update_row_with_video_info(self, url, row):
        try:
            track = FindMediaDescriptionService(url).execute()

            self.setItem(row, self.Columns.title, QTableWidgetItem(track.title))
            self.setItem(row, self.Columns.track_length, QTableWidgetItem(str(track.length)))
            self.setItem(row, self.Columns.start_time, QTableWidgetItem(str(track.start_time)))

        except MissingURL:
            pass
        except InvalidURL:
            pass
        except DownloadError:
            pass

    def _set_start_time_to_default(self, row):
        self.setItem(row, self.Columns.start_time,
                     QTableWidgetItem(str(self.DEFAULT_START_TIME)))

    def _last_row_index(self):
        return self.rowCount() - 1


class TracklistPresenter:
    def __init__(self, view):
        self._view = view

