import QtQuick 2.10
import QtQuick.Controls 1.4 as QtQc1
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("Power Hour Creator")

    QtQc1.SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal

        ListView {
            Layout.minimumWidth: 200
            model: 4
            delegate: ItemDelegate {
            text: "Power Hour " + (index + 1)
            }
        }

        ListView {
            model: 60
            interactive: false
            delegate: ItemDelegate {
                text: "Track " + (index + 1)
            }
        }
    }
}
