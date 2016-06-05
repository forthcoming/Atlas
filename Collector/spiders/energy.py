#coding:utf-8
from scrapy import Spider
from Collector.items import OilItem
from Collector.utils.mydict import city

class EnergySpider(Spider):
  name='energy'
  allowed_domains=['energy.Cf8.com.cn']
  start_urls=["http://energy.Cf8.com.cn/quote/crude.shtml"]
      
  def parse(self,response):

    sz=response.xpath('(//table[@class="oilTable"]/tbody/tr//td)/text()').extract()
   
    for index,type in enumerate(response.xpath('//thead/tr/td')[:4]):
      for tdgsj in response.xpath('//table[@class="oilTable"]/tbody/tr//th')[:-1]:
        item=OilItem(priceType='元/升',)
        item['placeName']=tdgsj.xpath('a/text()').extract()[0]
        item['district']=city.get(item['placeName'],'')
        item['oilType']=type.xpath('a/text()').extract()[0]
        item['oilPrice']=sz[index]
        yield item
        index+=4
