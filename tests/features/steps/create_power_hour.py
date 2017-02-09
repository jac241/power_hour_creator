from behave import *
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QPoint
from unittest.mock import Mock
import os
from should_dsl import should
from power_hour_creator.ui.power_hour_creator_window import ExportPowerHourDialog

use_step_matcher("re")


track_url = 'https://soundcloud.com/fsoe-excelsior/sodality-floe-running'


@when("I add a track to a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    tracklist = context.main_window.tracklist
    url_cell_pos = (tracklist.rowViewportPosition(1), tracklist.columnViewportPosition(1))
    viewport = tracklist.viewport()
    QTest.mouseClick(viewport, Qt.LeftButton, pos=QPoint(url_cell_pos[0], url_cell_pos[1]))
    QTest.mouseDClick(viewport, Qt.LeftButton, pos=QPoint(url_cell_pos[0], url_cell_pos[1]))
    QTest.keyClicks(viewport.focusWidget(), track_url)
    QTest.keyClick(viewport.focusWidget(), Qt.Key_Return)


@step("I create a power hour")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    context.export_path = os.path.join(context.support_path, 'exports/test.mp3')

    context.main_window.get_export_path = Mock()
    context.main_window.get_export_path.return_value = context.export_path

    QTest.mouseClick(context.main_window.createPowerHourButton, Qt.LeftButton)


@then("that power hour should have been created")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    def export_dialog_visible():
        export_dialog = next((w for w in context.app.topLevelWidgets() if type(w) is ExportPowerHourDialog), None)
        return export_dialog.isVisible()

    while export_dialog_visible():
        QTest.qWait(100)

    assert(os.path.exists(context.export_path))

