from unittest import TestCase

from PyQt5.QtWidgets import QApplication

from power_hour_creator.media import PowerHour
from power_hour_creator.ui.creation import CreatePowerHourDialog
from tests.ui.support import QtTestCase


class TestExportPowerHourDialog(QtTestCase):

    def setUp(self):
        super().setUp()

        self.power_hour_name = 'MyPowerHour'
        self.power_hour = PowerHour(
            tracks=[],
            path='~',
            is_video=True,
            name=self.power_hour_name
        )

        self.uut = CreatePowerHourDialog(
            parent=None,
            power_hour=self.power_hour
        )

    def test_init_should_set_title_from_power_hour(self):
        self.assertEqual(
            self.uut.windowTitle(),
            "Exporting: {}".format(self.power_hour_name))
