import os
from decimal import Decimal

import simplejson as json

import power_hour_creator.ui.tracklist_export
from power_hour_creator.ui.power_hour_list import DEFAULT_PR_HR_NAME
from tests.config import SUPPORT_PATH
from tests.features.models import get_local_video
from tests.support.mocks import patch_getOpenFileName

import_path = os.path.join(SUPPORT_PATH, 'tester.json')
export_path = os.path.join(SUPPORT_PATH, 'exports', 'test.json')


def test_exporting_power_hour_creates_json_file(
        main_window_component,
        tracklist_component,
        monkeypatch):

    monkeypatch.setattr(
        target=power_hour_creator.ui.tracklist_export,
        name='get_save_file_name',
        value=lambda *args, **kwargs: export_path
    )

    tracklist_component.add_track(get_local_video(), full_song=True)
    tracklist_component.set_track_start_time(1, 15.45)
    main_window_component.export_power_hour(export_path)

    with open(export_path, 'r') as f:
        ph_json = json.load(f, use_decimal=True)

    track = tracklist_component.tracks[0]

    assert ph_json == {
        'name': DEFAULT_PR_HR_NAME,
        'tracks': [{
            'url': track.url,
            'title': 'cc_roller_coaster.mp4',
            'length': 32,
            'full_song': 1,
            '_start_time': Decimal(15.45),
        }]
    }


def test_importing_power_hour_creates_a_power_hour(
        main_window_component,
        phs_list_component,
        tracklist_component,
        monkeypatch):

    patch_getOpenFileName(monkeypatch, import_path)

    main_window_component.import_power_hour(import_path)
    assert 'Tester' in phs_list_component.power_hour_names
    assert len(tracklist_component.tracks) == 3


def test_should_be_able_to_insert_then_delete_tracks_after_import(
        tracklist_component,
        main_window_component,
        monkeypatch
    ):

    patch_getOpenFileName(monkeypatch, import_path)
    main_window_component.import_power_hour(import_path)

    tracklist_component.add_track_below(row=2)
    assert tracklist_component.row_count == 4

    tracklist_component.delete_track(row=2)
    assert tracklist_component.row_count == 3


def test_create_ph_button_should_be_enabled_after_import(
        main_window_component,
        monkeypatch):
    patch_getOpenFileName(monkeypatch, import_path)

    main_window_component.import_power_hour(import_path)

    assert main_window_component.create_ph_button_enabled
