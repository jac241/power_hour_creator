import os
from PyQt5.QtWidgets import QFileDialog

from power_hour_creator.media import get_tracklist_from_file, PowerHour


def import_tracklist_from_file(parent_widget, phs_list_model, tracklist_model):
    import_path, _ = get_import_path(parent_widget)

    if not import_path:
        return

    tracklist = get_tracklist_from_file(import_path)
    power_hour = PowerHour.from_import(tracklist)
    power_hour_id = phs_list_model.add_power_hour(power_hour.name)
    tracklist_model.add_tracks_to_power_hour(power_hour.tracks, power_hour_id)

def get_import_path(parent_widget):
    return QFileDialog.getOpenFileName(
        parent_widget,
        'Import Tracklist',
        os.path.expanduser('~/Documents'),
        'Power Hour Tracklists (*.json)',
    )

