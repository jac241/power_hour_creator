from contextlib import contextmanager

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QApplication
from decimal import Decimal
from inflection import titleize
from sqlalchemy import create_engine, Integer, Column, Text, Numeric, Boolean, \
    ForeignKey, desc, asc, func
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship

from power_hour_creator import config
from power_hour_creator.media import find_track
from power_hour_creator.ui.tracklist import Tracklist, DEFAULT_NUM_TRACKS


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(f'sqlite:///{config.db_path()}', echo=True)
Base = automap_base()


class QtModelMixin:
    def set_data(self, column_index, value):
        old_value = getattr(self, self._column_name(column_index))
        if value != old_value:
            setattr(self, self._column_name(column_index), value)
            return True
        else:
            return False

    def data(self, column_index):
        return getattr(self, self._column_name(column_index))

    def _column_name(self, column_index):
        attribute_name = self.__table__._columns.keys()[column_index]
        return attribute_name

    @classmethod
    def column_names(cls):
        return cls.__table__._columns.keys()

    @classmethod
    def column_indices(cls):
        result = {}
        for index, name in enumerate(cls.column_names()):
            result[name] = index
        return result



class PowerHour(Base):
    __tablename__ = 'power_hours'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    tracks = relationship('Track', back_populates='power_hour', cascade='all, delete-orphan')


class Track(QtModelMixin, Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
    _url = Column('url', Text, nullable=False)
    title = Column(Text, nullable=False)
    length = Column(Integer, nullable=False)
    _start_time = Column('start_time', Numeric, nullable=False)
    full_song = Column(Boolean, nullable=False, default=False)
    power_hour_id = Column(Integer, ForeignKey('power_hours.id'))
    power_hour = relationship('PowerHour', back_populates='tracks')

    @hybrid_property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

        if self._url and self._url.strip():
            info = find_track(url)
            self.title = info.title
            self.start_time = info.start_time
            self.length = info.length
        else:
            self.title = ''
            self.start_time = 0
            self.length = 0

    @hybrid_property
    def start_time(self):
        try:
            return round(Decimal(self._start_time), 3)
        except TypeError:
            return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time


Base.prepare(engine, reflect=True)

Session = sessionmaker(bind=engine)
session = Session()


class TrackRepository:
    def __init__(self, session):
        self._session = session

    def find_by_power_hour_id(self, power_hour_id):
        return self._tracks_for_power_hour(power_hour_id).all()

    def create_tracks_for_new_power_hour(self, power_hour_id):
        for position in range(0, DEFAULT_NUM_TRACKS):
            self._session.add(
                Track(
                    position=position,
                    url='',
                    title='',
                    length=0,
                    start_time=0,
                    power_hour_id=power_hour_id
                )
            )

    def find_tracks_ready_for_export(self, power_hour_id):
        return self._tracks_for_power_hour(power_hour_id) \
            .filter(Track.url != None, func.trim(Track.url) != '') \
            .all()

    def _tracks_for_power_hour(self, power_hour_id):
        return self._query \
            .filter_by(power_hour_id=power_hour_id) \
            .order_by(asc(Track.position))

    @property
    def _query(self):
        return self._session.query(Track)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class TracklistModel(QAbstractTableModel):
    error_downloading = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_power_hour_id = None
        self._cache = []

    @property
    def current_power_hour_id(self):
        return self._current_power_hour_id

    @current_power_hour_id.setter
    def current_power_hour_id(self, power_hour_id):
        self.beginResetModel()
        self._current_power_hour_id = power_hour_id
        self._warm_cache()
        self.endResetModel()

    def show_tracks_for_power_hour(self, power_hour_id):
        self.current_power_hour_id = power_hour_id

    def _warm_cache(self):
        with session_scope() as s:
            repo = TrackRepository(session=s)
            self._cache = list(repo.find_by_power_hour_id(self.current_power_hour_id))
            s.expunge_all()

    def setData(self, index, value, role=None):
        if not self._is_index_valid(index):
            return False

        with session_scope() as s:
            track = self._cache[index.row()]

            data_changed = track.set_data(column_index=index.column(), value=value)

            if data_changed:
                s.merge(track)
                self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), self.columnCount()))

        return True

    def _is_index_valid(self, index):
        if index.row() < 0 or index.row() >= self.rowCount() or not index.isValid():
            return False
        else:
            return True

    def data(self, index, role=Qt.DisplayRole):
        if not self._is_index_valid(index):
            return

        if role == Qt.DisplayRole or role == Qt.EditRole:
            track = self._cache[index.row()]
            return track.data(index.column())
        else:
            return

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._cache)

    def columnCount(self, parent=QModelIndex(), **kwargs):
        return len(Track.column_names())

    def is_valid_for_export(self):
        def start_time_present_if_url(track):
            return (not track.url) or (track.url and track.start_time != '')

        return (
            self.current_power_hour_id is not None and
            bool(self._cache) and
            any(t.url for t in self._cache) and
            all(start_time_present_if_url(t) for t in self._cache)
        )

    def add_tracks_to_new_power_hour(self, power_hour_id):
        self.beginInsertRows(QModelIndex(), 0, DEFAULT_NUM_TRACKS - 1)
        with session_scope() as s:
            repo = TrackRepository(session=s)
            repo.create_tracks_for_new_power_hour(power_hour_id)

        self.endInsertRows()

    @property
    def tracks(self):
        with session_scope() as s:
            repo = TrackRepository(session=s)
            tracks = repo.find_tracks_ready_for_export(self.current_power_hour_id)
            s.expunge_all()

        return tracks

    def headerData(self, pos, orientation, role=None):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Vertical:
            return str(pos + 1)

        return titleize(str(Track.column_names()[pos]))



# app = QApplication([])
# power_hour = session.query(PowerHour).order_by('-id').first()
#
# tracklist_model = TracklistModel(None, track_repo=TrackRepository(session))
# tracklist_model.current_power_hour_id = power_hour.id
#
# view = Tracklist(None)
# view.setModel(tracklist_model)
#
# view.show()
# app.exec_()
#
# t = power_hour.tracks[0]
