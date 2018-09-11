from pymongo import MongoClient
from datetime import datetime
import logging
from common.common import Log
from settings import MONGO_URI,MONGO_ATLAS,MACHINE_ID
from concurrent.futures import ThreadPoolExecutor

def scheduler(db,category):
    logging.info('category:{}'.format(category))
    product=db['product_{}'.format(category)]
    source=db['image_match_result_{}'.format(category)]
    target=db['item_match_result_{}'.format(category)]
    cursor=source.find(
        {'robot_match':True,'$or':[{'added_to_item_match':{'$exists':False}},{'added_to_item_match':False}]}, 
        {'added_to_item_match':0}
    ).limit(80000)
    result={}
    for item in cursor:

        key='{}:{}'.format(item['b_id'],item['c_id'])
        if key in result:
            result[key]['match_num']+=1
            result[key]['_ids'].append(item['_id'])
            if item['hash_diff']<result[key]['hash_diff']:
                result[key]['hash_diff']=item['hash_diff']
                result[key]['b_image_url']=item['b_image_url']
                result[key]['c_image_url']=item['c_image_url']      
        else:
            result[key]={
                'match_num':1,
                'hash_diff':item['hash_diff'],
                'b_image_url':item['b_image_url'],
                'b_platform':item['b_platform'],
                'c_image_url':item['c_image_url'],
                'c_platform':item['c_platform'],
                '_ids':[item['_id']]
            }
    with ThreadPoolExecutor() as executor:
        for key in result:
            executor.submit(finalize,product,source,target,key,result[key])

def finalize(product,source,target,key,value):
    updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    b_id,c_id=key.split(':')
    logging.info('b_id:{} c_id:{}'.format(b_id,c_id))
    _ids=value.pop('_ids')
    data=target.find_one({'$or':[{'b_id':b_id,'c_id':c_id},{'b_id':c_id,'c_id':b_id}]},{'match_num':1,'hash_diff':1,'_id':1})
    if not data:
        value.update({
            'b_id':b_id,
            'c_id':c_id,
            'sim_score':value['hash_diff']/value['match_num'],
            'b_url':product.find_one({'system_id':b_id},{'_id':0,'product_url':1}).get('product_url',''),
            'c_url':product.find_one({'system_id':c_id},{'_id':0,'product_url':1}).get('product_url',''),
            'human_processed':False,
            'human_match':0,
            'added_to_cluster':False,
            'updated_at':updated_at,
            'oa_user_id':'',
            'oa_user_name':'',
        })
        target.insert_one(value)
    else:
        _value={
            'hash_diff':min(value['hash_diff'],data['hash_diff']),
            'match_num':value['match_num']+data['match_num'],
            'updated_at':updated_at,
            'b_id':b_id,
            'c_id':c_id,
            'b_image_url':value['b_image_url'],       
            'c_image_url':value['c_image_url'],     
            'b_platform':value['b_platform'],   
            'c_platform':value['c_platform'],   
            'b_url':product.find_one({'system_id':b_id},{'_id':0,'product_url':1}).get('product_url',''),
            'c_url':product.find_one({'system_id':c_id},{'_id':0,'product_url':1}).get('product_url',''),
        }
        _value['sim_score']=_value['hash_diff']/_value['match_num']
        target.update_one({'_id':data['_id']},{"$set":_value})
    source.update_many({'_id':{'$in':_ids}},{"$set":{'added_to_item_match':True}})


@Log(level=logging.INFO,name='item_match.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    categories=db['category_info'].find({'machine_id':MACHINE_ID},{'name_en':1,'_id':0})
    for category in categories:
        scheduler(db,category=category['name_en'])
    client.close()

if __name__=='__main__':
    main(MONGO_URI,MONGO_ATLAS)