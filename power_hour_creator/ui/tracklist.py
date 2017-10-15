import logging

from PyQt5.QtCore import QModelIndex, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtSql import QSqlTableModel, QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import QMenu, QAction, \
    QTableView
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QItemDelegate
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt
import re

from decimal import Decimal, InvalidOperation

from power_hour_creator.media import Track, find_track
from youtube_dl import DownloadError

DEFAULT_NUM_TRACKS = 60


class ConversionError(Exception):
    pass


class DisplayTime:
    def __init__(self, time):
        self._time = time

    def as_time_str(self):
        if self._already_a_time_str():
            return self._time

        if self._has_invalid_characters():
            return ''

        m, s = divmod(round(Decimal(self._time), 3), 60)
        s, f = divmod(s, 1)
        f_str = ('%s' % f).lstrip('0').rstrip('0') if f > 0 else ''

        return "%02d:%02d%s" % (m, s, f_str)

    def as_decimal(self):
        try:
            if self._is_a_number():
                return self._time

            if len(self._time) == 0:
                return self._time

            if self._has_invalid_characters():
                return ''

            if self._just_seconds_in_string():
                return Decimal(self._time)

            return sum(x * Decimal(t) for x, t in zip([60, 1], self._time.split(':')))
        except (InvalidOperation, TypeError) as e:
            logger = logging.getLogger(__name__)
            logger.exception('Error converting string to decimal for DisplayTime', self._time)
            raise ConversionError


    def _already_a_time_str(self):
        return ':' in str(self._time)

    def _just_seconds_in_string(self):
        return not self._already_a_time_str()

    def _has_invalid_characters(self):
        return not self._is_a_number() and re.search('[^0-9.:]', self._time)

    def _is_a_number(self):
        return type(self._time) != str


class ValidationError(ValueError):
    def __init__(self, params):
        self.params = params


class StartTimeValidator():
    def __init__(self, model_index):
        self._model_index = model_index

    def validate(self, start_time):
        if start_time.strip() == '':
            return

        self._ensure_start_time_less_than_track_length(start_time)

    def _ensure_start_time_less_than_track_length(self, start_time):
        track_length = self._model_index.sibling(
            self._model_index.row(),
            TracklistModel.Columns.length
        ).data(Qt.DisplayRole)

        try:
            if not DisplayTime(start_time).as_decimal() < track_length:
                raise ValidationError(params={
                    'code': 'start_time_too_late',
                    'start_time': start_time
                })
        except ConversionError:
            raise ValidationError(params={
                    'code': 'start_time_format_bad',
                    'start_time': start_time
                })




