import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.3
import Qt.labs.qmlmodels 1.0

Rectangle {
    Pane {
        anchors.fill: parent
        focusPolicy: Qt.ClickFocus
    }

//    MouseArea {
//        anchors.fill: parent
//        onClicked: forceActiveFocus()
//    }

    TableView {
        id: tracklist
        anchors.fill: parent
        columnSpacing: 1
        rowSpacing: 1
        clip: true
        boundsBehavior: Flickable.StopAtBounds


        model: TableModel {
            TableModelColumn { display: "name" }
            TableModelColumn { display: "number" }

            rows: [
                {
                    "name": "Bill Smith",
                    "number": "4125235801"
                },
                {
                    "name": "Jimmy Smith",
                    "number": "4125235801"
                },
                {
                    "name": "d Smith",
                    "number": "4125235801"
                },
                {
                    "name": "e Smith",
                    "number": "4125235801"
                },
                {
                    "name": "f Smith",
                    "number": "4125235801"
                },
                {
                    "name": "h Smith",
                    "number": "4125235801"
                },
                {
                    "name": "i Smith",
                    "number": "4125235801"
                },
                {
                    "name": "j Smith",
                    "number": "4125235801"
                },
                {
                    "name": "k Smith",
                    "number": "4125235801"
                },
                {
                    "name": "l Smith",
                    "number": "4125235801"
                },
                {
                    "name": "m Smith",
                    "number": "4125235801"
                },
                {
                    "name": "n Smith",
                    "number": "4125235801"
                },
                {
                    "name": "o Smith",
                    "number": "4125235801"
                },
            ]
        }

        delegate: Rectangle {
            implicitHeight: 50
            implicitWidth: 100
            border.width: 1
            MouseArea {
                anchors.fill: parent
                onClicked: forceActiveFocus()
            }

            TextInput {
                padding: 3
                text: display
                selectByMouse: true
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.IBeamCursor
                    acceptedButtons: Qt.NoButton
                }
            }
        }

        ScrollHelper {
            flickable: tracklist
            anchors.fill: parent
        }
    }

}
