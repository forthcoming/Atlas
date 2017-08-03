#coding=utf-8
'''
1. 调用start_requests
2. 调用make_requests_from_url,
3. 生成Request对象，由于未指定callback，默认调用parse
4. 调用parse
5. 调用parse_start_url
6. 执行rules规则
rules执行顺序:
6.1 restrict_xpaths & allow限定地址区域和类型
6.2 LinkExtractor获取地址(LinkExtractor.extract_links()实现)
6.3 process_links筛选地址
6.4 process_request重新发送请求
6.5 callback处理请求

如果不跟进的话，设置DEPTH_LIMIT也没用
LinkExtractor提取链接，Rule定义如何抓取数据
'''

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as LE
from scrapy.utils.spider import iterate_spider_output
from scrapy.http import Request, HtmlResponse

class MininovaSpider(CrawlSpider):

  name = 'mininova'
  allowed_domains = ['mininova.org']
  start_urls = ['http://www.mininova.org']
  rules = (
    Rule(
      LE(restrict_xpaths='//table[1]//a',
      #allow ='/tor/\d+',
      ),
      process_links='process_links',   #此处的筛选不常用，在LE中就可以把地址筛选好
      process_request='process_request',
      callback='parse_torrent',
      follow=True
    ),
    Rule(LE(restrict_xpaths='//h1//a',),),
  )

  def parse(self, response):
    print('parse')
    return self._parse_response(response, self.parse_start_url, cb_kwargs={}, follow=True)  #触发Rule的入口

  #第一次由parse调用，后面每次由_response_downloaded调用，形成闭环
  def _parse_response(self, response, callback, cb_kwargs, follow=True):
    if callback:
      cb_res = callback(response, **cb_kwargs) or ()    #第一次调用parse_start_url，后面每次调用Rule中指定的callback
      cb_res = self.process_results(response, cb_res)   #给什么返回什么
      for requests_or_item in iterate_spider_output(cb_res):
        yield requests_or_item
    if follow and self._follow_links:     #如果follow=True,则跟进(默认True)
      for request_or_item in self._requests_to_follow(response):   #开始rule规则
        yield request_or_item

  def _requests_to_follow(self, response):   #由_parse_response调用
    if not isinstance(response, HtmlResponse):
      return
    seen = set()
    for n, rule in enumerate(self._rules):  #遍历rules
      links = [l for l in rule.link_extractor.extract_links(response) if l not in seen] #此处已进行LE筛选，先于process_request
      if links and rule.process_links:   #如果有过滤规则process_links，则对links进行筛选
        links = rule.process_links(links)
      for link in links:   #此时link是个对象，包含url和text,且都为需要访问的地址,并将该links加入到seen集合
        seen.add(link)
        r = Request(url=link.url, callback=self._response_downloaded)  #实例化Request类
        '''
        Request实例化默认参数如下
        Request(url,callback=None,method='GET',headers=None,body=None,cookies=None,meta=None,encoding='utf-8',priority=0,dont_filter=False,errback=None)
        '''
        r.meta.update(rule=n, link_text=link.text)  #添加meta信息
        yield rule.process_request(r)    #调用rule指定的process_request,并传递Request请求

  def _response_downloaded(self, response):   #由_requests_to_follow调用
    rule = self._rules[response.meta['rule']]  #返回rules的第n个rule
    return self._parse_response(response, rule.callback, rule.cb_kwargs, rule.follow)  #用到了rule的follow和callback规则

  def parse_start_url(self, response):
    print('parse_start_url')
    for sel in response.xpath('//table[1]//a/@href').extract():
      if '/tor/' in sel:
        print(sel)

  def process_links(self,links):
    print('process_links')
    for link in links:
      if '/tor/' in link.url:
        print(link.url,'------------------\n')
        yield link

  def process_request(self,request):
    print('process_request')
    request.headers['User-Agent']="Mozilla/5.0"
    #request.meta['proxy'] = 'http://183.207.228.11:86'   #watch it!!!!!
    return request

  def parse_torrent(self, response):
    print('parse_torrent',response.request.headers['User-Agent'])