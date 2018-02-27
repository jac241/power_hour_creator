from PyQt5.QtSql import QSqlQuery


def test_application_should_enable_foreign_keys_on_start_up(main_window):
    q = QSqlQuery('PRAGMA foreign_keys')
    if not q.exec_():
        raise RuntimeError

    q.next()
    assert q.value(0)
