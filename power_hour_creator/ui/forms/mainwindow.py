# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(750, 577)
        self.centralWidget = QtWidgets.QWidget(mainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.createPowerHourButton = QtWidgets.QPushButton(self.centralWidget)
        self.createPowerHourButton.setObjectName("createPowerHourButton")
        self.gridLayout.addWidget(self.createPowerHourButton, 2, 0, 1, 1)
        self.tracklist = Tracklist(self.centralWidget)
        self.tracklist.setShowGrid(True)
        self.tracklist.setRowCount(60)
        self.tracklist.setColumnCount(4)
        self.tracklist.setObjectName("tracklist")
        item = QtWidgets.QTableWidgetItem()
        self.tracklist.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tracklist.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tracklist.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tracklist.setHorizontalHeaderItem(3, item)
        self.tracklist.horizontalHeader().setVisible(True)
        self.tracklist.horizontalHeader().setDefaultSectionSize(100)
        self.tracklist.horizontalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.tracklist, 0, 0, 1, 1)
        self.tracklistControls = QtWidgets.QHBoxLayout()
        self.tracklistControls.setObjectName("tracklistControls")
        self.addTrackButton = QtWidgets.QPushButton(self.centralWidget)
        self.addTrackButton.setObjectName("addTrackButton")
        self.tracklistControls.addWidget(self.addTrackButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.tracklistControls.addItem(spacerItem)
        self.gridLayout.addLayout(self.tracklistControls, 1, 0, 1, 1)
        mainWindow.setCentralWidget(self.centralWidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        mainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(mainWindow)
        self.statusBar.setObjectName("statusBar")
        mainWindow.setStatusBar(self.statusBar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "Power Hour Creator"))
        self.createPowerHourButton.setText(_translate("mainWindow", "Create Power Hour!"))
        item = self.tracklist.horizontalHeaderItem(0)
        item.setText(_translate("mainWindow", "URL"))
        item = self.tracklist.horizontalHeaderItem(1)
        item.setText(_translate("mainWindow", "Title"))
        item = self.tracklist.horizontalHeaderItem(2)
        item.setText(_translate("mainWindow", "Length"))
        item = self.tracklist.horizontalHeaderItem(3)
        item.setText(_translate("mainWindow", "Start Time"))
        self.addTrackButton.setText(_translate("mainWindow", "Add Track"))
        self.menuFile.setTitle(_translate("mainWindow", "File"))

from power_hour_creator.ui.tracklist import Tracklist
