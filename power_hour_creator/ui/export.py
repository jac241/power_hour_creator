import os

import simplejson as json
from PyQt5.QtWidgets import QFileDialog

from power_hour_creator.media import as_tracklist_dict


def export_tracklist(parent_widget, power_hour):
    export_path, _ = get_tracklist_export_path(parent_widget=parent_widget)

    if not export_path:
        return

    with open(export_path, 'w') as json_file:
        json.dump(
            obj=as_tracklist_dict(power_hour),
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
