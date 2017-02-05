import logging
import os
import sys

from power_hour_creator import config


def ensure_log_folder_exists():
    os.makedirs(config.app_dirs.user_log_dir, exist_ok=True)


def setup_logging():
    ensure_log_folder_exists()
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=os.path.join(config.app_dirs.user_log_dir, "power_hour_creator.log"),
                        filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def bootstrap_app():
    setup_logging()

