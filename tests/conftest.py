import pytest

from power_hour_creator import power_hour_creator
from tests.support.mocks import MockSettings


@pytest.fixture(scope="function")
def settings():
    mock_settings = MockSettings()

    yield mock_settings

    del mock_settings


@pytest.fixture(autouse=True)
def monkeypatch_settings(monkeypatch, settings):
    monkeypatch.setattr(
        target=power_hour_creator.config,
        name="get_persistent_settings",
        value=lambda: settings,
    )
