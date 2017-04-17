from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QListView

DEFAULT_PR_HR_NAME = "New Power Hour"


class PowerHourListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        model = QSqlTableModel(self, QSqlDatabase.database())
        model.setTable('power_hours')
        model.setEditStrategy(QSqlTableModel.OnFieldChange)
        model.select()

        self.setModel(model)
        self.setModelColumn(1)

    def add_power_hour(self):
        model = self.model()
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 1), DEFAULT_PR_HR_NAME)
        model.submitAll()
        self.setCurrentIndex(model.index(row, 1))

