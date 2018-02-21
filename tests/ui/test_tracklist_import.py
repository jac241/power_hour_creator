import os

from power_hour_creator import config
from power_hour_creator.config import get_persistent_settings
from power_hour_creator.ui.tracklist_import import IMPORT_DIR_KEY, \
    get_import_path
from tests.support.mocks import patch_getOpenFileName


def test_get_import_path_should_store_path_in_settings(monkeypatch):
    expected_path = os.path.join(config.DEFAULT_IMPORT_DIR, 'fake')
    import_path = os.path.join(expected_path, 'path.json')
    patch_getOpenFileName(monkeypatch, import_path)

    get_import_path(parent_widget=None)

    assert get_persistent_settings().value(IMPORT_DIR_KEY) == expected_path


