import os
import platform

from PyQt5.QtCore import QSettings
from appdirs import AppDirs

APP_NAME = "Power Hour Creator"
APP_AUTHOR = "jac241"
APP_DIRS = AppDirs(APP_NAME, APP_AUTHOR)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXT_DIR = os.path.abspath(os.path.join(ROOT_DIR, '../ext'))

AUDIO_FORMAT = 'm4a'
VIDEO_FORMAT = 'mp4'

phc_env = os.environ.get('PHC_ENV', 'production')

MIGRATIONS_PATH = os.path.join(ROOT_DIR, 'db', 'migrations')
track_length = 60

OS = platform.system().lower()


def db_path():
    return os.path.join(APP_DIRS.user_data_dir, '{}.db'.format(phc_env))


def persistent_settings():
    return QSettings(APP_AUTHOR, APP_NAME)