class TrackDelegate(QItemDelegate):
    def __init__(self, track_error_dispatcher, parent=None):
        super().__init__(parent)
        self._read_only_columns=TracklistModel.Columns.read_only
        self._time_columns=TracklistModel.Columns.time
        self._boolean_columns=TracklistModel.Columns.checkbox
        self._track_error_dispatcher = track_error_dispatcher

    def paint(self, painter, option, index):
        if self._column_is_time_column_and_has_data(index):
            seconds = index.model().data(index, Qt.DisplayRole)
            time = DisplayTime(seconds)
            value = time.as_time_str() if self._row_has_a_track(index) else ''
            self.drawDisplay(painter, option, option.rect, value)
            self.drawFocus(painter, option, option.rect)
        elif self._column_is_a_boolean_column(index):
            value = ''

            if self._row_has_a_track(index):
                value = 'Yes' if index.model().data(index, Qt.DisplayRole) else 'No'

            self.drawDisplay(painter, option, option.rect, value)
            self.drawFocus(painter, option, option.rect)
        else:
            super().paint(painter, option, index)

    def _column_is_time_column_and_has_data(self, index):
        return (self._column_is_a_time_column(index)
                and index.model().data(index, Qt.DisplayRole) is not None
                and index.model().data(index, Qt.DisplayRole) != '')

    def _column_is_a_time_column(self, index):
        return index.column() in self._time_columns

    def _column_is_a_boolean_column(self, index):
        return index.column() in self._boolean_columns

    def _row_has_a_track(self, index):
        url = index.sibling(index.row(), TracklistModel.Columns.url).data(Qt.DisplayRole)
        return url is not None and url.strip()

    def setEditorData(self, editor, index):
        if self._column_is_time_column_and_has_data(index):
            seconds = index.model().data(index, Qt.DisplayRole)
            time = DisplayTime(seconds)
            if type(editor) is QLineEdit:
                editor.setText(time.as_time_str())
        elif index.column() in self._boolean_columns:
            value = True if index.model().data(index, Qt.DisplayRole) else False
            index = editor.findData(value)
            editor.setCurrentIndex(index)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == TracklistModel.Columns.start_time:
            try:
                StartTimeValidator(index).validate(editor.text())
            except ValidationError as e:
                self._track_error_dispatcher.track_invalid.emit(e.params)
                model.setData(index, '')
                return
            model.setData(index, str(DisplayTime(editor.text()).as_decimal()))
        elif index.column() in self._boolean_columns:
            value = True if editor.itemData(editor.currentIndex()) else False
            model.setData(index, value)
        else:
            super().setModelData(editor, model, index)

    def createEditor(self, parent, option, index):
        if not self._cell_should_have_editor_now(index):
            return None
        if self._column_is_a_time_column(index):
            line_edit = QLineEdit(parent)
            reg_exp_validator = QRegExpValidator(QRegExp('[0-9.:]*'), parent)
            line_edit.setValidator(reg_exp_validator)
            line_edit.editingFinished.connect(self._commit_and_close_editor)
            return line_edit
        if self._column_is_a_boolean_column(index):
            combobox = QComboBox(parent)
            combobox.addItem('No', False)
            combobox.addItem('Yes', True)
            return combobox
        else:
            return super().createEditor(parent, option, index)

    def _cell_should_have_editor_now(self, index):
        if self._column_is_a_read_only_column(index):
            return False

        if index.column() == TracklistModel.Columns.url:
            return True

        if self._row_has_a_track(index):
            return True

    def _column_is_a_read_only_column(self, index):
        return index.column() in self._read_only_columns

    def _commit_and_close_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)


class DbError(IOError):
    pass


