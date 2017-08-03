#coding:utf-8
import random,os
from Spider.utils.mydict import agent_list,ip_list
from scrapy.dupefilters import RFPDupeFilter
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from pydispatch import dispatcher
from Spider.settings import *

class HeadersMiddleware:
  def process_request(self, request, spider):
    request.headers['User-Agent'] = random.choice(agent_list)


class ProxiesMiddleware:
  def process_request(self, request, spider):
    if 'proxy' in request.meta:  # ignore if proxy is already seted
      return
    #request.meta['proxy']=random.choice(self.ip_list)
    request.meta['proxy']=ip_list[1]


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