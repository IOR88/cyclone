import re
import scrapy
import urllib.parse as urlparse
from collections import namedtuple
from cyclone.items import ForecastTrackItem, CycloneItem, ForecastItem
from cyclone.models import ForecastModel


class CycloneSpider(scrapy.Spider):
    name = "cyclone_spider"

    start_urls = [
        'http://rammb.cira.colostate.edu/products/tc_realtime/index.asp'
    ]

    def __init__(self, *args, **kwargs):
        super(CycloneSpider, self).__init__(*args, **kwargs)
        self.pattern = re.compile('(?:\w*:\s*)(\d*)')

    def __get_query_parameters(self, response):
        parsed = urlparse.urlparse(response.request.url)
        return urlparse.parse_qs(parsed.query)

    def __get_table_headers(self, table):
        return list(map(lambda k: k.replace(' ', '_').lower(), table.xpath('.//tr')[0].xpath('.//td/text()').getall()))

    def parse_storm_tables(self, response):
        # extract cyclone information
        qp = self.__get_query_parameters(response)
        cyclone = CycloneItem(name=qp.get('storm_identifier')[0])
        yield cyclone

        # extract information needed by forecast
        fdefaults = namedtuple('ForecastDefaults',
                               'research_geographical_area cyclone synoptic_time type')(**{
            'research_geographical_area': cyclone.get('name')[:2],
            'cyclone': cyclone.get('name'),
            'synoptic_time': None,
            'type': None
        })
        for table in response.xpath('//table'):

            if table.xpath('.//td[contains(text(), "Forecast Hour")]/text()').get():
                # extract forecast information
                forecast = ForecastItem(**fdefaults._asdict())
                forecast['synoptic_time'] = int(self.pattern.search(
                    response.xpath('//h4[contains(text(), "Time of Latest Forecast")]/text()').get()).groups()[0])
                forecast['type'] = ForecastModel.TYPE_CHOICES[0][1]
                yield forecast

                keys = self.__get_table_headers(table)
                for track in table.xpath('.//tr')[1:]:
                    # extract track information
                    values = track.xpath('.//td/text()').getall()
                    yield {'track': ForecastTrackItem(**{k: v for k, v in zip(keys, values)}), 'forecast': forecast}

            elif table.xpath('.//td[contains(text(), "Synoptic Time")]/text()').get():
                keys = self.__get_table_headers(table)
                for track in table.xpath('.//tr')[1:]:
                    # extract track and forecast information
                    values = track.xpath('.//td/text()').getall()
                    item = {k: v for k, v in zip(keys, values)}

                    forecast = ForecastItem(**fdefaults._asdict())
                    forecast['synoptic_time'] = int(item['synoptic_time'])
                    forecast['type'] = ForecastModel.TYPE_CHOICES[1][1]
                    yield forecast

                    del item['synoptic_time']
                    yield {'track': ForecastTrackItem(**item), 'forecast': forecast}

    def parse(self, response):
        for href in response.css('.basin_storms').xpath('.//ul//li//a/@href').getall():
            # yield scrapy.Request(response.urljoin(href), self.parse_storm_tables)
            yield scrapy.Request(
                'http://rammb.cira.colostate.edu/products/tc_realtime/storm.asp?storm_identifier=WP012019',
                self.parse_storm_tables)
