# -*- coding: utf-8 -*-
# scrapy web scraping project
# WEBMD pain medications

# define model for scraped items
import scrapy

class WebmdItem(scrapy.Item):
    # define the fields for item:
    drug = scrapy.Field()
    condition = scrapy.Field()
    date = scrapy.Field()
    age = scrapy.Field()
    gender = scrapy.Field()
    treatment_length = scrapy.Field()
    reviewer_status = scrapy.Field()
    effectiveness = scrapy.Field()
    ease_of_use = scrapy.Field()
    satisfaction = scrapy.Field()
    comment = scrapy.Field()
