import unittest
from cyclone.pipelines import CyclonePipeline
from cyclone.models import CycloneModel, ForecastModel, TrackModel


class CycloneSpiderGetTableHeadersUnitTest(unittest.TestCase):

    def test_ok_default(self):
        item = {
            'cyclone__name': 'test', 'research_geographical_area__short_name': 'WP',
            'items': [{'forecast': {'synoptic_time': 201904041200, 'type': 0},
                       'tracks': [{'forecast_hour': 0, 'latitude': 0, 'longitude': 0, 'intensity': 0}]}]
        }
        pipeline = CyclonePipeline()
        pipeline.open_spider(None)
        pipeline.process_item(item, None)

        pipeline.session.query(CycloneModel).filter_by(
            name=item['cyclone__name']).one()

        pipeline.session.query(ForecastModel).filter_by(**item['items'][0]['forecast']).one()

        pipeline.session.query(TrackModel).filter_by(**item['items'][0]['tracks'][0]).one()

        pipeline.close_spider(None)

    def test_fail_cyclone_data_missing(self):
        item = {
            'cyclone__name': None, 'research_geographical_area__short_name': 'WP',
            'items': [{'forecast': {'synoptic_time': 201904041200, 'type': 0},
                       'tracks': [{'forecast_hour': 0, 'latitude': 0, 'longitude': 0, 'intensity': 0}]}]
        }
        pipeline = CyclonePipeline()
        pipeline.open_spider(None)
        self.assertRaises(AssertionError, pipeline.process_item, item, None)

        pipeline.close_spider(None)

    def test_fail_research_geographical_area_data_missing(self):
        item = {
            'cyclone__name': 'test', 'research_geographical_area__short_name': None,
            'items': [{'forecast': {'synoptic_time': 201904041200, 'type': 0},
                       'tracks': [{'forecast_hour': 0, 'latitude': 0, 'longitude': 0, 'intensity': 0}]}]
        }
        pipeline = CyclonePipeline()
        pipeline.open_spider(None)
        self.assertRaises(AssertionError, pipeline.process_item, item, None)

        pipeline.close_spider(None)

    def test_ok_items_missing(self):
        item = {
            'cyclone__name': 'test', 'research_geographical_area__short_name': 'WP',
            'items': None
        }
        pipeline = CyclonePipeline()
        pipeline.open_spider(None)
        pipeline.process_item(item, None)

        pipeline.close_spider(None)

    def test_ok_items_forecast_and_tracks_data_missing(self):
        item = {
            'cyclone__name': 'test', 'research_geographical_area__short_name': 'WP',
            'items': [{'forecast': None, 'tracks': []}]
        }
        pipeline = CyclonePipeline()
        pipeline.open_spider(None)
        pipeline.process_item(item, None)

        pipeline.close_spider(None)
