import os
import subprocess
import sys
from tempfile import TemporaryDirectory
import logging

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
    return resource_path(os.path.join(EXT_DIR, 'ffmpeg-3.2.2-win64-static/bin'))


def ffmpeg_exe():
    return os.path.join(ffmpeg_dir(), 'ffmpeg')


TRACK_LENGTH = 60


class MediaFile:
    def __init__(self, track, download_path):
        self.track = track
        self.download_path = download_path

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


class CreatePowerHourService:
    def __init__(self, tracks, power_hour_path, new_track_downloading_callback, download_progress_callback,
                 error_callback):
        self.tracks = tracks
        self.power_hour_path = power_hour_path
        self.new_track_downloading_callback = new_track_downloading_callback
        self.download_progress_callback = download_progress_callback
        self.error_callback = error_callback
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
                    'progress_hooks': [self.download_progress_callback],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'm4a',
                        'preferredquality': '192'
                    }],
                }
                with YoutubeDL(opts) as ydl:
                    try:
                        output_tracks = []
                        for index, track in enumerate(self.tracks):
                            self.new_track_downloading_callback(index, track)
                            output_tracks.append(self.create_track(track, ydl, download_dir))

                        self.merge_tracks_into_power_hour(output_tracks, download_dir)
                    except subprocess.CalledProcessError as e:
                        self.error_callback('Error in process: {}\nOutput: {}\nError code: {}'.format(e.cmd, e.output, e.returncode))
                    except FileNotFoundError as e:
                        self.error_callback(str(e))

    def create_track(self, track, ydl, download_dir):
        ydl.download([track.url])

        media_file = MediaFile(
            track=track,
            download_path=os.path.join(download_dir, '{:05d}.m4a'.format(ydl._num_downloads))
        )

        if media_file.should_be_shortened:
            self.shorten_to_one_minute(media_file)
        else:
            self.ensure_output_is_m4a(media_file)

        return media_file.output_path

    def shorten_to_one_minute(self, media_file):
        cmd = [
            ffmpeg_exe(),
           '-y',
           '-ss', str(media_file.track_start_time),
           '-t', '{}'.format(TRACK_LENGTH),
           '-i', media_file.download_path,
           '-acodec', 'aac',
           '-ar', '44100',
           '-b:a', '192k',
           media_file.output_path
        ]

        self.logger.debug('Shortening {} to 1 minute with cmd: {}'.format(media_file.track_title, ' '.join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def merge_tracks_into_power_hour(self, output_tracks, download_dir):
        concat_directive_path = os.path.join(download_dir, "concat_input.txt")
        self._write_output_track_list_to_file(output_tracks, concat_directive_path)

        cmd = [
            ffmpeg_exe(),
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_directive_path,
            '-c', 'copy',
            self.power_hour_path
        ]
        self.logger.info('Merging into power hour with command: {}'.format(" ".join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def ensure_output_is_m4a(self, media_file):
        cmd = [
            ffmpeg_exe(),
            '-y',
            '-i', media_file.download_path,
            '-acodec', 'aac',
            '-ar', '44100',
            '-b:a', '192k',
            media_file.output_path
        ]

        self.logger.debug('Converting {} to m4a with command {}'.format(media_file.track_title, ' '.join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def _write_output_track_list_to_file(self, output_tracks, concat_directive_path):
        with open(concat_directive_path, 'w') as f:
            for track_path in output_tracks:
                f.write("file '{}'{}".format(track_path, os.linesep))


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
