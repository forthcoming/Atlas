#coding: utf-8
import json,logging,os
from pymongo import MongoClient,ASCENDING
from pymongo.errors import CursorNotFound
from common.lshash import LSHash
from datetime import datetime
from multiprocessing import Process,cpu_count
from common.common import Log
from settings import MONGO_URI,MONGO_ATLAS,MACHINE_ID

def image_match(db,category,supply,retail,dis=4):
    logging.info('category:{} supply:{} retail:{}'.format(category,supply,retail))

    match_supply='match_{}'.format(supply)
    match_retail='match_{}'.format(retail)
    filters1_new={'$or':[{match_retail:False},{match_retail:{'$exists': False}}]}
    filters2_all={}
    filters1_old={match_retail:True}
    filters2_new={'$or':[{match_supply:False},{match_supply:{'$exists': False}}]}

    t1=datetime.now()
    _image_match(db,category,supply,retail,filters1_new,filters2_all,dis)
    t2=datetime.now()
    logging.info('filters1_new compare filters2_all cost {} seconds'.format(t2-t1))
    if supply!=retail:
        _image_match(db,category,supply,retail,filters1_old,filters2_new,dis)
    logging.info('filters1_old compare filters2_new cost {} seconds'.format(datetime.now()-t2))
    db['image_phash_{}_{}'.format(category,supply)].update_many(filters1_new,{"$set":{match_retail:True}})
    db['image_phash_{}_{}'.format(category,retail)].update_many(filters2_new,{"$set":{match_supply:True}})

def _image_match(db,category,supply,retail,filters1,filters2,dis): # filters1:supply,filters2:retail
    fields={'system_id':1,'imageurl':1,'phash':1,'_id':0}
    cursor1=db['image_phash_{}_{}'.format(category,supply)].find(filters1,fields)
    cursor2=db['image_phash_{}_{}'.format(category,retail)].find(filters2,fields)
    count1=cursor1.count()
    count2=cursor2.count()

    if count1 and count2:  # more efficient
        lsh = LSHash(16, 16)
        cpu=cpu_count()
        
        if count1<=count2:
            for each in cursor2:
                lsh.index(LSHash.hex_to_dec(each['phash']),extra_data=json.dumps(each))
            step=(count1//cpu)+1
            filters=filters1
            ends=count1
        else:
            for each in cursor1:
                lsh.index(LSHash.hex_to_dec(each['phash']),extra_data=json.dumps(each))
            step=(count2//cpu)+1
            filters=filters2
            ends=count2

        # for offset in range(0,ends,step):
        #     pid=os.fork()
        #     if pid==0:
        #         task(offset,step,lsh,category,supply,retail,filters,dis)
        #         os._exit(0)
        #     elif pid<0:
        #         logging.error('创建子程序失败')   
        # for i in range(cpu):  # 必须阻塞,否则会执行完image_match,成为孤儿进程
        #     os.waitpid(0,0)  # 在Manager中会出错
        processes=[Process(target=task, args=(offset,step,lsh,category,supply,retail,filters,dis)) for offset in range(0,ends,step)]
        for process in processes:
            process.start()
        for process in processes:  # 防止出现僵尸进程
            process.join()

def task(offset,step,lsh,category,supply,retail,filters,dis): 
    '''
    flag means supply or retail,status means new or old
    http://api.mongodb.com/python/current/faq.html#using-pymongo-with-multiprocessing
    PyMongo is not fork-safe. Care must be taken when using instances of MongoClient with fork().
    Specifically, instances of MongoClient must not be copied from a parent process to a child process. 
    Instead, the parent process and each child process must create their own instances of MongoClient. 
    Instances of MongoClient copied from the parent process have a high probability of deadlock in the child process due to the inherent incompatibilities between fork(), threads, and locks described below. 
    PyMongo will attempt to issue a warning if there is a chance of this deadlock occurring.
    '''       
    match_supply='match_{}'.format(supply)
    match_retail='match_{}'.format(retail)
    if filters and ((match_retail in filters) or (match_retail in filters['$or'][0])):
        flag=True
    else:
        flag=False
    if '$or' in filters:
        status=True
    else:
        status=False

    client=MongoClient(MONGO_URI) 
    db=client[MONGO_ATLAS]
    match_relation=match_retail if flag else match_supply
    source=db['image_phash_{}_{}'.format(category,supply if flag else retail)]
    target=db['image_match_result_{}'.format(category)]
    
    loop = 10
    while loop:
        if not flag:
            supply,retail=retail,supply
        # 由于前面的子进程已经开始,有可能使后面进程中游标数据比期望值要小,但不影响整个逻辑
        cursor = source.find(filters,{'system_id':1,'imageurl':1,'phash':1,'_id':1}).sort([('_id',ASCENDING)]).skip(offset).limit(step)
        try:
            for each in cursor:
                logging.info('flag:{} status:{} system_id:{}'.format(flag,status,each['system_id']))
                results=lsh.query(LSHash.hex_to_dec(each['phash']),distance_func='hamming',dis=dis)
                for result in results:
                    extra_data=json.loads(result[0][1])
                    if each['system_id']!=extra_data['system_id']: # The same product under the same platform dont product match pair(just compare system_id)
                        _={
                            'hash_diff':result[1],
                            'added_to_item_match':False,
                            'b_id':each['system_id'],
                            'b_platform':supply,
                            'b_image_url':each['imageurl'],
                            'c_id':extra_data['system_id'],
                            'c_platform':retail,
                            'c_image_url':extra_data['imageurl'],
                        }
                        if _['b_id']>_['c_id']:  # 按指定顺序存储
                            _['b_id'],_['c_id']=_['c_id'],_['b_id']
                            _['b_platform'],_['c_platform']=_['c_platform'],_['b_platform']
                            _['b_image_url'],_['c_image_url']=_['c_image_url'],_['b_image_url']
                        target.update_one({'b_id': _['b_id'],'c_id':_['c_id']},{'$setOnInsert':_},upsert=True)
                if status:
                    source.update_one({'_id':each['_id']},{"$set":{match_relation:True}})
                offset+=1
                step-=1
            break
        except CursorNotFound:
            loop-=1
    else:
        logging.error('unkonwn error found category:{} flag:{} filters:{}'.format(category,flag,filters))

@Log(level=logging.INFO,name='img_match.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    categories=db['category_info'].find({'machine_id':MACHINE_ID},{'sub_category':1,'max_diff':1,'name_en':1,'_id':0})
    for category in categories:
        platforms={sub_category['platform'] for sub_category in category['sub_category']}
        for supply in platforms:  # combinations function in itertools is also good
            for retail in platforms:
                image_match(db,category=category['name_en'],supply=supply,retail=retail,dis=category['max_diff'])
    client.close()

if __name__=='__main__':
    
    main(MONGO_URI,MONGO_ATLAS)
