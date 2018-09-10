#!--coding=utf8--
from common.sift import compute
from pymongo import MongoClient
import os,logging,signal
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import JoinableQueue,cpu_count
from atlas.config.settings import MONGO_URI,MONGO_ATLAS,MACHINE_ID,OFFSET,PATH
from common.common import Log,img_download

def scheduler(db,category):
    task=JoinableQueue()
    for i in range(cpu_count()):
        pid=os.fork()
        if pid==0:
            consumer(category,task)
            os._exit(0)
        elif pid<0:
            logging.error('创建子进程失败')   

    with ThreadPoolExecutor() as executor:
        cursor = db['image_match_result_{}'.format(category)].find(
            {'$or': [{'robot_processed': False}, {'robot_processed': {'$exists': False}}]}, 
            {'_id': 1, 'b_image_url': 1, 'c_image_url': 1}
        )
        for item in cursor:
            item['mark']=True # 标错
            executor.submit(producer, item, task)
        cursor = db['item_match_result_{}'.format(category)].find(
            {'$or': [{'robot_processed': False}, {'robot_processed': {'$exists': False}}]}, 
            {'_id': 1, 'b_image_url': 1, 'c_image_url': 1}
        )
        for item in cursor:
            item['mark']=False # 标对
            executor.submit(producer, item, task)
    task.join()
    os.kill(0,signal.SIGKILL)

def consumer(category,task):
    client=MongoClient(MONGO_URI) 
    db=client[MONGO_ATLAS]
    while True:
        item=task.get()
        if item['mark']:
            target=db['image_match_result_{}'.format(category)]
            threshold=10
        else:
            target=db['item_match_result_{}'.format(category)]
            threshold=90
        logging.info('category:{} qsize:{} _id:{}'.format(category,task.qsize(),item['_id']))
        name=str(item['_id'])
        cat=PATH + str(int(name,16) & OFFSET)
        picture1='{}/{}_0'.format(cat,name)
        picture2='{}/{}_1'.format(cat,name)
        try:
            _rate, des_total, des_match = compute(picture1, picture2)
            rate=round(_rate*100)
            extra_data={
                'robot_processed':True,
                'robot_score':rate,
                'robot_match':rate>threshold,
                'robot_total_dot' : des_total,
                'robot_match_dot' : des_match
            }
            os.remove(picture1)
            os.remove(picture2)
            target.update_one({"_id":item['_id']},{"$set":extra_data})
        except Exception as e:
            logging.error('error found in {},{}'.format(name,e))
        task.task_done()

def producer(item,task):
    logging.info('processing _id:{}'.format(item['_id']))
    name=str(item['_id'])
    cat=PATH + str(int(name,16) & OFFSET)
    for index,url in enumerate([item['b_image_url'],item['c_image_url']]):
        if not img_download(url,cat,name,index):
            break
    else:
        task.put(item)

@Log(level=logging.INFO,name='robot.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    for category in db['category_info'].find({'machine_id':MACHINE_ID},{'name_en':1,'_id':0}):
        scheduler(db, category['name_en'])
    client.close()

if __name__=='__main__':
    main(MONGO_URI,MONGO_ATLAS)
