#coding:utf-8
from scrapy import Spider,Request
import re
from Collector.items import PhoneItem

class PcpopSpider(Spider):
  name='pcpop'
  allowed_domains=['pcpop.com']
  start_urls=[
             #'http://product.pcpop.com/Mobile/01100/',
             "http://product.pcpop.com/Mobile/01334/",
             ]

  def parse(self,response):
    urls=response.xpath('//div[@class="p_list"]/ul/li/div[2]/a/@href').extract()
    for url in urls:
      url=url.replace('Index','Comment')
      yield Request(url,callback=self.parse_item)
    nextpage=response.xpath('//div[@class="page2"]/a[last()]/@href').extract()[0]
    yield Request(nextpage,callback=self.parse)

  
  def parse_item(self,response):   

    if 'Comment.html' in response.url:
      product_type=response.xpath('//span[@style="float:left"]/a[5]/text()').extract()[0]
    else:
      product_type=response.meta['type']
    product_name=re.match(r'(.+?)\s',product_type).group(1)
    series=re.search(r' ([a-zA-Z]+)',product_type).group(1)
    item=PhoneItem(series=series,product_type=product_type,url=response.url,product_name=product_name,)
    for sel in response.xpath('//*[@id="proComList"]//li'):  #for循环一定要通用
 
      score=sel.xpath('./div[@class="title"]/span//text()').extract()
      if score:
        item['integration_valuation_score']=score[1].strip()
        item['evaluation']=' '.join(sel.xpath('./dl//text()').extract())
        item['publish_date']=sel.xpath('./div[@class="dian"]/span/text()').extract()[0]
        yield item
    nextpage=response.xpath('(//div[@id="proComPage"]/span)[1]/a[last()]').extract()
    if nextpage:
      _=re.findall(r'\'(\d*)\'',nextpage[0])
      nextpage="http://product.pcpop.com/AjaxDataOperate/ProductComment.aspx?CurrentPage={}&F_ProductSN={}&F_SeriesSN={}&F_BrandSN={}".format(*_)
      yield Request(nextpage,meta={'type':product_type},callback=self.parse_item)