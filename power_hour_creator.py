import logging
import sys

from PyQt5 import QtWidgets, QtCore

from ui.power_hour_creator_window import PowerHourCreatorWindow
from boot import bootstrap_app


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger()
    logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)

sys.excepthook = handle_exception


if __name__ == "__main__":
    bootstrap_app()

    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    mainWindow = PowerHourCreatorWindow()
    mainWindow.show()

    sys.exit(app.exec_())
