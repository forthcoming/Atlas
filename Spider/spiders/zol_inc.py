#coding:utf-8
import re
from scrapy import Request
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor as LE
from scrapy.spiders import CrawlSpider, Rule
from Spider.items import PhoneItem
from time import strftime,time,localtime

#只要前一天的数据
class ZOl_inc(CrawlSpider):
    name = 'zol_inc'
    allowed_domains = ['zol.com.cn']
    start_urls = [
                 'http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&keyword=vivo',
                 'http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&keyword=OPPO',
                 'http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&manuId=34645&keyword=%D0%A1%C3%D7',
                 'http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&manuId=1434&keyword=%F7%C8%D7%E5',
                 'http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&manuId=35005&keyword=%C5%AC%B1%C8%D1%C7',
                 'http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&manuId=613&keyword=%BB%AA%CE%AA',
                 ]
    TIME=strftime('%Y%m%d%H%M')
    SCRAPY_DATE=strftime('%Y-%m-%d')
    rules = [
            Rule(
                 LE(
                   tags=('a'),
                   restrict_xpaths='//div[@class="page"]',
                   deny='isFilter',
                   ),

                 follow=True,
                 callback='parse_num',
                 ),
            ]

    def parse_num(self, response):
      for sel in response.xpath('//div[@class="list-box"]/div[@class="list-item clearfix"]'):
        num=sel.xpath('div[@class="pro-intro"]/div[@class="special clearfix"]/div[@class="grade"]/span/a/@href').re(r'/\d+/(\d+)/review\.shtml')[0]
        url='http://detail.zol.com.cn/xhr3_Review_GetListAndPage_order=2%5EisFilter=1%5EproId='+num+'%5Epage=1.html'
        yield Request(url,callback=self.parse_item,)


    def parse_item(self, response):
      sel=Selector(text=response.body.decode('unicode_escape').replace('\/','/'))
      yesterday=strftime('%Y-%m-%d',localtime(time()-24*3600))    #时间戳格式转换成具体日期

      for _ in sel.xpath('//li[@class="comment-item"]/div[@class="comments-list-content"]'):
        DATE=_.xpath('div[@class="single-score clearfix"]/span/text()').extract()[0]
        if DATE==yesterday:
          url=_.xpath('div[@class="comments-content"]/h3/a/@href').extract()[0]
          yield Request(response.urljoin(url),callback=self.parse_comment)

        elif DATE<yesterday:
          return


      next_page=sel.xpath('//div[@class="page"]/a[last()]/@href').re(r'page=\d+')[0]
      next_page=re.sub(r'page=\d+',next_page,response.url)
      yield Request(next_page,callback=self.parse_item)


    def parse_comment(self,response):
      xp=lambda s:response.xpath(s).extract()
      evaluation=re.sub(r'\s','',xp('string(//div[@class="comments-content"])')[0])
      score=xp('//ul[@class="score-item clearfix"]/li/span[2]/text()')
      integration=xp('(//div[@class="comments-score clearfix"]/div)[1]/strong/text()')

      item=PhoneItem()
      item['publish_date']=evaluation[:10]
      item['url']=response.url
      item['customer_id']=xp('//div[@class="comments-user-name"]//a/text()')[0]
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
