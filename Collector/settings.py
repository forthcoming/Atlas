# -*- coding: utf-8 -*-
from os import path


BOT_NAME = 'Collector'
SPIDER_MODULES = ['Collector.spiders']
NEWSPIDER_MODULE = 'Collector.spiders'

ITEM_PIPELINES = {
    'Collector.pipelines.JsonPipeline': 300,
}

DOWNLOADER_MIDDLEWARES = {
    #'Collector.utils.middlewares.MyHttpProxyMiddleware':400,
    'Collector.utils.middlewares.MyUserAgentMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

COOKIES_ENABLED=True      #Default True,If disabled, no cookies will be sent to web servers.

DOWNLOAD_DELAY=0.5 
#当设置DOWNLOADER_MIDDLEWARES时，默认的USER_AGENT就无效了
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'

ROBOTSTXT_OBEY = False

'''
DUPEFILTER_CLASS = 'Collector.utils.middlewares.MyRFPDupeFilter'
DEPTH_LIMIT=15
DEFAULT_REQUEST_HEADERS={
  'Host':'jandan.net',
  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
  'Accept-Encoding':"gzip, deflate",
  'Referer':"http://jandan.net/ooxx",
  'Connection':"keep-alive",
  'If-Modified-Since':'Sat, 01 Aug 2015 06:47:18 +0000'
}
'''

DATAPATH='{}/../data/'.format(path.split(__file__)[0])
PHOTOPATH='{}/../photo/'.format(path.split(__file__)[0])

