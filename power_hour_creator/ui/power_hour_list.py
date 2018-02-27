from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QListView, QMenu, QAction

DEFAULT_PR_HR_NAME = "New Power Hour"


class PowerHourModel(QSqlTableModel):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setTable('power_hours')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()

    def add_power_hour(self, name=DEFAULT_PR_HR_NAME):
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, 1), name)
        self.submitAll()
        return self.index(row, 0).data()

    def delete_power_hour(self, row):
        self.removeRow(row)
        self.submitAll()
        self.select()


class PowerHourListView(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.customContextMenuRequested.connect(self.show_context_menu)

    def select_new_power_hour(self, parent, row, column):
        self.setCurrentIndex(self._make_index(row))

    def write_settings(self, settings):
        settings.setValue('power_hour_list_view/row', self.currentIndex().row())

    def apply_settings(self, settings):
        self.setCurrentIndex(self._make_index(self._get_valid_row(settings)))

    def _get_valid_row(self, settings):
        stored_row = int(settings.value('power_hour_list_view/row', 0))
        return stored_row if stored_row < self.model().rowCount() else 0

    def _make_index(self, row):
        return self.model().index(row, 1)

    def show_context_menu(self, position):
        menu = self.build_context_menu()
        menu.popup(self.mapToGlobal(position))

    def build_context_menu(self):
        menu = QMenu(self)
        if len(self.selectedIndexes()) > 0:
            delete = QAction('&Delete', self)
            delete.triggered.connect(self._delete_power_hour)
            menu.addAction(delete)

        return menu

    def _delete_power_hour(self):
        selected_indexes = self.selectedIndexes()
        self._delete_selected_power_hours(selected_indexes)
        self._select_remaining_power_hour(selected_indexes)

    def _delete_selected_power_hours(self, selected_indexes):
        for model_index in selected_indexes:
            self.model().delete_power_hour(model_index.row())

    def _select_remaining_power_hour(self, selected_indexes):
        self.setCurrentIndex(selected_indexes[0])
        self._clear_selection_if_no_power_hours()

    def _clear_selection_if_no_power_hours(self):
        if self.model().rowCount() == 0:
            self.clearSelection()
