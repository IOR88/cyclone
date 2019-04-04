# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from cyclone.models import connect
from cyclone.models import CycloneModel, ForecastModel, TrackModel, ResearchGeographicalArea
import logging

logger = logging.getLogger(__name__)


def insert_data(session, model, data):
    query = session.query(model).filter_by(**data)
    obj = query.first()
    if not obj:
        obj = model(**data)
        try:
            session.add(obj)
        except (Exception,) as err:
            logger.log(logging.WARN, 'Session rollback reason:{err}'.format(err=err))
            session.rollback()
            obj = None
    return obj


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
        cyclone = insert_data(self.session, CycloneModel, {'name': item.get('cyclone__name')})
        self.session.commit()
        r_geo_area = self.session.query(ResearchGeographicalArea).filter_by(short_name=item.get('research_geographical_area__short_name')).one()

        for items in item.get('items'):
            forecast = insert_data(self.session, ForecastModel,
                                   {**items.get('forecast'), 'cyclone': cyclone.id, 'research_geographical_area': r_geo_area.id})
            self.session.commit()
            for track in items.get('tracks'):
                insert_data(self.session, TrackModel,
                            {**track, 'forecast': forecast.id})
                self.session.commit()
        return item
