import re
import scrapy
import urllib.parse as urlparse
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
        """
        lower and join with underscore all table column names
        """
        return list(map(lambda k: k.replace(' ', '_').lower(), table.xpath('.//tr')[0].xpath('.//td/text()').getall()))

    def parse_storm_tables(self, response):
        """
        Each active cyclone site, include cyclone and ocean information, it may as well include 2 tables with BASE or
        HISTORICAL FORECASTS and associated tracks.

        Because of relationship between cyclone -> forecast -> track, we gather all the data first and only than pass it
        to pipeline. We think that this simplifies the extracted data insertion into database, we avoid synchronization
        problems. If we would pass the results actively we would not have access to primary keys.
        :param response:
        :return:
        """

        extraction_data = {'cyclone__name': None, 'items': [], 'research_geographical_area__short_name': None}
        # extract cyclone and research area information
        qp = self.__get_query_parameters(response)
        extraction_data['cyclone__name'] = qp.get('storm_identifier')[0]
        extraction_data['research_geographical_area__short_name'] = extraction_data['cyclone__name'][:2]

        for table in response.xpath('//table'):

            if table.xpath('.//td[contains(text(), "Forecast Hour")]/text()').get():
                # extract forecast information
                data = {'forecast': None, 'tracks': []}
                data['forecast'] = {'synoptic_time': int(self.pattern.search(
                    response.xpath('//h4[contains(text(), "Time of Latest Forecast")]/text()').get()).groups()[0]),
                                    'type': ForecastModel.TYPE_CHOICES[0][1]}

                keys = self.__get_table_headers(table)
                for track in table.xpath('.//tr')[1:]:
                    # extract track information
                    values = track.xpath('.//td/text()').getall()
                    data['tracks'].append({k: v for k, v in zip(keys, values)})
                extraction_data['items'].append(data)

            elif table.xpath('.//td[contains(text(), "Synoptic Time")]/text()').get():
                keys = self.__get_table_headers(table)
                for track in table.xpath('.//tr')[1:]:
                    # extract track and forecast information
                    data = {'forecast': None, 'tracks': []}
                    values = track.xpath('.//td/text()').getall()
                    item = {k: v for k, v in zip(keys, values)}

                    data['forecast'] = {'synoptic_time': int(item['synoptic_time']),
                                        'type': ForecastModel.TYPE_CHOICES[1][1]}

                    del item['synoptic_time']
                    item['forecast_hour'] = 0
                    data['tracks'].append(item)
                    extraction_data['items'].append(data)

        yield extraction_data

    def parse(self, response):
        """
        From all oceans alias research areas it extract urls to active cyclones.
        :param response:
        :return:
        """
        for href in response.css('.basin_storms').xpath('.//ul//li//a/@href').getall():
            yield scrapy.Request(response.urljoin(href), self.parse_storm_tables)
