from unittest import TestCase

from PyQt5.QtWidgets import QApplication


class QtTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.qapp = QApplication([])

    def tearDown(self):
        self.qapp.quit()
