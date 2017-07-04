# -*- coding: utf-8 -*-
import json
from scrapy.exceptions import DropItem
from Collector.items import *

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
