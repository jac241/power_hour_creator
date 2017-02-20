import os
import glob

import power_hour_creator.config
from power_hour_creator import power_hour_creator, config
from PyQt5.QtTest import QTest


def after_step(context, step):
    QTest.qWait(5)


def before_scenario(context, scenario):
    launch_app(context)
    context.support_path = os.path.join(config.ROOT_DIR, "../tests/support")


def after_scenario(context, scenario):
    close_app(context)
    delete_export_files(context)


def launch_app(context):
    app = power_hour_creator.launch_app()
    context.main_window = app.main_window
    context.tracklist = context.main_window.tracklist
    context.app = app


def close_app(context):
    del context.app


def delete_export_files(context):
    export_files = glob.glob(os.path.join(context.support_path, "exports/*.aac"))
    for f in export_files:
        os.remove(f)
