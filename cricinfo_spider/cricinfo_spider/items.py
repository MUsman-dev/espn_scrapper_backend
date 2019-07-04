# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CricinfoSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    how_out = scrapy.Field()
    name = scrapy.Field()
    fielder = scrapy.Field()
    bowler = scrapy.Field()
    runs = scrapy.Field()
    inns = scrapy.Field()
    opposition = scrapy.Field()
    ground = scrapy.Field()
    start_date = scrapy.Field()
    description = scrapy.Field()
    balls = scrapy.Field()
    minutes = scrapy.Field()
    fours = scrapy.Field()
    sixes = scrapy.Field()
    strike_rate = scrapy.Field()