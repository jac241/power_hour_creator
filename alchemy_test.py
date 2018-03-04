from contextlib import contextmanager

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtWidgets import QApplication
from sqlalchemy import create_engine, Integer, Column, Text, Numeric, Boolean, ForeignKey, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, joinedload, relationship

from power_hour_creator import config
from power_hour_creator.media import find_track
from power_hour_creator.power_hour_creator import main
from power_hour_creator.ui.tracklist import Tracklist


def naive_singularize(base, local_cls, referred_cls, constraint):
    return referred_cls.__name__.lower()[0:-1]


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
    start_time = Column(Numeric, nullable=False)
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


Base.prepare(engine, reflect=True)

# Session = sessionmaker(bind=engine, expire_on_commit=False)
Session = sessionmaker(bind=engine)
session = Session()
r = session.query(Track).count()
print(r)

power_hour = session.query(PowerHour).order_by('-id').first()
for track in power_hour.tracks:
    print(track.url)


class TrackRepository:
    def __init__(self, session):
        self._session = session

    def find_by_power_hour_id(self, power_hour_id):
        return self._session.query(Track).filter_by(power_hour_id=power_hour_id).all()

    def commit(self):
        self._session.commit()

    def update(self, id, **kwargs):
        t = self._session.query(Track).filter_by(id=id).one()
        for key in kwargs.keys():
            setattr(t, key, kwargs[key])
        self._session.flush()


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
    def __init__(self, parent, track_repo):
        super().__init__(parent)
        self._current_power_hour_id = None
        self._cache = []
        self.repo = track_repo

    @property
    def current_power_hour_id(self):
        return self._current_power_hour_id

    @current_power_hour_id.setter
    def current_power_hour_id(self, power_hour_id):
        self.beginResetModel()
        self._current_power_hour_id = power_hour_id
        self._warm_cache()
        self.endResetModel()

    def _warm_cache(self):
        with session_scope() as s:
            repo = TrackRepository(session=s)
            self._cache = list(repo.find_by_power_hour_id(self._current_power_hour_id))
            s.expunge_all()

    def setData(self, index, value, role=None):
        if not self._is_index_valid(index):
            return False

        with session_scope() as s:
            track = self._cache[index.row()]

            data_changed = track.set_data(column_index=index.column(), value=value)

            if data_changed:
                session.merge(track)
                session.commit()
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
        return len(Track.__table__._columns.keys())


app = QApplication([])
tracklist_model = TracklistModel(None, track_repo=TrackRepository(session))
tracklist_model.current_power_hour_id = power_hour.id

view = Tracklist(None)
view.setModel(tracklist_model)

view.show()
app.exec_()
# new_url = 'https://www.youtube.com/watch?v=_e8xy7kpNPQ'
# url = tracklist.data(tracklist.index(0, 2))
# tracklist.setData(tracklist.index(0, 2), new_url)
# assert tracklist.data(tracklist.index(0, 2)) == new_url


t = power_hour.tracks[0]
