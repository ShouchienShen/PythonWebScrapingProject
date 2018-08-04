# -*- coding: utf-8 -*-
# scrapy web scraping project
# WEBMD pain medications Spider

# Scrapy settings for webmd project

BOT_NAME = 'webmd'

SPIDER_MODULES = ['webmd.spiders']
NEWSPIDER_MODULE = 'webmd.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
ITEM_PIPELINES = {
    'webmd.pipelines.WebmdPipeline': 300,
}

DOWNLOAD_DELAY = 1
