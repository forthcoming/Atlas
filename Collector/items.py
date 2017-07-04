# -*- coding: utf-8 -*-
from scrapy import Item,Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join,MapCompose,TakeFirst


#微博内容
class TweetItem(Item):
  news_id =  Field() #微博主键
  title = Field() #微博标题
  content = Field() #微博内容
  publish_time = Field() #微博发布日期
  num_praise=Field()  #点赞量
  num_relay=Field()  #转发量
  num_comment=Field()  #评论量


#点赞
class AttitudeItem(Item):
  news_id = Field() #微博主键
  user_id = Field() #点赞人ID
  praise_date = Field() #点赞日期

#转发
class RelayItem(Item):
  news_id = Field()     #主键
  user_id = Field()     #转发人ID
  relays = Field()      #评论内容
  num_praise=Field()    #被点赞数
  relay_date = Field()  #发布日期

#评论内容
class CommentItem(Item):
  news_id = Field() #微博主键
  comment_id = Field() #评论主键
  comments = Field() #评论内容
  user_id = Field() #评论人ID
  comment_date = Field() #评论发布日期
  num_attitude=Field()    #评论被点赞数

class JobItem(Item):
  name = Field() #职位名称
  catalog = Field() #职位类别
  workLocation = Field() #工作地点
  recruitNumber = Field() #职位所需人数
  datailLink = Field() #职位详情页连接
  publishTime = Field() #发布时间

class PhoneItem(Item):
  customer_id=Field()
  customer_name=Field()
  customer_register=Field()
  customer_lv=Field()
  customer_type=Field()

  battery_score=Field()
  screen_score=Field()
  photo_score=Field()
  video_entertainment_score=Field()
  appearance_score=Field()
  cost_performance_score=Field()
  fluency_score=Field()
  stability_score=Field()
  heat_score=Field()
  brand_score=Field()
  integration_valuation_score=Field()

  url=Field()
  title=Field()
  publish_date=Field()
  series=Field()
  product_name=Field()
  product_type=Field()
  product_id=Field()
  post_id=Field()
  comment_id=Field()
  thread_id=Field()
  evaluation_type=Field()
  evaluation=Field()

class OilItem(Item):
  placeName = Field()
  oilPrice = Field()
  oilType = Field()
  priceType = Field()
  district = Field()

  key_name=Field()      #yuan you ming
  s_type=Field()        #qi huo/xian huo
  price_y=Field()       #jia ge
  s_remark=Field()      #bei zhu

class OilItemLoader(ItemLoader):
  default_item_class=OilItem
  default_input_processor=MapCompose(lambda x:x+'Yeah')
  default_output_processor=TakeFirst() #只有字段没自定义processor时，才会调用默认的processor
  s_type_in=MapCompose(lambda s:s.upper())
  key_name_in=MapCompose(lambda x:x+'Avatar')
  key_name_out=Join()   #只有以_in和_out且名字跟上面类的成员名一样才有用
