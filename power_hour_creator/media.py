import json
import logging
import os
import shutil
import subprocess
from collections import namedtuple
from tempfile import TemporaryDirectory

import attr
import delegator
from youtube_dl import YoutubeDL, DownloadError

from power_hour_creator.config import EXT_DIR
from power_hour_creator.resources import resource_path


def ffmpeg_dir():
    return resource_path(os.path.join(EXT_DIR, 'ffmpeg-3.2.2-win32-static/bin'))


def ffmpeg_exe():
    return os.path.join(ffmpeg_dir(), 'ffmpeg')


def ffprobe_exe():
    return os.path.join(ffmpeg_dir(), 'ffprobe')

TRACK_LENGTH = 60


class MediaFile:
    def __init__(self, track, position, directory, is_video):
        self.track = track
        self._position = position
        self._directory = directory
        self.is_video = is_video

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
    def extension(self):
        return 'mp4' if self.is_video else 'm4a'

    @property
    def should_be_shortened(self):
        return not self.track.full_song

    @property
    def download_path(self):
        return os.path.join(self._directory, '{:05d}.{}'.format(self._position + 1, self.extension))

    @property
    def info(self):
        return self.__class__.read_info(self.download_path)

    @staticmethod
    def read_info(path):
        cmd = [
            ffprobe_exe(),
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            path
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.PIPE, stdin=subprocess.PIPE).decode()
        return json.loads(output)


def get_audio_downloader(progress_listener, download_dir, logger):
    audio_opts = {
        'ffmpeg_location': ffmpeg_dir(),
        'verbose': True,
        'outtmpl': os.path.join(download_dir, '%(autonumber)s.%(ext)s'),
        'format': 'bestaudio/best',
        '_logger': logger,
        'progress_hooks': [progress_listener.on_download_progress],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192'
        }],
    }
    return YoutubeDL(audio_opts)


class CreatePowerHourService:
    def __init__(self, power_hour, progress_listener):
        self._power_hour = power_hour
        self._progress_listener = progress_listener
        self._logger = logging.getLogger(__name__)
        self._is_cancelled = False

    def execute(self):
        with TemporaryDirectory() as download_dir:
            self._logger.debug("ffmpeg location : %s", ffmpeg_dir())
            self._logger.debug("ffmpeg found: %s", os.path.exists(ffmpeg_dir()))

            processor = self._build_media_processor(download_dir)

            try:
                output_files = []
                for index, track in enumerate(self._power_hour.tracks):
                    if self._is_cancelled:
                        break

                    self._progress_listener.on_new_track_downloading(index, track)

                    media_file = MediaFile(
                        track=track,
                        position=index,
                        directory=download_dir,
                        is_video=self._power_hour.is_video
                    )

                    processor.process_file(media_file)
                    output_files.append(media_file.output_path)

                if not self._is_cancelled:
                    processor.merge_files_into_power_hour(output_files, self._power_hour.path)

                if self._is_cancelled:  # can be cancelled at any time
                    self._handle_cancellation()

            except subprocess.CalledProcessError as e:
                self._progress_listener.on_service_error(
                    'Error in process: {}\nOutput: {}\nError code: {}'.format(e.cmd, e.output, e.returncode))
            except FileNotFoundError as e:
                self._progress_listener.on_service_error(str(e))

    def _build_media_processor(self, download_dir):
        shared_opts = {
            'ffmpeg_location': ffmpeg_dir(),
            'verbose': True,
            'outtmpl': os.path.join(download_dir, '%(autonumber)s.%(ext)s'),
            '_logger': self._logger,
            'progress_hooks': [self._progress_listener.on_download_progress],
        }
        if self._power_hour.is_video:
            video_opts = {
                'format': '(mp4)[height<=720]',
            }
            return VideoProcessor(
                download_dir=download_dir,
                progress_listener=self._progress_listener,
                downloader=YoutubeDL({**shared_opts, **video_opts})
            )
        else:
            audio_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192'
                }],
            }
            return AudioProcessor(
                download_dir=download_dir,
                progress_listener=self._progress_listener,
                downloader=YoutubeDL({**shared_opts, **audio_opts})
            )

    def cancel(self):
        self._is_cancelled = True

    def _handle_cancellation(self):
        try:
            os.remove(self._power_hour.path)
        except FileNotFoundError:
            pass


