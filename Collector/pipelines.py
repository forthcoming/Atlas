# -*- coding: utf-8 -*-
import json
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from Collector.items import *
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread
from Collector.utils import connection


class RedisPipeline(object):  #Thanks to scrapy-redis project on github !
  """Pushes serialized item into a redis list/queue"""

  def __init__(self, server):
    self.server = server
    self.encoder = ScrapyJSONEncoder()

  @classmethod
  def from_settings(cls, settings):
    server = connection.from_settings(settings)
    return cls(server)

  def process_item(self, item, spider):
    return deferToThread(self._process_item, item, spider)

  def _process_item(self, item, spider):
    key = "{}:items".format(spider.name)    #此处可以自定义item_key的名字
    data = self.encoder.encode(item)
    self.server.rpush(key, data)
    return item


class SqlPipeline(object):

  def __init__(self, path):
    self.path = path

  @classmethod
  def from_settings(cls, settings):  #获取settings中的设置
    path=settings.get('DATAPATH', './')
    return cls(path)

  def open_spider(self,spider):
    self._={TweetItem:'tweet',AttitudeItem:'attitude',RelayItem:'relay',CommentItem:'comment',}
    self.f=open('{}{}.sql'.format(self.path,spider.name),'w',encoding='utf-8')

  def process_item(self, item, spider):
    table=self._.get(item.__class__,'init')
    fields=','.join(item.keys())
    values="','".join((str(_) for _ in item.values()))  #join只适用于都是字符串的情形
    sql="insert into {}({}) values('{}');\n".format(table,fields,values)
    #sql="insert into {0}({1}) values('{2}');\n".format(table,fields,values)
    #sql="insert into {table}({fields}) values('{values}');\n".format(table=table,fields=fields,values=values)
    self.f.write(sql)
    return item

  def close_spider(self, spider):
    self.f.write('commit;')
    self.f.close()

class JsonPipeline(object):

  def __init__(self, path):
    self.path = path

  @classmethod
  def from_settings(cls, settings):
    path = settings.get('DATAPATH', './')
    return cls(path)
  
  '''  
  @classmethod
  def from_crawler(cls, crawler):
    settings=crawler.settings
    path = settings.get('DATAPATH', './')
    return cls(path)
  '''
  
  def open_spider(self,spider):
    self.f=open('{}{}.json'.format(self.path,spider.name),'w',encoding='utf-8')

  def process_item(self, item, spider):
    #self.f.write('{}\n'.format(json.dumps(dict(item),ensure_ascii=False)))
    #self.f.write('{}\n'.format(dict(item)))
    self.f.write('{}\n'.format(json.dumps(dict(item))))  #使用时只需要json.loads即可,你不需要转码
    return item

class MyRedisPipeline(object):
  def process_item(self, item, spider):
    item["name"] = 'master'
    return item


class ImagePipeline(ImagesPipeline):

  @classmethod
  def from_settings(cls, settings):
    s3store = cls.STORE_SCHEMES['s3']
    s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
    s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
    store_uri = settings.get('PHOTOPATH','./')     #watch it !!!!!!
    return cls(store_uri, settings=settings)

  def get_media_requests(self,item,info):
    #return [Request(x) for x in item.get('my_image_urls', [])]
    for image_url in item['my_image_urls']:
      yield Request(image_url)

  def file_path(self, request, response=None, info=None):
    '''
    image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
    return 'full/%s.jpg' % (image_guid)
    '''
    image_guid = request.url.split('/')[-1]
    return 'full/{}'.format(image_guid)

  def thumb_path(self, request, thumb_id, response=None, info=None):
    '''
    thumb_guid = hashlib.sha1(url).hexdigest()  # change to request.url after deprecation
    return 'thumbs/%s/%s.jpg' % (thumb_id, thumb_guid)
    '''
    image_guid = thumb_id + response.url.split('/')[-1]
    return 'thumbs/{}/{}'.format(thumb_id, image_guid)

  '''
  def item_completed(self,results,item,info):    #每完成一个item，调用一次
    for _ in results:
      print(_[0])   #True or False
      print(_[1]['url'])
      print(_[1]['path'])
      print(_[1]['checksum'])
  '''

