# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CycloneItem(scrapy.Item):
    name = scrapy.Field()


class ForecastItem(scrapy.Item):
    research_geographical_area = scrapy.Field()
    forecast_center = None
    cyclone = scrapy.Field()
    synoptic_time = scrapy.Field()
    type = scrapy.Field()


class ForecastTrackItem(scrapy.Item):
    forecast_hour = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    intensity = scrapy.Field()
