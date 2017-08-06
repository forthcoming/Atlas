#coding:utf-8
import re
from Spider.items import PhoneItem
from scrapy.linkextractors import LinkExtractor as LE
from scrapy.spiders import CrawlSpider, Rule

class Pcpop_le(CrawlSpider):
  name='pcpop_le'
  allowed_domains=['pcpop.com']
  start_urls=[
             'http://product.pcpop.com/Mobile/01334/',
             #'http://product.pcpop.com/Mobile/00670_4.html',
             #'http://product.pcpop.com/Mobile/01100/',
             ]

  def process_value(value):   #注意位置
    _=re.findall(r'\'(\d*)\'',value)
    #print value
    if _:
      value="http://product.pcpop.com/AjaxDataOperate/ProductComment.aspx?CurrentPage={}&F_ProductSN={}&F_SeriesSN={}&F_BrandSN={}".format(*_)
      #print value
      return value

  rules = [
            Rule(LE(restrict_xpaths='//div[@class="page2"]',),),
            Rule(
                 LE(
                   allow='\d+/Index\.html',
                   restrict_xpaths='//ul[@id="ProductList"]/li/div[@class="title"]',
                   ),
                ),
            Rule(
                 LE(
                   restrict_xpaths='//div[@id="proComPage"]/span',
                   attrs=('onclick','href',),
                   process_value=process_value,
                   ),
                ),
              
            Rule( 
                 LE(
                   restrict_xpaths='//div[@class="title"]',
                   attrs=('href',),
                   unique=False,
                   ),
                 callback='parse_item',
                 ),
          ]      

  def parse_item(self,response):   

    xp=lambda s:response.xpath(s).extract()
    name=xp('//ul[@id="proComList"]/li/div[@class="dian"]/a[last()]/text()')[0]
    item=PhoneItem(url=response.url,)
    item['product_name']=re.match(r'(.+?)\s',name).group(1)
    item['product_type']=name
    item['series']=re.search(r' ([a-zA-Z]+)',name).group(1)
    item['integration_valuation_score']=xp('//ul[@id="proComList"]/li/div[1]/span//text()')[1]
    item['evaluation']=' '.join(xp('//ul[@id="proComList"]/li/dl//text()'))
    item['publish_date']=xp('//ul[@id="proComList"]/li/div[2]/span/text()')[0]  
    yield item
