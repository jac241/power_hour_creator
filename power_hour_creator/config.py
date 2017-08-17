import os

from appdirs import AppDirs

APP_NAME = "Power Hour Creator"
APP_AUTHOR = "jac241"
APP_DIRS = AppDirs(APP_NAME, APP_AUTHOR)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXT_DIR = os.path.abspath(os.path.join(ROOT_DIR, '../ext'))

phc_env = os.environ.get('PHC_ENV', 'production')


def db_path():
    return os.path.join(APP_DIRS.user_data_dir, '{}.db'.format(phc_env))


MIGRATIONS_PATH = os.path.join(ROOT_DIR, 'db', 'migrations')
