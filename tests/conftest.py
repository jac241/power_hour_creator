import pytest

from power_hour_creator import power_hour_creator
from tests.ui.test_power_hour_list import MockSettings


@pytest.fixture(autouse=True)
def monkeypatch_settings(monkeypatch):
    monkeypatch.setattr(
        target=power_hour_creator.config,
        name='persistent_settings',
        value=lambda: MockSettings()
    )


