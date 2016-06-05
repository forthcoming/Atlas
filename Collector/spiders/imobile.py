#coding:utf-8
import re
from scrapy.linkextractors import LinkExtractor as LE
from scrapy.spiders import CrawlSpider, Rule
from Collector.items import PhoneItem

class ImobileSpider(CrawlSpider):
  name = 'imobile'
  allowed_domains = ['imobile.com.cn']
  start_urls = ['http://product.imobile.com.cn/list-brand_id-57.html']
  rules = [
          Rule(
               LE(
                 tags=('a'),
                 restrict_xpaths='//ul[@class="tabinfo"]',
                 allow='/show/\d*?\.html',
                 ),
               follow=True, # must be True
              ),
          Rule(
               LE(
                 allow='/comment/\d*?\.html',
                 #restrict_xpaths='//ul[@id="phone_nav"]',
                 ),
               callback='parse_item'
              ),
          ]

  def parse_item(self, response):

    _=response.xpath('//h2[@class="interest"]/text()').extract()[0]
    product_name=_[:4]
    series=re.search(r'(?<=vivo)[a-zA-Z]+|(?<=\s)[a-zA-Z]+',_).group()
    product_type=_[4:].strip() # delete both sides' blank(\n \t \r)

    for sel in response.xpath('//div[@class="cont left"]/div[@class="boxBord"]/div'):
      item=PhoneItem(url=response.url,product_name=product_name,series=series,product_type=product_type)
      item['customer_id']=sel.xpath('./h3[@class="titGrade"]/span/text()').extract()[0]
      item['integration_valuation_score']=sel.xpath('./div[@class="gradeBox left"]/h4/span/text()').extract()[0]
      score=sel.xpath('./div[@class="gradeBox left"]/dl/dd/span/text()').extract()
      (
       item['appearance_score'],
       item['cost_performance_score'],
       item['brand_score'],
       item['fluency_score'],
      )=score
      item['publish_date']=sel.xpath('./h3[@class="titGrade"]/em/text()').extract()[0][4:]
      item['evaluation']=','.join(sel.xpath('./ul[@class="tagBox right clear"]/li/text()').extract())
      yield item
