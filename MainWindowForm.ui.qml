import QtQuick 2.4
import QtQuick.Controls 2.3
import QtQuick.Controls 1.4 as Q1

Item {
    width: 400
    height: 400

    Q1.SplitView {
        id: splitView
        anchors.fill: parent

        ListView {
            model: 20

        }
    }
}
