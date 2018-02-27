import json
import logging
import os
import platform
import shutil
import subprocess
from collections import namedtuple
from contextlib import suppress
from decimal import Decimal
from tempfile import TemporaryDirectory

import attr
import delegator
import simplejson as json
from youtube_dl import YoutubeDL, DownloadError

from ffmpeg_normalize.__main__ import FFmpegNormalize
from power_hour_creator import config
from power_hour_creator.resources import ffmpeg_dir, ffmpeg_exe, ffprobe_exe


@attr.s
class Track:
    DEFAULT_START_TIME = 0

    url = attr.ib()
    title = attr.ib()
    length = attr.ib()
    full_song = attr.ib(default=False)
    _start_time = attr.ib(convert=Decimal, default=DEFAULT_START_TIME)

    @property
    def start_time(self):
        return round(self._start_time, 3)

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

    @classmethod
    def from_dict(cls, d):
        return cls(
            url=d['url'],
            title=d['title'],
            length=d['length'],
            full_song=d['full_song'],
            start_time=d['_start_time']
        )


def find_track(url):
    downloader = build_media_downloader(url)
    service = FindMediaDescriptionService(url, downloader=downloader)
    return service.execute()


def build_media_downloader(url, options=None):
    return LocalMediaHandler() if os.path.exists(url) else RemoteMediaDownloader(options)


class LocalMediaHandler:
    def extract_info(self, path):
        info = MediaFile.read_info(path)
        return {
            'webpage_url': path,
            'title': os.path.split(path)[1],
            'duration': divmod(float(info['format']['duration']), 1)[0]
        }

    def download(self, media_file, **_):
        shutil.copyfile(media_file.track_url, media_file.download_path)


class RemoteMediaDownloader:
    def __init__(self, options=None, remote_service_cls=YoutubeDL):
        self._options = options
        self._remote_service_cls = remote_service_cls
        self._logger = logging.getLogger(__name__)

    def extract_info(self, url):
        return self._remote_service_cls().extract_info(url, download=False)

    def download(self, media_file, progress_listener):
        self._build_remote_service(media_file, progress_listener) \
            .download([media_file.track_url])

    def _build_remote_service(self, media_file, progress_listener):
        shared_opts = {
            'ffmpeg_location': ffmpeg_dir(),
            'verbose': True,
            'outtmpl': os.path.splitext(media_file.download_path)[0] + '.%(ext)s',
            '_logger': self._logger,
            'progress_hooks': [progress_listener.on_download_progress],
        }
        if media_file.is_video:
            more_opts = {
                'format': '({})[height<=720]'.format(config.VIDEO_FORMAT),
            }
        else:
            more_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': config.AUDIO_FORMAT,
                    'preferredquality': '192'
                }],
            }

        return self._remote_service_cls({**shared_opts, **more_opts})


class FindMediaDescriptionService:
    def __init__(self, url, downloader):
        self._url = url
        self._downloader = downloader

    def execute(self):
        self.ensure_url_is_valid()
        return self.download_video_description()

    def download_video_description(self):
        result = self._downloader.extract_info(self._url)
        return Track.from_ydl(result)

    def ensure_url_is_valid(self):
        if not self.url_is_present():
            raise ValueError('URL is missing or blank')

    def url_is_present(self):
        return self._url and self._url.strip()


class PowerHour:
    def __init__(self, tracks, name, path=None, is_video=None):
        self.tracks = tracks
        self.name = name
        self.path = path
        self.is_video = is_video

    @classmethod
    def from_import(cls, tracklist):
        return cls(
            name=tracklist['name'],
            tracks=[Track.from_dict(d) for d in tracklist['tracks']]
        )


class MediaFile:
    def __init__(self, track, position, directory, is_video):
        self.track = track
        self._position = position
        self.directory = directory
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
    def download_path(self):
        return os.path.join(self.directory, '{:05d}.{}'.format(self._position + 1, self.extension))

    @property
    def normalized_path(self):
        dir, filepath  = os.path.split(self.output_path)
        return os.path.join(dir, 'normalized-{}'.format(filepath))

    @property
    def track_title(self):
        return self.track.title

    @property
    def extension(self):
        return config.VIDEO_FORMAT if self.is_video else config.AUDIO_FORMAT

    @property
    def should_be_shortened(self):
        return not self.track.full_song

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


class ServiceCancelled(Exception):
    pass


