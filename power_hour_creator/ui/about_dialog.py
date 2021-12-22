from PyQt5.QtWidgets import QDialog

from power_hour_creator.ui.forms.aboutdialog import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        # Set up the user interface from Designer.
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        self.setWindowTitle("About Power Hour Creator")
        self.ui.textBrowser.setOpenExternalLinks(True)
