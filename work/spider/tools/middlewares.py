#coding:utf-8
import random,os
from tools.dictionary import pc_agent,ip_list
from scrapy.dupefilters import RFPDupeFilter
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from pydispatch import dispatcher
from spider.settings import *

class HeadersMiddleware:
    def process_request(self, request, spider):
        # print('Using HeadersMiddleware!')
        request.headers['User-Agent'] = random.choice(pc_agent)

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
        options = webdriver.ChromeOptions()  # chrome和chromedriver一定要同时用最新版
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--blink-settings=imagesEnabled=false')
        # options.add_argument('--proxy-server=http://127.0.0.1:8118')
        options.add_argument(f'--user-data-dir={CHROME_DATA}')
        # options.add_argument('--user-agent=chrome')
        # options.add_argument('--start-maximized')  # 只适用于非headless模式
        # options.add_argument('--window-size=500,500')
        self.driver = webdriver.Chrome(chrome_options=options,executable_path='/opt/google/chrome/chromedriver')

    def process_request(self, request, spider):
        self.driver.get(request.url)
        content = self.driver.page_source
        return HtmlResponse(request.url, body=content, encoding='utf-8')

    def spider_closed(self, spider):
        self.driver.quit()
