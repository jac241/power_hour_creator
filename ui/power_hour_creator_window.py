from .forms.mainwindow import Ui_mainWindow
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QFileDialog
import os
from youtube_dl import YoutubeDL
import sys
import subprocess
from pydub import AudioSegment
from tempfile import TemporaryDirectory


class PowerHourCreatorWindow(QMainWindow, Ui_mainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._setup_grid_appearance()
        self._connect_add_track_button()
        self._connect_create_power_hour_button()

    def _setup_grid_appearance(self):
        self.tracklist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _connect_add_track_button(self):
        self.addTrackButton.clicked.connect(self.tracklist.add_track)

    def _connect_create_power_hour_button(self):
        self.createPowerHourButton.clicked.connect(self._export_power_hour)

    def _export_power_hour(self):
        file_name = QFileDialog.getSaveFileName(self, "Export Power Hour",
                                                os.path.expanduser('~/Music'),
                                                "Audio (*.mp3)")[0]
        if not file_name.lower().endswith('.mp3'):
            file_name += '.mp3'

        if file_name:
            DownloadVideosService(self.tracklist.tracks, file_name).execute()


class DownloadVideosService:
    def __init__(self, tracks, power_hour_path, download_dir=TemporaryDirectory()):
        self.tracks = tracks
        self.power_hour_path = power_hour_path
        self.download_dir = download_dir

    def execute(self):
            opts = {
                # 'postprocessor_args': ['-ss {}'.format(str(track.start_time)),
                #                        '-t 60'],
                # 'audio_format': 'mp3',
                'ffmpeg_location': self._ffmpeg_location,
                'verbose': True,
                'outtmpl': os.path.join(self.download_dir.name, '%(autonumber)s.%(ext)s'),
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            }
            with YoutubeDL(opts) as ydl:
                output_tracks = []
                for track in self.tracks:
                    output_tracks.append(self.create_track(track, ydl))

                self.merge_tracks_into_power_hour(output_tracks)

    def create_track(self, track, ydl):
        ydl.download([track.url])
        mp3file = os.path.join(self.download_dir.name, '{:05d}.mp3'.format(ydl._num_downloads))
        # ffmpeg -ss 30 -t 70 -i inputfile.mp3 -acodec copy outputfile.mp3
        output_file_path = self.shorten_to_one_minute(mp3file, track)
        return output_file_path

    def shorten_to_one_minute(self, mp3file, track):
        output_file_path = os.path.splitext(mp3file)[0] + '_out' + os.path.splitext(mp3file)[1]
        cmd = [self._ffmpeg_location,
               '-y',
               '-ss', str(track.start_time),
               '-t', '59',
               '-i', mp3file,
               '-acodec', 'copy',
               output_file_path]
        print(' '.join(cmd))
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        return output_file_path

    def merge_tracks_into_power_hour(self, output_tracks):
        AudioSegment.converter = self._ffmpeg_location
        power_hour = AudioSegment.empty()
        for file in output_tracks:
            audio_data = AudioSegment.from_mp3(file)
            power_hour += audio_data
        print(self.power_hour_path)
        power_hour.export(self.power_hour_path)

    @property
    def _ffmpeg_location(self):
        return os.path.normpath(os.path.join(os.path.dirname(sys.modules['__main__'].__file__),
                            "ext", "ffmpeg-3.2.2-win64-static", "bin", "ffmpeg.exe"))
