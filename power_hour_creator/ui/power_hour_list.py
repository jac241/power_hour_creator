from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QListView

DEFAULT_PR_HR_NAME = "New Power Hour"


class PowerHourModel(QSqlTableModel):
    def add_power_hour(self):
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, 1), DEFAULT_PR_HR_NAME)
        self.submitAll()
        return self.index(row, 0).data()


class PowerHourListView(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)

    def select_new_power_hour(self, parent, row, column):
        self.setCurrentIndex(self.model().index(row, 1))
