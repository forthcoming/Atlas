# -*- coding: utf-8 -*-  
from pymongo import MongoClient
from datetime import datetime
import logging,time
from common.common import Log
from settings import MONGO_URI,MONGO_ATLAS,MACHINE_ID
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.dummy import Lock 

def item_match(db,category):
    logging.info('category:{}'.format(category))
    product=db['product_{}'.format(category)]
    source=db['image_match_result_{}'.format(category)]
    target=db['item_match_result_{}'.format(category)]
    pipeline=[
        {
            '$match':{'robot_match':True,'$or':[{'added_to_item_match':{'$exists':False}},{'added_to_item_match':False}]}
        },
        {
            '$limit': 50000
        },    
        {    
            # The aggregation pipeline can determine if it requires only a subset of the fields in the documents to obtain the results. 
            # If so, the pipeline will only use those required fields, reducing the amount of data passing through the pipeline.
            '$project':{'_id':1,'b_id':1,'c_id':1,'hash_diff':1,'b_image_url':1,'b_platform':1,'c_image_url':1,'c_platform':1}
        },
        {
            '$group':{
                '_id':{'b_id':"$b_id",'c_id':"$c_id"},
                'match_num':{'$sum':1},
                'hash_diff':{'$min':'$hash_diff'},
                'b_image_url':{'$first':'$b_image_url'},
                'b_platform':{'$first':'$b_platform'},
                'c_image_url':{'$last':'$c_image_url'},
                'c_platform':{'$last':'$c_platform'},
                'keys':{'$push':'$_id'},    
            }
        },
        {    
            # 会基于最近一个$project或者$group字段进行映射
            '$project':{'_id':0,'keys':1,'b_id':'$_id.b_id','c_id':'$_id.c_id','match_num':1,'hash_diff':1,'b_image_url':1,'b_platform':1,'c_image_url':1,'c_platform':1,'sim_score':{'$divide':['$hash_diff','$match_num']}}
        },        
    ]
    mutex=Lock()
    tasks_id=set()
    with ThreadPoolExecutor() as executor:
        for item in source.aggregate(pipeline,allowDiskUse=True):
            executor.submit(task,product,source,target,item,mutex,tasks_id)

def task(product,source,target,item,mutex,tasks_id):
    b_id=item['b_id']
    c_id=item['c_id']
    logging.info('b_id:{} c_id:{}'.format(b_id,b_id))

    '''
    flag='{}{}'.format(b_id,c_id)
    _flag='{}{}'.format(c_id,b_id)
    with mutex:  # 也可以针对数据操作部分加锁,但速度会变慢(基本变成多线程串行),由于b_id,c_id已按照指定顺序排序,此处不需要再用锁
        while True:
            if _flag in tasks_id:
                time.sleep(.05)
            else:
                tasks_id.add(flag)  # flag mustn't exist in _id
                break
    '''

    updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    data=target.find_one({'b_id':b_id,'c_id':c_id},{'match_num':1,'hash_diff':1,'_id':1})
    if not data:
        result={
            'b_id':b_id,
            'c_id':c_id,
            'match_num':item['match_num'],
            'hash_diff':item['hash_diff'],
            'b_image_url':item['b_image_url'],
            'b_platform':item['b_platform'],
            'c_image_url':item['c_image_url'],
            'c_platform':item['c_platform'],            
            'sim_score':item['sim_score'],            
            'b_url':product.find_one({'system_id':b_id},{'_id':0,'product_url':1}).get('product_url',''),
            'c_url':product.find_one({'system_id':c_id},{'_id':0,'product_url':1}).get('product_url',''),
            'human_processed':False,
            'human_match':0,
            'added_to_cluster':False,
            'updated_at':updated_at,
            'oa_user_id':'',
            'oa_user_name':'',
        }
        target.insert_one(result)
    else:
        result={
            'hash_diff':min(item['hash_diff'],data['hash_diff']),
            'match_num':item['match_num']+data['match_num'],
            'updated_at':updated_at        
        }
        result['sim_score']=result['hash_diff']/result['match_num']
        target.update_one({'_id':data['_id']},{"$set":result})
    source.update_many({'_id':{'$in':item['keys']}},{"$set":{'added_to_item_match':True}})

    # tasks_id.remove(flag)


@Log(level=logging.INFO,name='item_match.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    categories=db['category_info'].find({'machine_id':MACHINE_ID},{'name_en':1,'_id':0})
    for category in categories:
        item_match(db,category=category['name_en'])
    client.close()

if __name__=='__main__':
    main(MONGO_URI,MONGO_ATLAS)