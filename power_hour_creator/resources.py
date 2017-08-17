import os
from os.path import join, abspath
import sys
import platform

from power_hour_creator.config import EXT_DIR


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, relative_path)

    return join(abspath("."), relative_path)


def image_path(relative_path):
    return join(resource_path(join('assets', 'images')), relative_path)


def ffmpeg_dir():
    return resource_path(os.path.join(EXT_DIR, platform_dir(), 'bin'))


def platform_dir():
    options = {
        'Windows': 'ffmpeg-3.2.2-win32-static',
        'Darwin': 'mac'
    }
    return options.get(platform.system())


def ffmpeg_exe():
    return os.path.join(ffmpeg_dir(), 'ffmpeg')


def ffprobe_exe():
    return os.path.join(ffmpeg_dir(), 'ffprobe')
