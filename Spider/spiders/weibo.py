#coding:utf-8
'''
COOKIES_ENABLED=False时自定义head中的cookie才生效,此时scrapy的cookie中间件将被禁用
COOKIES_ENABLED=True时在Request中使用meta={'dont_merge_cookies':True},使自定义head中的cookie生效,但cookie不能传递下去，每次请求需手动带上cookie信息
COOKIES_ENABLED=True时Request的cookies参数才会生效，且写入到scrapy的中间件中,当指定cookies={'a':'b'}时会将其update到已有的cookie字典中
cookiejar用来标记每个cookies,Request通过它来判断使用哪个cookies
proxy用来设置代理,eg meta={'proxy':'http://ip:port'}
'''

import re
from Spider.utils.cookie import Login
from scrapy import Spider,Request
from Spider.items import TweetItem,CommentItem,RelayItem,AttitudeItem
from time import strftime,time,localtime

class Weibo(Spider):

  custom_settings = {
    'ITEM_PIPELINES':{'Spider.pipelines.SqlPipeline':301},
    'COOKIES_ENABLED':True,
  }
  name='weibo'
  allowed_domains=['weibo.cn']
  start_urls=(
    'http://weibo.cn',
  )

  def start_requests(self):
    head={
    'User-Agent': 'avatar',
    'Cookie':'here',
    }
    for url in self.start_urls:
      yield Request(url,dont_filter=True,callback=self.parse_tweet,cookies=Login('sina')(),headers=head,meta={'cookiejar':8},)

  def parse_tweet(self,response):
    #response.request即代表了产生response的request对象，可以获取到诸如headers,callback,url等信息
    #print(response.request.headers['Cookie'])
    item=TweetItem()
    for sel in response.xpath('//div[@class="c" and starts-with(@id,"M_")]'):
      item['news_id'] = sel.xpath('@id').extract()[0]
      item['title'],item['content']=self.tweet_extract(sel,len(sel.xpath('div')))  #注意有的微博没有标题
      publish_time= sel.xpath('div[last()]/span[@class="ct"]/text()').extract()[0] #注意要限定
      item['publish_time'] =self.time_extract(publish_time)
      (
       item['num_praise'],
       item['num_relay'],
       item['num_comment'],
      )=sel.xpath('div[last()]/a/text()')[-4:-1].re(r'\[(\d*)\]')    #注意转义,此处不能使用extract
      #sel.xpath('div[last()]/a/text()')[-4:-1].re(r'\d+') 
      yield item

      if item['num_praise']:
        #注意点赞地址不要直接双击
         url='http://weibo.cn/attitude/'+item['news_id'][2:]
         yield Request(url,callback = self.parse_attitude,meta={'news_id':item['news_id'],'cookiejar': response.meta['cookiejar']})
      if item['num_relay']:
        url='http://weibo.cn/repost/'+item['news_id'][2:]
        yield Request(url,callback = self.parse_relay,meta={'news_id':item['news_id'],'cookiejar': response.meta['cookiejar']})

      if item['num_comment']:
        url='http://weibo.cn/comment/'+item['news_id'][2:]
        yield Request(url,callback = self.parse_comment,meta={'news_id':item['news_id'],'cookiejar': response.meta['cookiejar']})

    nextpage=response.xpath('//div[@id="pagelist"]/form/div/a[1]/@href').extract()[0]
    yield Request(response.urljoin(nextpage),callback = self.parse_tweet,meta={'cookiejar': response.meta['cookiejar']})

  def parse_attitude(self,response):

    item=AttitudeItem(news_id=response.meta['news_id'])
    for sel in response.xpath('//div[@class="c"]')[3:-1]:   #注意用法
      praise_date= sel.xpath('span[@class="ct"]/text()').extract()[0]  #注意要限定
      item['praise_date']=self.time_extract(praise_date)
      item['user_id']=sel.xpath('a[1]/@href').extract()[0]
      yield item   
  
    nextpage=response.xpath('//*[@id="pagelist"]/form/div/a[1]/@href').extract()
    if nextpage:
      yield Request(response.urljoin(nextpage[0]),callback = self.parse_attitude,meta={'news_id':item['news_id'],'dont_redirect':True,'handle_httpstatus_list': [302],'cookiejar': response.meta['cookiejar']})
      # 'handle_httpstatus_list': [302,]表示状态码为302的也抓取，但仅针对请求的地址有效，
	  # 要想对整个工程起效，应该定义如下：handle_httpstatus_list = [404]
	  
  def parse_relay(self,response):

    item=RelayItem(news_id=response.meta['news_id'])
    for sel in response.xpath('//div[@class="c"]')[3:-1]:   #注意用法
      relay_date= sel.xpath('span[@class="ct"]/text()').extract()  #注意要限定
      if relay_date:    #去掉查看更多的标签
        item['user_id']=sel.xpath('a[1]/@href').extract()[0]
        item['relay_date']=self.time_extract(relay_date[0])
        item['num_praise'] = sel.xpath('span[@class="cc"]/a/text()').re(r'\[(\d*)\]')[0]
        item['relays']=sel.xpath('./text()').extract()[0][1:]
        yield item  
    nextpage=response.xpath('//*[@id="pagelist"]/form/div/a[1]/@href').extract()
    if nextpage:
      yield Request(response.urljoin(nextpage[0]),callback = self.parse_relay,meta={'news_id':item['news_id'],'dont_redirect':True,'cookiejar': response.meta['cookiejar']}) #自动去重
    

  def parse_comment(self,response):
    item=CommentItem(news_id=response.meta['news_id'])
    for sel in response.xpath('//div[@class="c" and @id!="M_"]'):   #注意用法
      item['comment_id']=sel.xpath('@id').extract()[0]
      item['comments']=sel.xpath('string(span[@class="ctt"])').extract()[0]
      item['user_id']=sel.xpath('a[1]/@href').extract()[0]
      comment_date=sel.xpath('span[@class="ct"]/text()').extract()[0]
      item['comment_date']=self.time_extract(comment_date)
      item['num_attitude']=sel.xpath('span[@class="cc"]/a/text()')[0].re(r'\[(\d*)\]')[0]
      yield item  
    nextpage=response.xpath('//*[@id="pagelist"]/form/div/a[1]/@href').extract()
    if nextpage:
      yield Request(response.urljoin(nextpage[0]),callback = self.parse_comment,meta={'news_id':item['news_id'],'dont_redirect':True,'cookiejar': response.meta['cookiejar']}) #自动去重

      #去除字符串中空白符（ \n等）
      #content= sel.xpath('string(//div[@id="article"])').extract()[0]
      #item['content'] =''.join(content.split()) 
      

  def time_extract(self,string):
    '''
    string如下：
    2009-12-09 10:37:51 来自关联博客
    09月03日 23:09 来自IT之家
    今天 15:40 来自微博 weibo.com
    1分钟前 来自iPhone 6 Plus
    31分钟前 来自微博 weibo.com
    '''
    string=string.strip()      #针对转发时间有空格的情况 
    #string=re.match('.*(?= 来自)',string).group()  
    string=re.sub(' 来自.*','',string)     #提取“ 来自”前面的内容,比match更通用 ,为什么这里用\s 空格等都不行，只能复制粘贴？？？
    if '月' in string and '日' in string:                        
      string=strftime('%Y-')+string.replace('月','-').replace('日','')+':00'
    elif '今天' in string:
      string=strftime('%Y-%m-%d')+string.replace('今天','')+':00'
    elif '分钟前' in string:
      minute=int(re.match('\d*',string).group())
      string=strftime('%Y-%m-%d %H:%M:%S',localtime(time()-minute*60))    #重要
    return string

  def tweet_extract(self,sel,length):
    if length==2:
      _=sel.xpath('string(div[1]/span[@class="ctt"])').extract()[0]  #注意要限定,还要通用（@情形等）
    else:
      #sel.xpath('string(div[last()]/span[@class="cmt"])').extract()  #Wrong
      _=sel.xpath('string(div[last()])').extract()[0]
    regex=re.compile('http://.+|赞\[\d*\].+')   #赞那个是针对转发做的，注意通用性
    _=regex.sub('',_)                          #去网址及后面的内容   
    if '【' in _ and '】' in _:
      regex=re.compile('(?<=【).*(?=】)|(?<=】).*')
      return regex.findall(_)                         #一旦出错便会终止
    else:
      return ['',_]
