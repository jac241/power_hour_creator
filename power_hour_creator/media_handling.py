import os
import subprocess
import sys
from tempfile import TemporaryDirectory, TemporaryFile
import logging

from furl import furl

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


class DownloadMediaService:
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
                        'preferredcodec': 'aac',
                        'preferredquality': '192'
                    }],
                }
                with YoutubeDL(opts) as ydl:
                    try:
                        output_tracks = []
                        for index, track in enumerate(self.tracks):
                            self.new_track_downloading_callback(index, track)
                            output_tracks.append(self.create_track(track, ydl, download_dir))

                        self.merge_tracks_into_power_hour(output_tracks)
                    except subprocess.CalledProcessError as e:
                        self.error_callback('Error in process: {}\nOutput: {}\nError code: {}'.format(e.cmd, e.output, e.returncode))
                    except FileNotFoundError as e:
                        self.error_callback(str(e))

    def create_track(self, track, ydl, download_dir):
        ydl.download([track.url])
        mp3file = os.path.join(download_dir, '{:05d}.aac'.format(ydl._num_downloads))
        output_file_path = self.shorten_to_one_minute(mp3file, track)
        return output_file_path

    def shorten_to_one_minute(self, mp3file, track):
        output_file_path = os.path.splitext(mp3file)[0] + '_out' + os.path.splitext(mp3file)[1]

        cmd = [
            ffmpeg_exe(),
           '-y',
           '-ss', str(track.start_time),
           '-t', '60',
           '-i', mp3file,
           '-acodec', 'aac',
           '-ar', '44100',
           '-b:a', '192k',
           output_file_path
        ]

        self.logger.debug('Shortening {} to 1 minute with cmd: {}'.format(track.title, ' '.join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        return output_file_path

    def merge_tracks_into_power_hour(self, output_tracks):
        cmd = [
            ffmpeg_exe(),
            '-y',
            '-i', "concat:{}".format("|".join(output_tracks)),
            '-acodec', 'aac',
            '-b:a', '192k',
            '-ar', '44100',
            self.power_hour_path
        ]
        self.logger.info('Merging into power hour with command: {}'.format(cmd))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)


@attr.s
class Track:
    url = attr.ib()
    title = attr.ib()
    length = attr.ib(convert=str)
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
    # _ensure_url_is_present(_url)
    # result = _downloader.extract_info(_url, download=False)
    # return Track.from_ydl(result)


def _ensure_url_is_present(url):
    if _is_blank(url):
        raise ValueError


def _is_blank(s):
    return not (s and s.strip())