class CreatePowerHourService:
    def __init__(self, power_hour, progress_listener):
        self._power_hour = power_hour
        self._progress_listener = progress_listener

        self._logger = logging.getLogger(__name__)
        self._creation_was_cancelled = False
        self.did_error = False

    def execute(self):
        with TemporaryDirectory() as temporary_dir:
            self._export_power_hour(download_dir=temporary_dir)

    def cancel(self):
        self._creation_was_cancelled = True

    def _export_power_hour(self, download_dir):
        processor = self._build_media_processor(download_dir)
        media_files = list(self._media_files_in_power_hour(download_dir))

        try:
            self._download_and_prepare_each_file(media_files, processor)
            self._normalize_audio(media_files)
            self._merge_files_into_power_hour(media_files, processor)

        except subprocess.CalledProcessError as e:
            self._handle_exception(
                f'Error in process: {e.cmd}\nOutput: {e.output}\nError code: {e.returncode}'
            )
        except FileNotFoundError as e:
            self._handle_exception(str(e))
        except DownloadError as e:
            self._handle_exception(f'Error occurred while downloading media file: {e}')
        except ServiceCancelled:
            self._handle_cancellation()

    def _build_media_processor(self, download_dir):
        if self._power_hour.is_video:
            return VideoProcessor(
                download_dir=download_dir,
                progress_listener=self._progress_listener,
            )
        else:
            return AudioProcessor(
                download_dir=download_dir,
                progress_listener=self._progress_listener,
            )

    def _media_files_in_power_hour(self, download_dir):
        for index, track in enumerate(self._power_hour.tracks):
            yield MediaFile(
                track=track,
                position=index,
                directory=download_dir,
                is_video=self._power_hour.is_video
            )

    def _download_and_prepare_each_file(self, media_files, processor):
        for media_file in media_files:
            self._download_media_file(media_file)
            self._process_media_file(media_file, processor)
        self._progress_listener.on_all_media_downloaded()

    def _download_media_file(self, media_file):
        self._cancellation_checkpoint()
        self._progress_listener.on_new_track_downloading(
            download_number=media_file._position,
            track=media_file.track
        )

        downloader = build_media_downloader(media_file.track_url)
        downloader.download(
            media_file=media_file,
            progress_listener=self._progress_listener
        )

    def _process_media_file(self, media_file, processor):
        self._cancellation_checkpoint()
        processor.process_file(media_file)

    def _normalize_audio(self, media_files):
        self._cancellation_checkpoint()
        normalize_audio(media_files)

    def _merge_files_into_power_hour(self, media_files, processor):
        self._cancellation_checkpoint()
        output_paths = [f.output_path for f in media_files]
        processor.merge_files_into_power_hour(output_paths, self._power_hour.path)

    def _cancellation_checkpoint(self):
        if self._creation_was_cancelled:
            raise ServiceCancelled

    def _handle_cancellation(self):
        self._logger.info(f'Cancelled exporting power hour "{self._power_hour.name}"')
        with suppress(FileNotFoundError):
            os.remove(self._power_hour.path)

    def _handle_exception(self, message):
        self._logger.exception('Exception occurred during power hour creation')
        self.did_error = True
        self._progress_listener.on_service_error(message)


class MediaProcessor:
    def __init__(self, download_dir, progress_listener):
        self._download_dir = download_dir
        self._progress_listener = progress_listener
        self._logger = logging.getLogger(__name__)

    def process_file(self, media_file):
        raise NotImplementedError


class AudioProcessor(MediaProcessor):

    def process_file(self, media_file):
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

        self._logger.info('Merging into power hour with command: {}'.format(" ".join(cmd)))

        if platform.system() == 'Windows':
            process = delegator.run(cmd)
        else:
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def _shorten_to_one_minute(self, media_file):
        cmd = [
            ffmpeg_exe(),
            '-y',
            '-ss', str(media_file.track_start_time),
            '-t', '{}'.format(config.track_length),
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

    def process_file(self, media_file):
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
            '-t', '{}'.format(config.track_length),
            '-i', media_file.download_path,
            '-codec', 'copy',
            media_file.output_path
        ]

        self._logger.debug('Shortening {} to 1 minute with cmd: {}'.format(media_file.track_title, ' '.join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def _move_file_to_output_path(self, media_file):
        shutil.copyfile(media_file.download_path, media_file.output_path)


def normalize_audio(media_files):
    build_audio_normalizer(output_paths=[f.output_path for f in media_files]).run()

    for media_file in media_files:
        shutil.copyfile(src=media_file.normalized_path, dst=media_file.output_path)


def build_audio_normalizer(output_paths):
    args = {
        # map has no len, so we have to make it a list
        # http://stackoverflow.com/questions/21572840/map-object-has-no-len-in-python-3-3
        '<input-file>': output_paths,
        '--acodec': 'aac',
        '--debug': False,
        '--dir': False,
        '--dry-run': False,
        '--ebu': False,
        '--extra-options': '-b:a 192k -ar 44100',
        '--force': True,
        '--format': 'wav',
        '--level': '-26',
        '--max': False,
        '--merge': True,
        '--no-prefix': False,
        '--prefix': 'normalized',
        '--threshold': '0.5',
        '--verbose': False,
    }

    return FFmpegNormalize(args)


def export_power_hour_to_json(json_file, power_hour):
    json.dump(
        obj=serialize_to_dict(power_hour),
        fp=json_file,
        use_decimal=True,
        indent=4 * ' '
    )


def serialize_to_dict(power_hour):
    return {
        'name': power_hour.name,
        'tracks': [attr.asdict(t) for t in power_hour.tracks]
    }


def get_tracklist_from_file(import_path):
    with open(import_path, 'r') as f:
        return json.load(fp=f, use_decimal=True)
