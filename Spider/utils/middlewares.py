#coding:utf-8
import random,os
from Spider.utils.dictionary import agent_list,ip_list
from scrapy.dupefilters import RFPDupeFilter
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from pydispatch import dispatcher
from Spider.settings import *

class HeadersMiddleware:
    def process_request(self, request, spider):
        # print('Using HeadersMiddleware!')
        request.headers['User-Agent'] = random.choice(agent_list)

class ProxiesMiddleware:
    def process_request(self, request, spider):
        if not request.meta.get('proxy'):  # ignore if proxy is already seted
            # print('Using ProxiesMiddleware!')
            # request.meta['proxy']=random.choice(self.ip_list)
            request.meta['proxy']='http://H37XPSB6V57VA96D:CAB31DADB9313CE5@proxy.abuyun.com:9020'

class MyRFPDupeFilter(RFPDupeFilter):
  '''
  scrapy默认过滤规则:
  相同网址和不属于allow_domains的都自动过滤
  当使用dont_filter=True后不过滤（以上2条失效）
  '''

  def request_seen(self, request):
    #fp = self.request_fingerprint(request)
    fp=request.url
    if fp in self.fingerprints:
      return True
    self.fingerprints.add(fp)
    if self.file:
      self.file.write(fp + os.linesep)

class JSRenderMiddleware:
    def __init__(self):
        dispatcher.connect(self.spider_closed,signals.spider_closed)
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--blink-settings=imagesEnabled=false')
        # options.add_argument('--proxy-server=http://127.0.0.1:8118')
        options.add_argument(f'--user-data-dir={CHROME_DATA}')
        # options.add_argument('--user-agent=Spider')
        # options.add_argument('--start-maximized')
        # options.add_argument('--window-size=500,500')
        self.driver = webdriver.Chrome(chrome_options=options,executable_path='/opt/google/chrome/chromedriver')

    def process_request(self, request, spider):
        self.driver.get(request.url)
        content = self.driver.page_source
        return HtmlResponse(request.url, body=content, encoding='utf-8')

    def spider_closed(self, spider):
        self.driver.quit()

class SpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
