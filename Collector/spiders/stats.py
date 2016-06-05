#coding:utf-8
from scrapy import Spider,Request
from Collector.items import StatsItem

class StatsSpider(Spider):
  name='stats'
  allowed_domains=['stats.gov.cn']
  start_urls=['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2013/index.html']

  def parse(self,response):
    for sel in response.xpath('//tr[@class="provincetr"]/td'):
      province=sel.xpath('a/text()').extract()[0]
      url=response.urljoin(sel.xpath('a/@href').extract()[0])    #注意此时urljoin的用法
      yield Request(url,callback = self.parse_city,meta={'province':province,}) 
       

  def parse_city(self,response):
    for sel in response.xpath('//table[@class="citytable"]/tr[@class="citytr"]'):
      code1=sel.xpath('td[1]//text()').extract()[0]
      city=sel.xpath('td[2]//text()').extract()[0]
      url=response.urljoin(sel.xpath('td[1]/a/@href').extract()[0])
      response.meta.update({'code1':code1,'city':city})      #利用update合并字典效率最高
      yield Request(url,callback = self.parse_county,meta=response.meta) 


  def parse_county(self,response):
    for sel in response.xpath('//table[@class="countytable"]/tr[@class="countytr"]'):
      code2=sel.xpath('td[1]//text()').extract()[0]
      county=sel.xpath('td[2]//text()').extract()[0]
      url=response.urljoin(sel.xpath('td[1]/a/@href').extract()[0])
      response.meta.update({'code2':code2,'county':county}) 
      yield Request(url,callback = self.parse_town,meta=response.meta) 

     
  def parse_town(self,response):
    for sel in response.xpath('//table[@class="towntable"]/tr[@class="towntr"]'):
      code3=sel.xpath('td[1]//text()').extract()[0]
      town=sel.xpath('td[2]//text()').extract()[0]
      url=response.urljoin(sel.xpath('td[1]/a/@href').extract()[0])
      response.meta.update({'code3':code3,'town':town}) 
      yield Request(url,callback = self.parse_village,meta=response.meta) 
    
  def parse_village(self,response):
    for sel in response.xpath('//table[@class="villagetable"]/tr[@class="villagetr"]'):
      code4=sel.xpath('td[1]//text()').extract()[0]
      classify=sel.xpath('td[2]//text()').extract()[0]
      village=sel.xpath('td[3]//text()').extract()[0]
      yield StatsItem(
                     province=response.meta.get('province',''),
                     code1=response.meta.get('code1',''),
                     city=response.meta.get('city',''),
                     code2=response.meta.get('code2',''),
                     county=response.meta.get('county',''),
                     code3=response.meta.get('code3',''),
                     town=response.meta.get('town',''),
                     code4=code4,
                     classify=classify,
                     village=village,
                    )