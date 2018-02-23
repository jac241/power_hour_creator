import os

from power_hour_creator import config
from power_hour_creator.config import get_persistent_settings
from power_hour_creator.ui import tracklist_export
from power_hour_creator.ui.tracklist_export import get_tracklist_export_path, \
    EXPORT_DIR_KEY


def test_get_tracklist_export_path_should_store_path_in_settings(monkeypatch):
    expected_path = os.path.join(config.DEFAULT_TRACKLIST_DIR, 'fake')
    export_path = os.path.join(expected_path, 'path.json')
    monkeypatch.setattr(
        target=tracklist_export.QFileDialog,
        name='getSaveFileName',
        value=lambda *args: (export_path, '*.json')
    )
    get_tracklist_export_path(parent_widget=None)

    assert get_persistent_settings().value(EXPORT_DIR_KEY)