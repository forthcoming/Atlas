from datetime import datetime
from pymongo import HASHED,ASCENDING,IndexModel
import os

def check(node,cluster_id):
    if node.find_one({'cluster_id':cluster_id,'on_sale':True}):
        data=node.find({'cluster_id':cluster_id,'on_sale':True},{'serial_num':1,'_id':0}).sort([('serial_num',1)]).limit(1)
        node.update_many({'cluster_id':cluster_id},{'$set':{'cluster_id':next(data)['serial_num']}})

def on_off_sale(node,system_id,status): 
    assert isinstance(status,bool)    
    data=node.find_one_and_update({'system_id':system_id},{'$set':{'on_sale':status,'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}},projection={'cluster_id':1,'_id':0})
    cluster_id=data['cluster_id'] if data else 0  # system_id may not exists
    check(node,cluster_id)

def init(db,offset,path):
    os.makedirs(path,exist_ok=True)
    os.chdir(path)
    for cat in range(offset+1):
        cat = str(cat)
        if not os.path.exists(cat):
            os.mkdir(cat)
        elif not os.path.isdir(cat):
            os.remove(cat)
            os.mkdir(cat)
    db.counters.update_one({'_id':'serial_num'},{'$setOnInsert': {'seq':.0}},upsert=True)
    for name_en in db['category_info'].distinct('name_en'):
        db['product_{}'.format(name_en)].create_indexes([IndexModel([("system_id", HASHED)]), IndexModel([("product_id", ASCENDING)])])
        db['image_match_result_{}'.format(name_en)].create_index([('b_id',ASCENDING),('c_id',ASCENDING)])  # For a compound index on the key 'mike' descending and 'eliot' ascending we need to use a list of tuples
        db['item_match_result_{}'.format(name_en)].create_indexes([IndexModel([('human_processed',ASCENDING)]),IndexModel([('human_match',ASCENDING)]), IndexModel([('human_processed',ASCENDING),('human_match',ASCENDING)])])
        db['cluster_node_{}'.format(name_en)].create_indexes([IndexModel([("cluster_id", HASHED)]), IndexModel([("system_id", HASHED)])])
        for platform in db['category_info'].distinct('sub_category.platform',{'name_en':name_en}):
            db['image_phash_{}_{}'.format(name_en,platform)].create_index([('imageurl',HASHED)])
