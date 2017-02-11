import os
import glob

from power_hour_creator import power_hour_creator, definitions
from PyQt5.QtTest import QTest


def before_scenario(context, scenario):
    power_hour_creator.launch_app()
    context.main_window = power_hour_creator.main_window
    context.app = power_hour_creator.app
    context.support_path = os.path.join(definitions.ROOT_DIR, "../tests/support")

def after_scenario(context, scenario):
    delete_export_files(context)


def delete_export_files(context):
    export_files = glob.glob(os.path.join(context.support_path, "exports/*.mp3"))
    for f in export_files:
        os.remove(f)
