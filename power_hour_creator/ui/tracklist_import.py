from PyQt5.QtWidgets import QFileDialog

from power_hour_creator.config import get_persistent_settings, \
    DEFAULT_TRACKLIST_DIR
from power_hour_creator.media import get_tracklist_from_file, PowerHour
from power_hour_creator.ui.helpers import store_dirname_in_settings

IMPORT_DIR_KEY = 'tracklist_import/dir'


def import_tracklist_from_file(parent_widget, phs_list_model, tracklist_model):
    import_path = get_import_path(parent_widget)

    if not import_path:
        return

    tracklist = get_tracklist_from_file(import_path)
    power_hour = PowerHour.from_import(tracklist)
    power_hour_id = phs_list_model.add_power_hour(power_hour.name)
    tracklist_model.add_tracks_to_power_hour(power_hour.tracks, power_hour_id)


@store_dirname_in_settings(key=IMPORT_DIR_KEY)
def get_import_path(parent_widget):
    path, _ = QFileDialog.getOpenFileName(
        parent_widget,
        'Import Tracklist',
        get_persistent_settings().value(IMPORT_DIR_KEY, DEFAULT_TRACKLIST_DIR),
        'Power Hour Tracklists (*.json)',
    )

    return path

