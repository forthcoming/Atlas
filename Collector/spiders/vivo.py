#coding:utf-8
import re
from scrapy import Spider,Request
from Collector.items import PhoneItem
from scrapy.linkextractors import LinkExtractor as LE

class VivoSpider(Spider):
  name = 'vivo'
  allowed_domains = ['vivo.com.cn']

  def start_requests(self):

    for url in ('http://bbs.vivo.com.cn/forum-121-{}.html'.format(_) for _ in range(1,1000)):  #watch it  !!!
      yield self.make_requests_from_url(url)    #X系列
      
    for url in ('http://bbs.vivo.com.cn/forum-118-{}.html'.format(_) for _ in range(1,1000)):
      yield self.make_requests_from_url(url)    #Xplay系列

    for url in ('http://bbs.vivo.com.cn/forum-138-{}.html'.format(_) for _ in range(1,1000)):
      yield self.make_requests_from_url(url)    #Xshot系列

    for url in ('http://bbs.vivo.com.cn/forum-107-{}.html'.format(_) for _ in range(1,1000)):
      yield self.make_requests_from_url(url)    #Y系列及其他

  def parse(self, response):
    #print response.url
    for sel in response.xpath('//*[@id="moderate"]/table//tbody[re:test(@id,"[a-z]+_\d+")]'):   #watch it  !!!
      url=sel.xpath('.//td[@class="thread_con"]//a[3]/@href').extract()[0]   #watch it !!!
      yield Request(url,callback=self.parse_thread)

  def parse_thread(self,response):
    '''
    series=response.xpath('//div[@class="z"]/a[4]/text()').extract()[0]
    title=response.xpath('//div[@class="z"]/a[5]/text()').extract()[0]
    #这么写代码不够健壮，容易出错
    '''
    #推荐写法
    series=response.xpath('/html/head/meta[@name="keywords"]/@content').extract()[0]   
    title=response.xpath('/html/head/meta[@name="description"]/@content').extract()[0]

    if u'系列' in series:
      '''
      #这么写容易断，注意理解其缺点
      urls=response.xpath('(//div[@class="pg"])[1]/a[last()]/@href').extract()      #watch it!!!
      if urls:
        yield Request(urls[0],callback=self.parse_thread)
      '''
      #推荐写法
      le=LE(restrict_xpaths='//div[@class="pg"]',tags='a',attrs='href',allow='bbs\.vivo\.com\.cn/thread-\d+-\d+-\d+\.html')
      for _ in le.extract_links(response):
        yield Request(_.url,callback=self.parse_thread)  

      
      id=re.search(r'thread-(\d+)-',response.url)
      if id:   #过滤如 http://bbs.vivo.com.cn/forum.php?mod=viewthread&tid=2183027
        id=id.group(1)
        for sel in response.xpath('//*[@id="comment_list"]/div[starts-with(@id,"post_")]/table/tr[1]'):
          item=PhoneItem(thread_id=id,url=response.url,series=series,title=title,)
          #为什么要放在for内部???
          _=sel.xpath('string(td[@class="plc plcon"]/div[@class="pi"]/div[@class="pti"])').extract()[0]
          item['customer_name']=_.split()[0]
          item['publish_date']=re.search(u'\d{4}-\d{1,2}-\d{1,2}',_).group()
          item['evaluation']=''.join(sel.xpath('string(.//*[starts-with(@id,"postmessage_")])').extract()[0].split())
          homepage=sel.xpath('td[@class="pls"]/div[@id]//div[@class="avatar"]/a/@href').extract()[0]
          yield Request(homepage,callback=self.parse_home,meta={'item':item},)


  def parse_home(selfself,response):
    item=response.meta['item']
    customer_id=response.xpath('//span[@class="xw0"]/text()').re(r'\d+')   
    customer_register=response.xpath('//ul[@id="pbbs"]/li[2]/text()').extract()  
    lv=response.xpath('//div[@class="pbm mbm bbda c"]/p[last()-1]/font[1]/b/text()').extract()
    item['customer_id']=customer_id[0] if customer_id else '-1'
    item['customer_register']=customer_register[0] if customer_register else '0000' 
    item['customer_lv']=lv[0] if lv else ''
    yield item
