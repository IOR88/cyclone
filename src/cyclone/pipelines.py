# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from cyclone.models import connect
from cyclone.items import ForecastTrackItem, CycloneItem, ForecastItem
from cyclone.models import CycloneModel, ForecastModel, TrackModel, ResearchGeographicalArea
import logging

logger = logging.getLogger(__name__)


def get_model_dict(model):
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns)


def create_or_update(session, data, imodel):
    s = get_model_dict(imodel)
    del s['id']
    query = session.query(imodel.__class__).filter_by(**s)
    item = query.first()
    if item:
        logger.log(logging.INFO, 'Item not updated')
    else:
        session.add(imodel)


def add_default(session, item, model):
    data = dict(item.get('item'))
    imodel = model(**data)
    create_or_update(session, data, imodel)
    return imodel


def add_forecast_model(session, item, model):
    data = dict(item.get('item'))
    imodel = model()
    imodel.research_geographical_area = session.query(ResearchGeographicalArea)\
        .filter_by(short_name=data.get('research_geographical_area')).one().id
    imodel.cyclone = session.query(CycloneModel).filter_by(name=data.get('cyclone')).one().id
    imodel.type = data.get('type')
    imodel.synoptic_time = data.get('synoptic_time')
    create_or_update(session, data, imodel)


def add_forecast_track_model(session, item, model):
    data = item.get('item')
    imodel = model(**data)
    imodel.forecast = session.query(ForecastModel).join(CycloneModel, ResearchGeographicalArea).filter_by(**item.get('forecast')).one().id
    create_or_update(session, data, imodel)


MAP = {
    CycloneItem.__name__: {'model': CycloneModel, 'add': add_default},
    ForecastItem.__name__: {'model': ForecastModel, 'add': add_forecast_model},
    ForecastTrackItem.__name__: {'model': TrackModel, 'add': add_forecast_track_model}
}


class CyclonePipeline:
    def __init__(self):
        self._engine = None
        self.session = None

    def open_spider(self, spider):
        self._engine = connect()
        Session = sessionmaker(bind=self._engine)
        self.session = Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        scenario = MAP.get(item.get('item').__class__.__name__)
        imodel = None
        try:
            imodel = scenario['add'](self.session, item, scenario['model'])
            self.session.commit()
        except (IntegrityError, InvalidRequestError,) as err:
            logger.log(logging.WARN, err)
            self.session.rollback()
        # else:
        #     return imodel
