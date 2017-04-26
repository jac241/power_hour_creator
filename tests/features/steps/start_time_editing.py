from PyQt5.QtCore import Qt

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QLineEdit
from behave import *
from hamcrest import *

from power_hour_creator.ui.tracklist import DisplayTime

use_step_matcher("re")


@then("I should see the start time in the correct format")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    tracklist = context.main_window.tracklist
    columns = tracklist.Columns
    start_time_column = tracklist.model().Columns.start_time

    delegate = tracklist.itemDelegate()
    editor = QLineEdit()
    delegate.setEditorData(editor, tracklist.model().index(1, start_time_column))

    start_time_text = editor.text()
    assert_that(start_time_text, is_("00:30"))
