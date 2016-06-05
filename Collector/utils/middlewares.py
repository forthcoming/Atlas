#coding:utf-8
import random,os
from Collector.utils.mydict import agent_list,ip_list
from scrapy.dupefilters import RFPDupeFilter

class MyUserAgentMiddleware():
  def process_request(self, request, spider):
    request.headers['User-Agent'] = random.choice(agent_list)


class MyHttpProxyMiddleware():
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
