import os
import subprocess
import sys
from tempfile import TemporaryDirectory
import logging
import shutil

from youtube_dl import YoutubeDL
from youtube_dl.YoutubeDL import DownloadError

import attr

from power_hour_creator.config import EXT_DIR


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)


def ffmpeg_dir():
    return resource_path(os.path.join(EXT_DIR, 'ffmpeg-3.2.2-win32-static/bin'))


def ffmpeg_exe():
    return os.path.join(ffmpeg_dir(), 'ffmpeg')


TRACK_LENGTH = 60


class MediaFile:
    def __init__(self, track, position, directory):
        self.track = track
        self._position = position
        self._directory = directory

    @property
    def track_url(self):
        return self.track.url

    @property
    def track_start_time(self):
        return self.track.start_time

    @property
    def output_path(self):
        return os.path.splitext(self.download_path)[0] + '_out' + os.path.splitext(self.download_path)[1]

    @property
    def track_title(self):
        return self.track.title

    @property
    def should_be_shortened(self):
        return not self.track.full_song

    @property
    def download_path(self):
        return os.path.join(self._directory, '{:05d}.m4a'.format(self._position + 1))


def get_audio_downloader(progress_listener, download_dir, logger):
    audio_opts = {
        'ffmpeg_location': ffmpeg_dir(),
        'verbose': True,
        'outtmpl': os.path.join(download_dir, '%(autonumber)s.%(ext)s'),
        'format': 'bestaudio/best',
        'logger': logger,
        'progress_hooks': [progress_listener.on_download_progress],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192'
        }],
    }
    return YoutubeDL(audio_opts)


class AudioProcessor:
    def __init__(self, download_dir, progress_listener, downloader):
        self._download_dir = download_dir
        self._progress_listener = progress_listener
        self._logger = logging.getLogger(__name__)
        self._downloader = downloader

    def process_file(self, media_file):
        self._downloader.download([media_file.track_url])

        if media_file.should_be_shortened:
            self._shorten_to_one_minute(media_file)
        else:
            self._move_unprocessed_file_to_correct_path(media_file)

    def merge_files_into_power_hour(self, output_files, power_hour_path):
        concat_directive_path = os.path.join(self._download_dir, "concat_input.txt")
        self._write_output_track_list_to_file(output_files, concat_directive_path)

        cmd = [
            ffmpeg_exe(),
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_directive_path,
            '-c', 'copy',
            power_hour_path
        ]
        self._logger.info('Merging into power hour with command: {}'.format(" ".join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def _shorten_to_one_minute(self, media_file):
        cmd = [
            ffmpeg_exe(),
            '-y',
            '-ss', str(media_file.track_start_time),
            '-t', '{}'.format(TRACK_LENGTH),
            '-i', media_file.download_path,
            '-acodec', 'copy',
            '-ar', '44100',
            '-b:a', '192k',
            media_file.output_path
        ]

        self._logger.debug('Shortening {} to 1 minute with cmd: {}'.format(media_file.track_title, ' '.join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def _move_unprocessed_file_to_correct_path(self, media_file):
        shutil.copyfile(media_file.download_path, media_file.output_path)

    def _write_output_track_list_to_file(self, output_tracks, concat_directive_path):
        with open(concat_directive_path, 'w') as f:
            for track_path in output_tracks:
                f.write("file '{}'{}".format(track_path, os.linesep))


class CreatePowerHourService:
    def __init__(self, tracks, power_hour_path, progress_listener):
        self.tracks = tracks
        self.power_hour_path = power_hour_path
        self._progress_listener = progress_listener
        self.logger = logging.getLogger(__name__)

    def execute(self):
            with TemporaryDirectory() as download_dir:
                self.logger.debug("ffmpeg location : %s", ffmpeg_dir())
                self.logger.debug("ffmpeg found: %s", os.path.exists(ffmpeg_dir()))

                opts = {
                    'ffmpeg_location': ffmpeg_dir(),
                    'verbose': True,
                    'outtmpl': os.path.join(download_dir, '%(autonumber)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'logger': self.logger,
                    'progress_hooks': [self._progress_listener.on_download_progress],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'm4a',
                        'preferredquality': '192'
                    }],
                }
                processor = AudioProcessor(
                    download_dir=download_dir,
                    progress_listener=self._progress_listener,
                    downloader=YoutubeDL(opts))
                try:
                    output_files = []
                    for index, track in enumerate(self.tracks):
                        self._progress_listener.on_new_track_downloading(index, track)

                        media_file = MediaFile(
                            track=track,
                            position=index,
                            directory=download_dir)

                        processor.process_file(media_file)
                        output_files.append(media_file.output_path)

                    processor.merge_files_into_power_hour(output_files, self.power_hour_path)
                except subprocess.CalledProcessError as e:
                    self._progress_listener.on_service_error('Error in process: {}\nOutput: {}\nError code: {}'.format(e.cmd, e.output, e.returncode))
                except FileNotFoundError as e:
                    self._progress_listener.on_service_error(str(e))


@attr.s
class Track:
    url = attr.ib()
    title = attr.ib()
    length = attr.ib(convert=str)
    full_song = attr.ib(default=False)
    start_time = attr.ib(convert=int, default=30)

    @classmethod
    def from_ydl(cls, result):
        url = result['webpage_url']
        title = result['title']
        length = result['duration'] if 'duration' in result else ''
        return cls(url=url, title=title, length=length)


class FindMediaDescriptionService:
    def __init__(self, url, downloader):
        self._url = url
        self._downloader = downloader

    def execute(self):
        self.ensure_url_is_valid()
        return self.download_video_description()

    def download_video_description(self):
        result = self._downloader.extract_info(self._url, download=False)
        return Track.from_ydl(result)

    def ensure_url_is_valid(self):
        if not self.url_is_present():
            raise ValueError('URL is missing or blank')

    def url_is_present(self):
        return self._url and self._url.strip()


def find_track(url):
    service = FindMediaDescriptionService(url, downloader=YoutubeDL())
    return service.execute()
