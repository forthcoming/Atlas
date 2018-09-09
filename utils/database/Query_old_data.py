import sys
import time
import Queue
import datetime
from bson import ObjectId
from pymongo import MongoClient
sys.path.append('../..')
from log.log import Log
from config.settings import *
reload(sys)
sys.setdefaultencoding('utf-8')

queue = Queue.Queue()

db_client = MONGO_URI
db_database = MONGO_ATLAS
client = MongoClient(db_client)
db_client = client[db_database]
db_set = db_client[MONGO_SET]

result = db_set.find()

# d = info.find_one({'_id':ObjectId('577d211b1d41c8303f73cf7d')})
# print d


def object_id_from_datetime(from_datetime=None, span_days=0, span_hours=0, span_minutes=0,
                            span_seconds=0, span_weeks=0):
    '''根据时间手动生成一个objectid，此id不作为存储使用'''
    if not from_datetime:
        from_datetime = datetime.datetime.now()
        # print from_datetime
    from_datetime = from_datetime + datetime.timedelta(days=span_days, hours=span_hours, minutes=span_minutes, weeks=span_weeks)
    # print from_datetime
    return ObjectId.from_datetime(generation_time=from_datetime)


def get_id():
    result = db_set.find({'machine_id': MACHINE_ID})
    for item in result:
        name_en = item['name_en']
        objid_time_to = object_id_from_datetime(span_days=0)

        set_name = "product_%s" % name_en.encode('utf-8')
        print set_name

        cursor = db_client[set_name].find(
            {
                '_id': {'$lt': ObjectId(objid_time_to)},
                'platform': "taobao"
            },
            {
                'product_id': 1,
                'keywords': 1,
            },
        )
        p_id_big_li = []
        for i in cursor:
            i.pop('_id')
            print i.get('product_id')
            kw = i.get('keywords')
            p_id_big_li.append(i.get('product_id'))
            queue.put((name_en, kw, p_id_big_li))
        # print queue.qsize()



# db.history_taobao_digital_office.aggregate(
#     {$group:
#         {
#             _id:'$system_id',
#             counter:{$sum:1},
#         }
#     },
#     {
#         $match:{counter:{$gt:14}}
#     }
# ).count()
def timestamp_from_objectid(objectid):
    result = 0
    try:
        result = time.mktime(objectid.generation_time.timetuple())
    except:
        pass
    return result


if __name__ == '__main__':
    st = time.time()
    get_id()
    print time.time()-st
    # timestamp = (timestamp_from_objectid(ObjectId('5b1e6a7a21fed62f2af7ade3')))
    # #转换成localtime
    # time_local = time.localtime(timestamp)
    # #转换成新的时间格式(2016-05-05 20:28:54)
    # dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    #
    # print dt
