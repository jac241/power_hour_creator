from os.path import join, abspath
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, relative_path)

    return join(abspath("."), relative_path)

def image_path(relative_path):
    return join(resource_path(join('assets', 'images')), relative_path)
