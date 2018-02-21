from power_hour_creator.ui import tracklist_import


class MockSettings:
    def __init__(self, settings={}):
        self._settings = settings

    def value(self, key, default=None):
        return self._settings.get(key, default)

    def setValue(self, key, value):
        self._settings[key] = value

    def contains(self, key):
        return key in self._settings


def patch_getOpenFileName(monkeypatch, returned_path):
    monkeypatch.setattr(
        target=tracklist_import.QFileDialog,
        name='getOpenFileName',
        value=lambda *args: (returned_path, '*.json')
    )