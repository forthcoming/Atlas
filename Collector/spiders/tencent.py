#coding=utf-8
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor as LE
from Collector.items import JobItem

class TencentSpider(CrawlSpider):

  custom_settings = {
      'DEPTH_LIMIT':1,
  }
  name = "tencent"
  allowed_domains = ["tencent.com"]
  start_urls = ["http://hr.tencent.com/position.php"]
  rules =(
         Rule(
             LE(allow=("start=\d{,4}#a")),
             follow=True,
             callback='parse_item',    #注意这里不能写成callback=self.parse_item
         ),
  )

  def parse_item(self,response):
    print('\n***\n',response.url,response.meta['depth'],'\n***\n')
    '''
    当depth_limit=1时打印如下:
    http://hr.tencent.com/position.php?start=10 1
    http://hr.tencent.com/position.php?start=20 1
    http://hr.tencent.com/position.php?start=30 1
    http://hr.tencent.com/position.php?start=40 1
    http://hr.tencent.com/position.php?start=50 1
    http://hr.tencent.com/position.php?start=60 1
    http://hr.tencent.com/position.php?start=70 1
    http://hr.tencent.com/position.php?start=1490 1
    注意第一页的depth=2,他是通过depth=1的页面获得的
    再来看make_requests_from_url函数
    def make_requests_from_url(self, url):
      return Request(url, dont_filter=True)
    这里为什么要用dont_filter=True ?(本例中start_urls[0]就被访问了2次，所以要用dont_filter=True来说明)
    '''
    for sel in response.xpath('//table[@class="tablelist"]/tr')[1:-1]:  #注意这里按数组处理 
      item = JobItem(catalog='')
      item['name'] = sel.xpath('td[1]/a/text()').extract()[0]
      item['datailLink'] = response.url
      catalog = sel.xpath('td[2]/text()').extract()
      if catalog:item['catalog']=catalog #这里一定要判断，不然catalog有的是空
      item['workLocation'] = sel.xpath('td[4]/text()').extract()[0]
      item['recruitNumber'] = sel.xpath('td[3]/text()').extract()[0]
      item['publishTime'] = sel.xpath('td[5]/text()').extract()[0]
      yield item
