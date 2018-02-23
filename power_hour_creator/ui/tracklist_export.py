from PyQt5.QtWidgets import QFileDialog

from power_hour_creator.config import get_persistent_settings, \
    DEFAULT_TRACKLIST_DIR
from power_hour_creator.media import export_power_hour_to_json
from power_hour_creator.ui.helpers import store_dirname_in_settings

EXPORT_DIR_KEY = 'tracklist_export/dir'


def export_tracklist_to_file(parent_widget, power_hour):
    export_path = get_tracklist_export_path(parent_widget=parent_widget)

    if not export_path:
        return

    with open(export_path, 'w') as json_file:
        export_power_hour_to_json(json_file, power_hour)


@store_dirname_in_settings(key=EXPORT_DIR_KEY)
def get_tracklist_export_path(parent_widget):
    path, _ = QFileDialog.getSaveFileName(
        parent_widget,
        'Export Tracklist',
        get_persistent_settings().value(EXPORT_DIR_KEY, DEFAULT_TRACKLIST_DIR),
        'Power Hour Tracklists (*.json)',
    )

    return path
