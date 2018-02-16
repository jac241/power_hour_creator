from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QListView

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


class PowerHourListView(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)

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
