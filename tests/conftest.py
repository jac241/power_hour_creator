import pytest

from power_hour_creator import power_hour_creator
from tests.support.mocks import MockSettings


@pytest.fixture(autouse=True)
def monkeypatch_settings(monkeypatch):
    monkeypatch.setattr(
        target=power_hour_creator.config,
        name='get_persistent_settings',
        value=lambda: MockSettings()
    )