class TracklistModel(QSqlTableModel):

    new_power_hour_selected = pyqtSignal()
    error_downloading = pyqtSignal(str, str)

    class Columns:
        id = 0
        position = 1
        url = 2
        title = 3
        length = 4
        start_time = 5
        full_song = 6
        power_hour_id = 7
        read_only = [title, length]
        time = [length, start_time]
        checkbox = [full_song]

    def __init__(self, parent=None, db=QSqlDatabase(), *args, **kwargs):
        super().__init__(parent, db, *args, **kwargs)
        self.current_power_hour_id = None

        self.setTable("tracks")
        self.setEditStrategy(QSqlTableModel.OnFieldChange)

        self.setHeaderData(self.Columns.url, Qt.Horizontal, "URL")
        self.setHeaderData(self.Columns.title, Qt.Horizontal, "Title")
        self.setHeaderData(self.Columns.length, Qt.Horizontal, "Duration")
        self.setHeaderData(self.Columns.start_time, Qt.Horizontal, "Start Time")
        self.setHeaderData(self.Columns.full_song, Qt.Horizontal, "Full Song?")

        self.setSort(self.Columns.position, Qt.AscendingOrder)
        self.dataChanged.connect(self._load_track_info_if_new_url_given)

        self.select()

    def _load_track_info_if_new_url_given(self, top_left_index, *_):
        column = top_left_index.column()
        row = top_left_index.row()
        if column == self.Columns.url:
            url = top_left_index.data()
            self._update_row_with_video_info(url, row)

    def _update_row_with_video_info(self, url, row):
        try:
            self._show_track_details(row, find_track(url))
        except ValueError:
            self._clear_row(row)
        except DownloadError as e:
            self.error_downloading.emit(url, str(e))
            self._clear_out_invalid_url(row)

    def _show_track_details(self, row, track):
        self.submit()
        self.setData(self.index(row, self.Columns.title), track.title)
        self.setData(self.index(row, self.Columns.length), track.length)
        self.setData(self.index(row, self.Columns.start_time), str(track.start_time))
        self.submitAll()

    def _clear_row(self, row):
        self.submit()
        self.setData(self.index(row, self.Columns.title), '')
        self.setData(self.index(row, self.Columns.length), 0)
        self.setData(self.index(row, self.Columns.start_time), 0)
        self.setData(self.index(row, self.Columns.full_song), 0)
        self.submitAll()

    def _clear_out_invalid_url(self, row):
        self.setData(self.index(row, self.Columns.url), '')

    @property
    def tracks(self):
        model = self._tracks_query_model()

        tracks = []
        for record in map(lambda i: model.record(i), range(model.rowCount())):
            tracks.append(Track.from_record(record))

        return tracks

    def is_valid_for_export(self):
        if self.current_power_hour_id is not None:
            model = self._tracks_query_model()
            num = self._num_tracks_with_blank_start_times()
            return model.rowCount() and num == 0
        else:
            return False

    def _tracks_query_model(self):
        model = QSqlTableModel()
        model.setTable(self.tableName())
        q_filter = self.filter()
        q_filter += " AND " if self.filter().strip() else ''
        q_filter += "length(trim(url)) > 0"
        model.setFilter(q_filter)
        model.setSort(self.Columns.position, Qt.AscendingOrder)
        model.select()
        return model

    def _num_tracks_with_blank_start_times(self):
        query = self._blank_start_time_query()
        query.exec_()
        query.next()
        return query.value(0)

    def _blank_start_time_query(self):
        query = QSqlQuery()
        query.prepare(
            "SELECT COUNT(*) "
            "FROM tracks "
            "WHERE power_hour_id = :power_hour_id AND "
            "      url != '' AND "
            "      trim(start_time) = ''"
        )
        query.bindValue(':power_hour_id', self.current_power_hour_id)
        return query

    def add_tracks_to_new_power_hour(self, power_hour_id):
        self.beginInsertRows(QModelIndex(), 0, DEFAULT_NUM_TRACKS-1)
        self.current_power_hour_id = power_hour_id
        self.database().transaction()

        for pos in range(DEFAULT_NUM_TRACKS):
            self._rollback_and_error_if_unsuccessful(self.insertRow(pos))

        self.database().commit()
        self.endInsertRows()

    def add_track_to_end(self):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.insertRow(self.rowCount())
        self.endInsertRows()
        self.select()

    def insertRow(self, position, *args, **kwargs):
        query = QSqlQuery()

        query.prepare(
            "INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) "
            "VALUES (:position, :url, :title, :length, :start_time, :full_song, :power_hour_id)"
        )

        query.bindValue(":position", position)
        query.bindValue(":url", "")
        query.bindValue(":title", "")
        query.bindValue(":length", 0)
        query.bindValue(":start_time", 0)
        query.bindValue(":full_song", 0)
        query.bindValue(":power_hour_id", self.current_power_hour_id)

        return query.exec_()

    def show_tracks_for_power_hour(self, power_hour_id):
        self.setFilter("power_hour_id = {}".format(power_hour_id))
        self.current_power_hour_id = power_hour_id
        self.new_power_hour_selected.emit()

    def insert_row_accounting_for_existing_tracks(self, row):
        self.beginInsertRows(QModelIndex(), row, row)
        self.database().transaction()

        self._increment_position_for_rows_from(row)

        self._rollback_and_error_if_unsuccessful(self.insertRow(row))

        self.database().commit()
        self.endInsertRows()

        self.select()

    def _increment_position_for_rows_from(self, row):
        # need to use a weird query here http://stackoverflow.com/questions/7703196/sqlite-increment-unique-integer-field

        query = QSqlQuery()
        query.prepare(
            'UPDATE tracks '
            'SET position = -(position+1) '
            'WHERE position >= :position AND power_hour_id = :power_hour_id'
        )
        query.bindValue(':position', row)
        query.bindValue(':power_hour_id', self.current_power_hour_id)

        self._rollback_and_error_if_unsuccessful(query.exec_())

        query.prepare(
            'UPDATE tracks '
            'SET position = -position '
            'WHERE position < 0 AND power_hour_id = :power_hour_id'
        )
        query.bindValue(':power_hour_id', self.current_power_hour_id)

        self._rollback_and_error_if_unsuccessful(query.exec_())

    def _rollback_and_error_if_unsuccessful(self, successful):
        if not successful:
            self._handle_database_error()

    def _handle_database_error(self):
        self.database().rollback()
        raise DbError(self.database().lastError().databaseText())

    def remove_track_accounting_for_existing_tracks(self, position):
        self.beginRemoveRows(QModelIndex(), position, position)
        self.database().transaction()

        self._rollback_and_error_if_unsuccessful(self.removeRow(position))

        self._decrement_position_for_tracks_from(position)

        self.database().commit()
        self.endRemoveRows()

        self.select()

    def _sort_by_position(self):
        self.sort(self.Columns.position, Qt.AscendingOrder)

    def removeRow(self, position, *args, **kwargs):
        query = QSqlQuery()

        query.prepare(
            'DELETE FROM tracks '
            'WHERE position = :position AND power_hour_id = :power_hour_id'
        )

        query.bindValue(":position", position)
        query.bindValue(":power_hour_id", self.current_power_hour_id)

        return query.exec_()

    def _decrement_position_for_tracks_from(self, position):
        query = QSqlQuery()
        query.prepare(
            'UPDATE tracks '
            'SET position = position -1 '
            'WHERE position > :position AND power_hour_id = :power_hour_id')
        query.bindValue(':position', position)
        query.bindValue(':power_hour_id', self.current_power_hour_id)

        self._rollback_and_error_if_unsuccessful(query.exec_())


