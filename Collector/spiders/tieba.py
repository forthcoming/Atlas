#coding:utf-8
import re
from scrapy import Request,Spider
from Collector.items import PhoneItem

class TiebaSpider(Spider):
  name = 'tieba'
  allowed_domains = ['baidu.com']

  def start_requests(self):
    for url in ('http://tieba.baidu.com/f?kw=vivo&ie=utf-8&pn={}'.format(_) for _ in range(0,50,100000)):  #watch it  !!!
    #for url in ('http://tieba.baidu.com/f?kw=vivo&ie=utf-8&pn={}'.format(_) for _ in range(0,50,50)):
      yield self.make_requests_from_url(url)


  def parse(self, response):
    for _ in response.xpath('//*[@id="thread_list"]//@href').re(r'/p/\d+'):
      url=response.urljoin(_)
      yield Request(url,callback=self.parse_thread)
      #print(url)


  def parse_thread(self,response):
    #print(response.url)
    title=response.xpath('/html/head/title/text()').extract()[0][:-11]

    for sel in response.xpath('//*[@id="j_p_postlist"]/div'):
      item=PhoneItem(url=response.url,title=title,)
      _=sel.xpath('@data-field')
      if _:
        item['customer_id']=_.re('"user_id":(\d+)')[0]
        item['customer_name']=_.re('"user_name":"(.+?)"')[0].decode('unicode_escape')   #watch it !!!
        item['publish_date']=_.re('"date":"(\d{4}-\d\d-\d\d)')[0]   #watch it !!! 只能从这里取
        item['evaluation']=''.join(sel.xpath('string(div[@class="d_post_content_main"]/div[1])').extract()[0].split())
        #homepage=response.urljoin(sel.xpath('div[@class="d_author"]/ul[@class="p_author"]/li[@class="d_name"]/a[@data-field]/@href').extract()[0])
        homepage='http://tieba.baidu.com/home/main?un={}&ie=utf-8'.format(item['customer_name'])
        yield Request(homepage,callback=self.parse_home,meta={'item':item},)

    nextpage=response.xpath('(//ul[@class="l_posts_num"]/li/a)[last()-1]/@href').extract()   #不加()则返回2个结果，watch it!!!
    if nextpage:
      yield Request(response.urljoin(nextpage[0]),callback=self.parse_thread)

  def parse_home(self,response):
    item=response.meta['item']
    userinfo=response.xpath('string(//*[@class="userinfo_num"])').extract()[0]
    _=re.search(u'吧龄:([0-9.]+年)',userinfo)
    item['customer_register']=_.group(1) if _ else '0'
    item['customer_comment_num']=re.search(u'发贴:[0-9.]+万|发贴:[0-9.]+',userinfo).group()[3:]     #注意|两边的顺序
    yield item
