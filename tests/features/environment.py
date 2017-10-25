import glob
import os
import sys
from contextlib import suppress

from PyQt5.QtSql import QSqlQuery
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import power_hour_creator.config
from power_hour_creator import power_hour_creator, config, boot
from power_hour_creator.boot import bootstrap_app_environment
from power_hour_creator.ui.main_window import build_main_window
from tests.config import SUPPORT_PATH
from tests.features.models import TracklistTestModel


def before_all(context):
    config.phc_env = 'test'
    delete_database()


def after_step(context, step):
    QTest.qWait(5)


def before_scenario(context, scenario):
    config.phc_env = 'test'
    config.track_length = 5

    launch_app(context)
    context.support_path = SUPPORT_PATH
    context.num_tracks = 0
    context.prhr_length = 0
    context.tracklist_test_model = TracklistTestModel(context.main_window.tracklist)
    QTest.qWaitForWindowActive(context.main_window)


def after_scenario(context, scenario):
    close_app(context)
    delete_export_files()
    clean_database()


def launch_app(context):
    app = QApplication(sys.argv)
    bootstrap_app_environment()
    context.main_window = build_main_window(app)
    context.tracklist = context.main_window.tracklist
    context.app = app
    context.main_window.show()


def close_app(context):
    del context.app


def delete_export_files():
    for ext in [config.AUDIO_FORMAT, config.VIDEO_FORMAT, 'json']:
        export_files = glob.glob(
            os.path.join(
                SUPPORT_PATH,
                "exports/*.{}".format(ext)
            )
        )
        for f in export_files:
            os.remove(f)


def clean_database():
    try:
        db = boot.connect_to_db()
        query = QSqlQuery()
        query.exec_("DELETE FROM tracks")
        query.exec_("DELETE FROM power_hours")
        query.exec_("DELETE FROM migrations")
    finally:
        db.close()


def delete_database():
    if 'test' in config.db_path():
        with suppress(OSError):
            os.remove(config.db_path())


