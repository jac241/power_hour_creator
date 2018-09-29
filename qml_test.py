import sys
from PyQt5.QtCore import QCoreApplication, Qt, QUrl
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlEngine, QQmlApplicationEngine, QQmlComponent
from PyQt5.QtWidgets import QApplication


def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(QUrl('main.qml'))
    win = engine.rootObjects()[0]
    win.show()
    sys.exit(app.exec_())


main()
