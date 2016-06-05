#coding:utf-8
from scrapy import Spider,Request
from Collector.items import PhoneItem
from Collector.utils.mydict import amazoninfo

class AmazonSpider(Spider):
  name='amazon'
  allowed_domains=['amazon.cn']
  start_urls=[
    'http://www.amazon.cn/s/ref=sr_pg_1?rh=n%3A2016116051%2Cn%3A%212016117051%2Cn%3A664978051%2Cn%3A665002051%2Cp_89%3AHuawei+%E5%8D%8E%E4%B8%BA&ie=UTF8&qid=1452051019',
    'http://www.amazon.cn/s/ref=sr_nr_p_89_3?fst=as%3Aoff&rh=n%3A2016116051%2Cn%3A%212016117051%2Cn%3A664978051%2Cn%3A665002051%2Cp_89%3A%E5%B0%8F%E7%B1%B3&bbn=665002051&ie=UTF8&qid=1452066949&rnid=125596071',
    'http://www.amazon.cn/gp/search/ref=sr_nr_p_89_4?fst=as%3Aoff&rh=n%3A2016116051%2Cn%3A%212016117051%2Cn%3A664978051%2Cn%3A665002051%2Cp_89%3A%E9%AD%85%E6%97%8F&bbn=665002051&ie=UTF8&qid=1452068037&rnid=125596071',
    'http://www.amazon.cn/s/ref=sr_in_-2_p_89_17?fst=as%3Aoff&rh=n%3A2016116051%2Cn%3A%212016117051%2Cn%3A664978051%2Cn%3A665002051%2Cp_89%3AOPPO&bbn=665002051&ie=UTF8&qid=1452069151&rnid=125596071',
    'http://www.amazon.cn/s/ref=sr_in_-2_p_89_39?fst=as%3Aoff&rh=n%3A2016116051%2Cn%3A%212016117051%2Cn%3A664978051%2Cn%3A665002051%2Cp_89%3ANubia+%E5%8A%AA%E6%AF%94%E4%BA%9A&bbn=665002051&ie=UTF8&qid=1452069151&rnid=125596071',
    'http://www.amazon.cn/s/ref=sr_in_-2_p_89_16?fst=as%3Aoff&rh=n%3A2016116051%2Cn%3A%212016117051%2Cn%3A664978051%2Cn%3A665002051%2Cp_89%3Avivo&bbn=665002051&ie=UTF8&qid=1452069151&rnid=125596071',
  ]

  def parse(self,response):   
    xp=lambda s:response.xpath(s).extract()
    for product_id in xp('//li[starts-with(@id,"result_")]/@data-asin'):
      url_comment='http://www.amazon.cn/product-reviews/{}'.format(product_id)
      yield Request(url_comment,callback=self.parse_comment,meta={'product_id':product_id,})
  
    nextpage=xp('//*[@class="pagnHy"]/span[last()]/a/@href')
    if nextpage:
      nextpage=self.start_urls[0][:20]+nextpage[0]
      yield Request(nextpage,callback=self.parse)  

    #为什么这样写筛选不到???
    #for product_id in xp('//*[@id="atfResults"]/ul/li/@data-asin'):

  def parse_comment(self,response):
    xp=lambda s:response.xpath(s).extract()
    if xp('//div[@class="a-row averageStarRatingIconAndCount"]/span[last()]/text()')[0]!='0':  #评论数超过0的才执行
      #为什么不能在这里初始化item?????
      for sel in response.xpath('//div[@id="cm_cr-review_list"]/div[@class="a-section review"]'):
        item=PhoneItem(product_id=response.meta['product_id'],url=response.url,)
        (
        item['product_name'],
        item['product_type'],
        item['series'],
        )=amazoninfo.get(item['product_id'],['Others','Others','Others'])
        item['comment_id']=sel.xpath('@id').extract()[0]
        item['integration_valuation_score']=sel.xpath('./div[@class="a-row"][1]/a/i/span/text()').extract()[0][0]
        _=sel.xpath('./div[@class="a-row"][2]/span[last()]/text()').re(r'\d+')
        if len(_[1])==1: _[1]='0'+_[1]
        if len(_[2])==1: _[2]='0'+_[2]
        item['publish_date']='-'.join(_)     
        item['evaluation']=sel.xpath('string(./div[@class="a-row review-data"])').extract()[0]
        item['customer_name']=sel.xpath('./div[@class="a-row"][2]/span/a/text()').extract()[0]
        item['customer_id']=sel.xpath('./div[@class="a-row"][2]/span/a/@href').re(r'/gp/pdp/profile/(\w+)')[0]
        home_page='http://www.amazon.cn/gp/pdp/profile/{}'.format(item['customer_id'])
        yield Request(home_page,callback=self.parse_home,meta={'item':item},)
   
      num=response.xpath('//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href').re(r'pageNumber=(\d+)')
      if num:
        nextpage='http://www.amazon.cn/product-reviews/{}?pageNumber={}'.format(item['product_id'],num[0])
        meta={'product_id':response.meta['product_id'],}
        yield Request(nextpage,callback=self.parse_comment,meta=meta,)

  def parse_home(self,response):
    yield response.meta['item']
