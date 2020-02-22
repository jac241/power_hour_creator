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
        anchors.margins: 5
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

        delegate: DelegateChooser {
            DelegateChoice {
                column: 0
                delegate: RowLayout {
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5
                    spacing: 5
                    Label {
                        text: "Name: "
                    }
                    TextField {
                        text: display
                        onAccepted: model.display = text
                        selectByMouse: true

                        onActiveFocusChanged: {
                            if (activeFocus) {
                                selectAll()
                            }
                        }
                    }
                }
            }
            DelegateChoice {
                column: 1
                delegate: RowLayout {
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5
                    spacing: 5
                    Label {
                        text: "Phone Number: "
                    }
                    TextField {
                        text: display
                        onAccepted: model.display = text
                        selectByMouse: true
                    }
                }
            }
        }

        ScrollHelper {
            flickable: tracklist
            anchors.fill: parent
        }
    }

}
