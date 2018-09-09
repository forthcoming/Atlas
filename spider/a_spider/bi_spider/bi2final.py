# coding=utf-8
from pymongo import MongoClient,HASHED,ASCENDING,DESCENDING
from datetime import datetime
from atlas.config.settings import MONGO_URI,MONGO_BI

def sync():
    client=MongoClient(MONGO_URI)
    bi=client[MONGO_BI]
    source=bi['product_bi']
    target=bi['product_bi_final']
    category=bi['category']
    source.create_index([("category_id",ASCENDING)])
    source.create_index([("ps_product_sn",HASHED)])
    target.create_index([('goods_sn',HASHED)])
    target.create_index([('dw_web_id',ASCENDING)])
    target.create_index([('category_id',ASCENDING)])
    target.create_index([('score_type',ASCENDING)])
    target.create_index([('score_a', DESCENDING)])
    target.create_index([('supplier_num', ASCENDING)])
    target.create_index([('max_price', ASCENDING)])
    target.create_index([('min_price', ASCENDING)])
    target.create_index([('hash_url', ASCENDING)])

    for each in category.find({},{'category_id':1,'_id':0}):
        result=target.find({'category_id':each['category_id']},{"dw_etl_dt":1,'_id':0}).sort([('dw_etl_dt',-1)]).limit(1)
        try:
            last_time=next(result)['dw_etl_dt']
        except:
            last_time=datetime(1992,8,24)  
        for item in source.find({'category_id':each['category_id'],'goods_sn':{'$ne':None},'product_image':{'$type':'string'},"dw_etl_dt":{'$gte':last_time}},{'_id':0}).sort([('dw_etl_dt',ASCENDING)]):
            print('processing {}'.format(item['goods_sn']))
            target.update_one({'goods_sn':item['goods_sn'],'dw_web_id':item['dw_web_id']},{'$set':item},upsert=True)
    client.close()

if __name__=='__main__':
    sync()
