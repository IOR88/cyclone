import re
import unittest
from cyclone.spiders.cyclone_spider import CycloneSpider
from scrapy.selector import Selector
from scrapy.http import Response, Request


class CycloneSpiderGetTableHeadersUnitTest(unittest.TestCase):

    def test_ok_default(self):
        headers = ['test_header_one', 'test_header_two']
        table = Selector(text='<table><tr><td>{0}<td><td>{1}</td><tr></table>'.format(*headers))
        results = CycloneSpider.get_table_headers(table)
        self.assertSetEqual(set(headers), set(results))

    def test_ok_empty_table(self):
        table = Selector(text='<table></table>')
        results = CycloneSpider.get_table_headers(table)
        self.assertSetEqual(set(), set(results))

    def test_ok_replacing(self):
        headers = ['Test Header One', 'Test Header Two']
        keys = ['test_header_one', 'test_header_two']
        table = Selector(text='<table><tr><td>{0}<td><td>{1}</td><tr></table>'.format(*headers))
        results = CycloneSpider.get_table_headers(table)
        self.assertSetEqual(set(keys), set(results))

    def test_ok_no_headers(self):
        table = Selector(text='<table><tr><tr></table>')
        results = CycloneSpider.get_table_headers(table)
        self.assertSetEqual(set(), set(results))

    def test_ok_no_headers_values(self):
        table = Selector(text='<table><tr><td></td><td></td><tr></table>')
        results = CycloneSpider.get_table_headers(table)
        self.assertSetEqual(set(), set(results))

    def test_ok_duplicate_values(self):
        headers = ['test_header_one', 'test_header_one']
        table = Selector(text='<table><tr><td>{0}<td><td>{1}</td><tr></table>'.format(*headers))
        results = CycloneSpider.get_table_headers(table)
        self.assertEqual(headers[0], results[0])
        self.assertEqual(headers[1], results[1])


class CycloneSpiderGetSynopticTimeForForecastHourUnitTest(unittest.TestCase):

    def setUp(self):
        self.pattern = re.compile(r'(?:\w*:\s*)(\d*$)')

    def test_ok_default(self):
        synoptic_time = 201904291200
        text = Selector(text='<h4>Time of Latest Forecast:{0}</h4>'.format(synoptic_time))
        results = CycloneSpider.get_synoptic_time_for_forecast_hour(self.pattern, text)
        self.assertEqual(synoptic_time, results)

    def test_ok_many_blank_spaces_after_colon(self):
        synoptic_time = 201904291200
        text = Selector(text='<h4>Time of Latest Forecast:   {0}</h4>'.format(synoptic_time))
        results = CycloneSpider.get_synoptic_time_for_forecast_hour(self.pattern, text)
        self.assertEqual(synoptic_time, results)

    def test_ok_many_blank_spaces_before_colon(self):
        synoptic_time = 201904291200
        text = Selector(text='<h4>Time of Latest Forecast    :{0}</h4>'.format(synoptic_time))
        results = CycloneSpider.get_synoptic_time_for_forecast_hour(self.pattern, text)
        self.assertEqual(synoptic_time, results)

    def test_wrong_no_match(self):
        synoptic_time = 201904291200
        text = Selector(text='<h4>... Latest Forecast:{0}</h4>'.format(synoptic_time))
        results = CycloneSpider.get_synoptic_time_for_forecast_hour(self.pattern, text)
        self.assertEqual(None, results)

    def test_wrong_no_numeric_value(self):
        synoptic_time = 'X201904291200'
        text = Selector(text='<h4>Time of Latest Forecast    :{0}</h4>'.format(synoptic_time))
        results = CycloneSpider.get_synoptic_time_for_forecast_hour(self.pattern, text)
        self.assertEqual(None, results)


class CycloneSpiderGetQueryParametersUnitTest(unittest.TestCase):

    def test_ok_default(self):
        data = {'key': 'tkey', 'value': 'tvalue'}
        response = Response(url='', request=Request(url='https://example.com/?{key}={value}'.format(**data)))
        results = CycloneSpider.get_query_parameters(response)
        self.assertEqual({data['key']: [data['value']]}, results)

    def test_ok_not_query_parameters(self):
        response = Response(url='', request=Request(url='https://example.com/'))
        results = CycloneSpider.get_query_parameters(response)
        self.assertEqual({}, results)


class CycloneSpiderGetTableValuesUnitTest(unittest.TestCase):

    def test_ok_default(self):
        values = ['value_one', 'value_two']
        table = Selector(text='<table><tr></tr><tr><td>{0}</td><td>{1}</td></tr></table>'.format(*values))
        results = CycloneSpider.get_table_values(table)
        self.assertSetEqual(set(values), set(results[0]))

    def test_ok_empty_table(self):
        table = Selector(text='<table></table>')
        results = CycloneSpider.get_table_values(table)
        self.assertSetEqual(set(), set(results))

    def test_ok_only_headers(self):
        table = Selector(text='<table><tr><td>head_one</td><td>head_two</td></tr></table>')
        results = CycloneSpider.get_table_values(table)
        self.assertSetEqual(set(), set(results))
