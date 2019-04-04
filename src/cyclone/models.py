from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, UniqueConstraint, BigInteger
from sqlalchemy.orm import sessionmaker
from cyclone import settings


Base = declarative_base()


class ResearchGeographicalArea(Base):
    """
    We have choose a research geographical area to represent oceans as it seems more accurate because
    ocean may be divided into sub areas.
    """
    __tablename__ = 'research_geographical_area'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), unique=True, nullable=False)
    short_name = Column('short_name', String(50), unique=True, nullable=False)


class ForecastCenterModel(Base):
    __tablename__ = 'forecast_center'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), unique=True, nullable=False)
    short_name = Column('short_name', String(50), unique=True, nullable=False)


class CycloneModel(Base):
    __tablename__ = 'cyclone'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), unique=True, nullable=False)


class ForecastModel(Base):
    """
    Uniqueness of forecast is guaranteed by ocean alias research geographical area, cyclone, synoptic time and type.
    Based on http://rammb.cira.colostate.edu/products/tc_realtime/about.asp information forecast may be of 2 types
    historical and base.
    """

    TYPE_CHOICES = (
        ('BASIC', 0),
        ('HISTORICAL', 1)
    )
    __tablename__ = 'forecast'
    __table_args__ = (
        UniqueConstraint('research_geographical_area', 'cyclone', 'synoptic_time', 'type', name='_forecast_unique'),
    )

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    research_geographical_area = Column('research_geographical_area', ForeignKey('research_geographical_area.id'), nullable=False)
    forecast_center = Column('forecast_center', ForeignKey('forecast_center.id'), nullable=True)
    cyclone = Column('cyclone', ForeignKey('cyclone.id'), nullable=False)
    synoptic_time = Column('synoptic_time', BigInteger, nullable=False)
    type = Column('type', Integer, nullable=False)


class TrackModel(Base):
    """
    By default all tracks related to forecast of type 1(HISTORICAL) will have forecast hour 0. This is because historical
    tracks are produced from forecast center warnings and are most accurate when the warning is issued.
    """

    __tablename__ = 'track'
    __table_args__ = (
        UniqueConstraint('forecast', 'hour', name='_track_unique'),
    )

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    forecast = Column('forecast', ForeignKey('forecast.id'), nullable=False)
    forecast_hour = Column('hour', Integer, nullable=False)
    latitude = Column('latitude', Float, nullable=False)
    longitude = Column('longitude', Float, nullable=False)
    intensity = Column('intensity', Integer, nullable=False)


def connect():
    engine = create_engine(
        "postgresql+psycopg2://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
            .format(
            database_host=settings.DATABASE_HOST,
            database_port=settings.DATABASE_PORT,
            database_name=settings.DATABASE_NAME,
            database_user=settings.DATABASE_USER,
            database_password=settings.DATABASE_PASSWORD
        ))

    return engine


if __name__ == '__main__':
    engine = connect()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # load initial data

    # add research areas
    try:
        session.add_all([
            ResearchGeographicalArea(name='Atlantic', short_name='A'),
            ResearchGeographicalArea(name='Eastern Pacific', short_name='EP'),
            ResearchGeographicalArea(name='Central Pacific', short_name='CP'),
            ResearchGeographicalArea(name='Western Pacific', short_name='WP'),
            ResearchGeographicalArea(name='North Indian Ocean', short_name='IO'),
            ResearchGeographicalArea(name='Southern Hemisphere', short_name='SH')
        ])
        session.commit()
    except (IntegrityError, InvalidRequestError) as err:
        pass

    # add forecast centers
    try:
        session.add_all([
            ForecastCenterModel(name='National Hurricane Center', short_name='NHC'),
            ForecastCenterModel(name='Central Pacific Hurricane Center', short_name='CPHC'),
            ForecastCenterModel(name='Joint Typhoon Warning Center', short_name='JTWC')
        ])
        session.commit()
    except (IntegrityError, InvalidRequestError) as err:
        pass

    session.close()
