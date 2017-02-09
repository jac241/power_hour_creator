import os

from power_hour_creator import power_hour_creator, definitions
from PyQt5.QtTest import QTest


def before_all(context):
    power_hour_creator.launch_app()
    context.main_window = power_hour_creator.main_window
    context.app = power_hour_creator.app
    context.support_path = os.path.join(definitions.ROOT_DIR, "../tests/support")
