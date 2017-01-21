from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from youtube_dl import YoutubeDL
from pprint import pprint
from furl import furl
from collections import namedtuple


class Tracklist(QTableWidget):

    class Columns:
        url = 0
        title = 1
        track_length = 2
        start_time = 3

    DEFAULT_START_TIME = 30

    Track = namedtuple('Track', 'url start_time')

    def __init__(self, parent):
        super().__init__(parent)
        self._setup_signals()

    def add_track(self):
        self.insertRow(self.rowCount())

    @property
    def tracks(self):
        tracks = []
        for row in range(self.rowCount()):
            url = self.item(row, self.Columns.url).text()
            start_time = self.item(row, self.Columns.start_time).text()
            if url and url.strip() and start_time:
                tracks.append(self.Track(url=url, start_time=start_time))
        return tracks

    def _setup_signals(self):
        self.cellChanged.connect(self._handle_cell_change)

    def _handle_cell_change(self, row, column):
        if column == self.Columns.url:
            url = self.item(row, column).text()
            self._update_row_with_video_info(url, row)

    def _update_row_with_video_info(self, url, row):
        try:
            result = FindVideoDescriptionService(url).execute()

            if 'title' in result:
                self.setItem(row, self.Columns.title,
                             QTableWidgetItem(str(result['title'])))
            if 'duration' in result:
                self.setItem(row, self.Columns.track_length,
                             QTableWidgetItem(str(result['duration'])))

            self._set_start_time_to_default(row)

        except MissingURL:
            pass
        except InvalidURL:
            pass

    def _set_start_time_to_default(self, row):
        self.setItem(row, self.Columns.start_time,
                     QTableWidgetItem(str(self.DEFAULT_START_TIME)))

    def _last_row_index(self):
        return self.rowCount() - 1


class InvalidURL(Exception):
    pass


class MissingURL(Exception):
    pass


class FindVideoDescriptionService:
    VALID_HOSTS = ['youtube.com', 'www.youtube.com']

    def __init__(self, url):
        self.url = url
        self.invalid_url_callable = None

    def execute(self):
        self.ensure_url_is_valid()
        return self.get_video_description()

    def get_video_description(self):
        opts = {'outtmpl': '%(id)s%(ext)s'}
        with YoutubeDL(opts) as ydl:
            result = ydl.extract_info(self.url, download=False)
            return result

    def ensure_url_is_valid(self):
        if not self.url_is_present():
            raise MissingURL()
        if not self.url_is_valid():
            raise InvalidURL()

    def url_is_present(self):
        return self.url and self.url.strip()

    def url_is_valid(self):
        return furl(self.url).host in self.VALID_HOSTS
