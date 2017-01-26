# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\power_hour_export_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PowerHourExportDialog(object):
    def setupUi(self, PowerHourExportDialog):
        PowerHourExportDialog.setObjectName("PowerHourExportDialog")
        PowerHourExportDialog.resize(400, 164)
        self.gridLayout = QtWidgets.QGridLayout(PowerHourExportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.overallProgressLabel = QtWidgets.QLabel(PowerHourExportDialog)
        self.overallProgressLabel.setObjectName("overallProgressLabel")
        self.gridLayout.addWidget(self.overallProgressLabel, 1, 0, 1, 1)
        self.overallProgressBar = QtWidgets.QProgressBar(PowerHourExportDialog)
        self.overallProgressBar.setProperty("value", 24)
        self.overallProgressBar.setObjectName("overallProgressBar")
        self.gridLayout.addWidget(self.overallProgressBar, 2, 0, 1, 1)
        self.currentSongLabel = QtWidgets.QLabel(PowerHourExportDialog)
        self.currentSongLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.currentSongLabel.setObjectName("currentSongLabel")
        self.gridLayout.addWidget(self.currentSongLabel, 3, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(PowerHourExportDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout, 7, 0, 1, 1)
        self.currentSongProgressBar = QtWidgets.QProgressBar(PowerHourExportDialog)
        self.currentSongProgressBar.setProperty("value", 24)
        self.currentSongProgressBar.setObjectName("currentSongProgressBar")
        self.gridLayout.addWidget(self.currentSongProgressBar, 4, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 0, 1, 1)

        self.retranslateUi(PowerHourExportDialog)
        QtCore.QMetaObject.connectSlotsByName(PowerHourExportDialog)

    def retranslateUi(self, PowerHourExportDialog):
        _translate = QtCore.QCoreApplication.translate
        PowerHourExportDialog.setWindowTitle(_translate("PowerHourExportDialog", "Dialog"))
        self.overallProgressLabel.setText(_translate("PowerHourExportDialog", "Overall"))
        self.currentSongLabel.setText(_translate("PowerHourExportDialog", "Current Song"))
        self.cancelButton.setText(_translate("PowerHourExportDialog", "Cancel"))

