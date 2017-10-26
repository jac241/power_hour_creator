import os

import simplejson as json
from PyQt5.QtWidgets import QFileDialog

from power_hour_creator.media import serialize_to_dict


def export_tracklist(parent_widget, power_hour):
    export_path, _ = get_tracklist_export_path(parent_widget=parent_widget)

    if not export_path:
        return

    with open(export_path, 'w') as json_file:
        export_power_hour_to_json(json_file, power_hour)


def export_power_hour_to_json(json_file, power_hour):
    json.dump(
        obj=serialize_to_dict(power_hour),
        fp=json_file,
        use_decimal=True,
        indent=4 * ' '
    )


def get_tracklist_export_path(parent_widget):
    return QFileDialog.getSaveFileName(
        parent_widget,
        'Export Tracklist',
        os.path.expanduser('~/Documents'),
        'Power Hour Tracklists (*.json)',
    )
