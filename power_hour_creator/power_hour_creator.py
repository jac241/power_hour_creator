import logging
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QCoreApplication

from power_hour_creator import config
from power_hour_creator.ui.main_window import build_main_window
from .boot import bootstrap_app_environment


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger()
    logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)

sys.excepthook = handle_exception


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    bootstrap_app_environment()

    logger = logging.getLogger(__name__)
    logger.info("Launching GUI")
    logger.info("Showing main window")

    main_window = build_main_window(app)
    main_window.show_with_last_full_screen_setting()

    sys.exit(app.exec_())

