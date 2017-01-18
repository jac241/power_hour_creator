from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from youtube_dl import YoutubeDL
from pprint import pprint


class Tracklist(QTableWidget):

    class Columns:
        url = 0
        title = 1
        track_length = 2
        start_time = 3

    DEFAULT_START = 30

    def __init__(self, parent):
        super().__init__(parent)

        self.setup_signals()

    def setup_signals(self):
        self.cellChanged.connect(self.handle_cell_change)

    def handle_cell_change(self, row, column):
        if column == self.Columns.url:
            url = self.item(row, column).text()
            opts = {'outtmpl': '%(id)s%(ext)s'}
            with YoutubeDL(opts) as ydl:
                result = ydl.extract_info(url, download=False)
                pprint(result)

            if 'title' in result:
                self.setItem(row, self.Columns.title,
                             QTableWidgetItem(result['title']))
            if 'duration' in result:
                self.setItem(row, self.Columns.track_length,
                             QTableWidgetItem(str(result['duration'])))

            self._set_start_time_to_default(row)

    def add_track(self):
        self.insertRow(self.rowCount())

    def _set_start_time_to_default(self, row):
        self.setItem(row, self.Columns.start_time,
                     QTableWidgetItem(str(self.DEFAULT_START)))

    def _last_row_index(self):
        return self.rowCount() - 1