class Tracklist(QTableView):

    def __init__(self, parent):
        super().__init__(parent)
        self._setup_context_menu()

    def add_track(self):
        self.insertRow(self.rowCount())

    def _items_have_text(self, items):
        return all(i is not None and len(i.text()) > 0 for i in items)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            pass
        super().keyPressEvent(event)

    def _last_row_index(self):
        return self.rowCount() - 1

    def _setup_context_menu(self):
        self.customContextMenuRequested.connect(self._build_custom_menu)

    def _build_custom_menu(self, position):
        menu = QMenu(self)

        if self.model().rowCount() > 0:
            insert_above = QAction('Insert Track Above', self)
            insert_above.triggered.connect(self._insert_row_above)
            menu.addAction(insert_above)

            insert_below = QAction('Insert Track Below', self)
            insert_below.triggered.connect(self._insert_row_below)
            menu.addAction(insert_below)

            delete_selected = QAction('Delete Selected Tracks', self)
            delete_selected.triggered.connect(self._delete_selected_tracks)
            menu.addAction(delete_selected)

        add_track_to_end = QAction('Add Track To End', self)
        add_track_to_end.triggered.connect(self.model().add_track_to_end)
        menu.addAction(add_track_to_end)

        menu.popup(self.viewport().mapToGlobal(position))

    def _insert_row_above(self):
        selected_row = self.selectedIndexes()[0].row()
        self.model().insert_row_accounting_for_existing_tracks(selected_row)

    def _insert_row_below(self):
        last_selected_row = self.selectedIndexes()[-1].row()
        self.model().insert_row_accounting_for_existing_tracks(last_selected_row + 1)

    def _delete_selected_tracks(self):
        for index in reversed(sorted(self.selectionModel().selectedRows())):
            self.model().remove_track_accounting_for_existing_tracks(index.row())
