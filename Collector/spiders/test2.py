# -*- coding: utf-8 -*-
'''
需要开启splash
pip install scrapy-splash
'''
from scrapy import Spider
from scrapy_splash import SplashRequest

class SplashSpider(Spider):    #splash速度是phantomjs的3倍
  
  name = 'splash'
  custom_settings = {
    'DOWNLOADER_MIDDLEWARES':{
      # Engine side
      'scrapy_splash.SplashCookiesMiddleware': 723,
      'scrapy_splash.SplashMiddleware': 725,
      'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
      # Downloader side
    },
    'SPIDER_MIDDLEWARES':{
      'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    },
    'SPLASH_URL':'http://127.0.0.1:8050/',
    'DUPEFILTER_CLASS':'scrapy_splash.SplashAwareDupeFilter',
    'HTTPCACHE_STORAGE':'scrapy_splash.SplashAwareFSCacheStorage',
  }

  def start_requests(self):
    url='http://www.toutiao.com'
    yield SplashRequest(url,self.parse,endpoint='render.json',args={'har': 1,'html': 1,})

  def parse(self, response):
    print("PARSED", response.real_url, response.url)
    print(response.data["har"]["log"]["pages"])
    with open('splash.html','wb') as f:
      f.write(response.body)
