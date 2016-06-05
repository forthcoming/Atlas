#coding:utf-8
from scrapy.utils.spider import iterate_spider_output
from scrapy.linkextractors import LinkExtractor as LE
from scrapy.spiders import CrawlSpider, Rule,Request
from re import compile,sub,search
from Collector.items import PhoneItem

class Zol_plusSpider(CrawlSpider):
  name='zol_plus'
  allowed_domains = ['zol.com.cn']

  rules = [
          #http://detail.zol.com.cn/1140/1139537/review.shtml
          Rule(LE(allow='/\d+/\d+/review\.shtml'),),
          #http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&keyword=vivo&page=2
          #http://detail.zol.com.cn/xhr3_Review_GetListAndPage_proId=392874%5EisFilter=1%5Eorder=1.html
          Rule(
               LE(restrict_xpaths='//div[@class="page"]',),
               follow=True,   #此处follow必须为True，否则不管深度为多少本rule规则不起效,(此处默认为True)
               process_links='process_links',
               ),
          #http://detail.zol.com.cn/1140/1139537/review_0_0_1335425_1.shtml#tagNav
          Rule(
               LE(
                 tags=('a'),
                 restrict_xpaths='//div[@class="comments-content"]',
                 allow=r'/\d+/\d+/review',
                 ),
               callback='parse_comment',
               ),
          ]

  # 由于zol调皮了，所以请求时得添加cookies信息和头信息，才给访问哦
  def start_requests(self):
    urls=['http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&keyword=vivo']
    cookie = {
      'listSubcateId': '57',
      'visited_serachKw': 'vivo',
    }
    head = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
    }
    for url in urls:
      yield Request(url, cookies=cookie, dont_filter=True, headers=head)

  def _parse_response(self, response, callback, cb_kwargs, follow=True):

    if 'isFilter' in response.url:     #watch it!!!!!!!
      response=response.replace(body=str(response.body.decode('unicode_escape').replace('\/','/')))

    #super()._parse_response(response, callback, cb_kwargs, follow=True),为什么不行？？？
    if callback:
      cb_res = callback(response, **cb_kwargs) or ()
      cb_res = self.process_results(response, cb_res)
      for requests_or_item in iterate_spider_output(cb_res):
        yield requests_or_item

    if follow and self._follow_links:
      for request_or_item in self._requests_to_follow(response):
        yield request_or_item


  def process_links(self,links):
    regex=compile(r'(?<=&)proId=\d*|(?<=&)page=\d*')
    for link in links:
      _=regex.findall(link.url)
      if 'isFilter' in link.url:  #如果没找到，说明link来自start_urls的分页
        link.url='http://detail.zol.com.cn/xhr3_Review_GetListAndPage_order=1%5EisFilter=1%5E{}%5E{}.html'.format(*_)
      yield link

  def parse_comment(self,response):
    xp=lambda s:response.xpath(s).extract()
    name=xp('(//div[@class="breadcrumb"]/a)[4]/text()')[0]   #注意括号
    evaluation=sub(r'\s','',xp('string(//div[@class="comments-content"])')[0]) #注意\s用法
    score=xp('//ul[@class="score-item clearfix"]/li/span[2]/text()')
    integration=xp('(//div[@class="comments-score clearfix"]/div)[1]/strong/text()')
    item=PhoneItem(url=response.url)
    item['product_name'],item['product_type']=name.split(' ',1) #分割1次
    item['series']=search(r' ([a-zA-Z]+)',name).group(1)   #注意要通用,是group(1)
    item['customer_id']=xp('//div[@class="comments-user-name"]//a/text()')[0]
    item['publish_date']=evaluation[:10]
    item['evaluation']=evaluation[10:]
    item['integration_valuation_score']=integration[0] if integration else ''
    (
     item['battery_score'],
     item['screen_score'],
     item['photo_score'],
     item['video_entertainment_score'],
     item['appearance_score'],
     item['cost_performance_score'],
    )=score if score else ('','','','','','')
    yield item
