# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\power_hour_export_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PowerHourExportDialog(object):
    def setupUi(self, PowerHourExportDialog):
        PowerHourExportDialog.setObjectName("PowerHourExportDialog")
        PowerHourExportDialog.resize(326, 156)
        self.gridLayout = QtWidgets.QGridLayout(PowerHourExportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(PowerHourExportDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout, 8, 0, 1, 1)
        self.exportProgressLayout = QtWidgets.QVBoxLayout()
        self.exportProgressLayout.setObjectName("exportProgressLayout")
        self.overallProgressLabel = QtWidgets.QLabel(PowerHourExportDialog)
        self.overallProgressLabel.setObjectName("overallProgressLabel")
        self.exportProgressLayout.addWidget(self.overallProgressLabel)
        self.overallProgressBar = QtWidgets.QProgressBar(PowerHourExportDialog)
        self.overallProgressBar.setProperty("value", 0)
        self.overallProgressBar.setObjectName("overallProgressBar")
        self.exportProgressLayout.addWidget(self.overallProgressBar)
        self.currentSongLabel = QtWidgets.QLabel(PowerHourExportDialog)
        self.currentSongLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.currentSongLabel.setObjectName("currentSongLabel")
        self.exportProgressLayout.addWidget(self.currentSongLabel)
        self.currentSongProgressBar = QtWidgets.QProgressBar(PowerHourExportDialog)
        self.currentSongProgressBar.setProperty("value", 0)
        self.currentSongProgressBar.setObjectName("currentSongProgressBar")
        self.exportProgressLayout.addWidget(self.currentSongProgressBar)
        self.cancellingLabel = QtWidgets.QLabel(PowerHourExportDialog)
        self.cancellingLabel.setObjectName("cancellingLabel")
        self.exportProgressLayout.addWidget(self.cancellingLabel)
        self.gridLayout.addLayout(self.exportProgressLayout, 1, 0, 1, 1)

        self.retranslateUi(PowerHourExportDialog)
        QtCore.QMetaObject.connectSlotsByName(PowerHourExportDialog)

    def retranslateUi(self, PowerHourExportDialog):
        _translate = QtCore.QCoreApplication.translate
        PowerHourExportDialog.setWindowTitle(_translate("PowerHourExportDialog", "Dialog"))
        self.cancelButton.setText(_translate("PowerHourExportDialog", "Cancel"))
        self.overallProgressLabel.setText(_translate("PowerHourExportDialog", "Overall"))
        self.currentSongLabel.setText(_translate("PowerHourExportDialog", "Downloading:"))
        self.cancellingLabel.setText(_translate("PowerHourExportDialog", "Cancelling..."))

