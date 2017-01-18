import sys

from PyQt5 import QtWidgets

from ui.power_hour_creator_window import PowerHourCreatorWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainWindow = PowerHourCreatorWindow()
    mainWindow.show()

    sys.exit(app.exec_())
