from PyQt5.QtWidgets import QListWidget, QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

app = QApplication([])
main = QMainWindow()
funList = QListWidget(main)
itemN = QtWidgets.QListWidgetItem()
# Create widget
widget = QtWidgets.QWidget()
widgetText = QtWidgets.QLabel("I love PyQt!")
widgetButton = QtWidgets.QPushButton("Push Me")
widgetLayout = QtWidgets.QHBoxLayout()
widgetLayout.addWidget(widgetText)
widgetLayout.addWidget(widgetButton)
widgetLayout.addStretch()

widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
widget.setLayout(widgetLayout)
itemN.setSizeHint(widget.sizeHint())

# Add widget to QListWidget funList
funList.addItem(itemN)
funList.setItemWidget(itemN, widget)
main.show()
app.exec_()