from power_hour_creator.ui import tracklist
from tests.features.models import local_videos


def test_user_should_be_able_to_select_local_video_from_context_menu(
        monkeypatch,
        tracklist_component):
    path = local_videos[0].url
    monkeypatch.setattr(
        target=tracklist.QFileDialog,
        name='getOpenFileName',
        value=lambda *args, **kwargs: (path, 'Videos (*.mp4')
    )

    tracklist_component.add_local_song_through_context_menu()
    assert tracklist_component.tracks[0].url == path


def test_user_should_still_see_old_track_if_they_back_out_of_adding_local_file_from_menu(
        monkeypatch,
        tracklist_component):
    monkeypatch.setattr(
        target=tracklist.QFileDialog,
        name='getOpenFileName',
        value=lambda *args, **kwargs: ('', 'Videos (*.mp4')
    )
    tracklist_component.add_track()
    tracklist_component.add_local_song_through_context_menu()

    assert len(tracklist_component.tracks) == 1
