from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, joinedload

from power_hour_creator import config
from power_hour_creator.power_hour_creator import main


def naive_singularize(base, local_cls, referred_cls, constraint):
    return referred_cls.__name__.lower()[0:-1]


engine = create_engine(f'sqlite:///{config.db_path()}', echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True, name_for_scalar_relationship=naive_singularize)

PowerHour = Base.classes.power_hours
Track = Base.classes.tracks


Session = sessionmaker(bind=engine)
s = Session()
r = s.query(Track).count()
print(r)

power_hour = s.query(PowerHour).first()
tracks = s.query(Track).filter(PowerHour.id == power_hour.id).options(joinedload(Track.power_hour))

new_ph = PowerHour(name='time')
s.add(new_ph)

for index in range(60):
    new_track = Track(
        url='',
        title='',
        length='',
        start_time=0,
        full_song=False,
        position=index,
        power_hour=new_ph
    )
    s.add(new_track)

s.commit()
