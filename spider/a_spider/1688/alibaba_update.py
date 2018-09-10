# -*-coding=utf-8-*-
# time 2018-8-24-15:28
# add function to update the date which is ignored by spider#
from atlas.config.settings import *
import pymongo
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 全局参数
# @AMOUNT_PER_TIME 限定每次运行更新的数量
AMOUNT_PER_TIME = 10000000


def query_data(database, category, kw, dt):
    # dt = (datetime.datetime.now() - datetime.timedelta(DAYS_BEFORE)).strftime('%Y-%m-%d')
    collection_name = 'product_{}'.format(category)
    _db = database.get_db
    course = _db[collection_name].find(
        {'$and': [{'platform': '1688'}, {'keywords': kw},
                  {'$or': [{'update_at': {'$exists': False}}, {'update_at': {'$lt': dt}}]}]}).limit(AMOUNT_PER_TIME)
    product_id_list = []
    for item in course:
        product_id_list.append(item.get('product_id', ''))

    return product_id_list, category, kw


if __name__ == '__main__':
    print '======='
    db = pymongo.MongoClient(MONGO_URI)[MONGO_ATLAS]
    print db
    for item1, item2, item3 in query_data(db, 'jewellery', u'项饰'):
        print item1, item2, item3
        # break
    print '------------'
    print (datetime.datetime.now()-datetime.timedelta(days=60)).strftime('%Y-%m-%d')