class MediaProcessor:
    def __init__(self, download_dir, progress_listener, downloader):
        self._download_dir = download_dir
        self._progress_listener = progress_listener
        self._downloader = downloader
        self._logger = logging.getLogger(__name__)

    def process_file(self, media_file):
        self._downloader.download([media_file.track_url])
        self.after_download(media_file)

    def after_download(self, media_file):
        raise NotImplementedError


class AudioProcessor(MediaProcessor):

    def after_download(self, media_file):
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
            '-nostdin',
            power_hour_path
        ]
        pass
        self._logger.info('Merging into power hour with command: {}'.format(" ".join(cmd)))
        p = delegator.run(cmd)

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
            '-nostdin',
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


class VideoProcessor(MediaProcessor):

    def after_download(self, media_file):
        self._prepare_files_for_merge(media_file)

    def merge_files_into_power_hour(self, output_files, power_hour_path):
        scale_string = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1:1'
        filter_strings = []

        for index in range(len(output_files)):
            filter_strings.append('[{}:v]{}[v{}];'.format(index, scale_string, index))

        for index in range(len(output_files)):
            filter_strings.append('[v{}][{}:a:0]'.format(index, index))

        filter_complex = '{} concat=n={}:v=1:a=1 [v] [a]'.format(' '.join(filter_strings), len(output_files))

        input_directives = []
        for file in output_files:
            input_directives.append('-i')
            input_directives.append(file)

        cmd = [
            ffmpeg_exe(),
            *input_directives,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '[a]',
            '-y',
            '-acodec', 'aac',
            '-vcodec', 'libx264',
            '-s', '1280x720',
            '-r', '30',
            '-preset', 'faster',
            '-nostdin',
            power_hour_path
        ]

        self._logger.debug('Combining videos into power hour with cmd: {}'.format(' '.join(cmd)))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        self._log_process_output(p)

        self._logger.debug('Done')

    def _prepare_files_for_merge(self, media_file):
        if media_file.should_be_shortened:
            self._shorten_to_one_minute(media_file)
            self._move_file_back_to_download_path(media_file)

        self._move_file_to_output_path(media_file)

    def _frame_rate_and_resolution_are_correct(self, media_file):
        info = self._video_stream_info(media_file)
        return info['height'] == 720 and info['width'] == 1280

    def _video_stream_info(self, media_file):
        return media_file.info['streams'][0]

    def _convert_video_to_correct_attributes(self, media_file):
        cmd = [
            ffmpeg_exe(),
            '-i', media_file.download_path,
            '-y',
            '-acodec', 'aac',
            '-vcodec', 'libx264',
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
            '-r', '30',
            '-preset', 'faster',
            '-nostdin',
            media_file.output_path
        ]

        self._logger.debug('Resizing and correcting video {} with command: {}'.format(media_file.track_title, ' '.join(cmd)))
        # subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        self._log_process_output(p)

        self._logger.debug('Done')

    def _log_process_output(self, p):
        while True:
            line = p.stdout.readline().decode().strip()
            self._logger.debug(line),
            if line == '' and p.poll() is not None:
                break

    def _move_file_back_to_download_path(self, media_file):
        shutil.copyfile(media_file.output_path, media_file.download_path)

    def _shorten_to_one_minute(self, media_file):
        cmd = [
            ffmpeg_exe(),
            '-y',
            '-ss', str(media_file.track_start_time),
            '-t', '{}'.format(TRACK_LENGTH),
            '-i', media_file.download_path,
            '-codec', 'copy',
            media_file.output_path
        ]

        self._logger.debug('Shortening {} to 1 minute with cmd: {}'.format(media_file.track_title, ' '.join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def _move_file_to_output_path(self, media_file):
        shutil.copyfile(media_file.download_path, media_file.output_path)


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

    @classmethod
    def from_record(cls, record):
        return cls(
            url=record.value("url"),
            title=record.value("title"),
            length=record.value("length"),
            full_song=record.value("full_song"),
            start_time=record.value("start_time")
        )


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


PowerHour = namedtuple('PowerHour', 'tracks path is_video')