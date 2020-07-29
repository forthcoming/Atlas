#coding: utf-8
from os import path
from pymongo import MongoClient
import os,logging,imagehash
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process,JoinableQueue  # Queue只能用于线程
from web_demo.common.common import init,img_download,Log
from PIL import Image

OFFSET=0b111111
PATH='/'.join(path.realpath(__file__).split('/')[:-3])+'/image/'

def scheduler(db,category):
    source=db['product_{}'.format(category)]
    task=JoinableQueue()
    
    for i in range(2):
        process=Process(target=consumer, args=(category,task),daemon=True)
        process.start()

    blacklist=['lazada','wish','11street']
    with ThreadPoolExecutor() as executor:
        for item in source.find({'platform':{'$nin':blacklist},'$or':[{'is_hash':False},{'is_hash':{'$exists': False}}]},{'platform':1,'_id':1,'image':1,'system_id':1}):
            executor.submit(producer,item,task,source) 
    task.join()
    # while task.qsize():  # bug
    #     time.sleep(60)

def consumer(category,task):
    client=MongoClient("mongodb://127.0.0.1:27017")
    db=client['test']
    source=db['product_{}'.format(category)]
    while True:
        item=task.get()  # (block=True, timeout=None)
        logging.info('category:{} qsize:{} _id:{}'.format(category,task.qsize(),item['_id']))
        target=db['image_phash_{}_{}'.format(category,item['platform'])]
       
        name=str(item['_id'])
        cat=PATH + str(int(name,16) & OFFSET)
        try:  # avoid defunct process
            for index,url in enumerate(item['image']):
                picture='{}/{}_{}'.format(cat,name,index)
                img=Image.open(picture)
                his=[cnt for cnt in img.convert('L').histogram() if cnt]
                if img.width>150 and img.height>150 and len(his)>6:
                    hash_code=imagehash.phash(img)
                    target.update_one({'imageurl':url},{'$setOnInsert': {'phash':str(hash_code),'system_id':item['system_id']}},upsert=True) # dont need to add imageurl into setOnInsert
                os.remove(picture)
            source.update_one({"_id":item['_id']},{"$set":{"is_hash":True}}) # Put here to prevent missing some phash generation failures
        except Exception as e:
            logging.error('error found in {},{}'.format(name,e))
        task.task_done()
        
def producer(item,task,source):
    logging.info('processing _id:{}'.format(item['_id']))
    urls=item['image']
    if not isinstance(urls,list):
        data=source.find_one_and_delete({"_id":item['_id']})
        logging.error('error found product_url:{} image:{}'.format(data.get('product_url',''),urls))
        return
    name=str(item['_id'])
    cat=PATH + str(int(name,16) & OFFSET)
    for index,url in enumerate(urls):
        if not img_download(url,cat,name,index):
            break
    else:
        task.put(item)

@Log(level=logging.INFO,name='imghash.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    init(db,OFFSET,PATH)
    categories=db['category_info'].find({'machine_id':1},{'name_en':1,'_id':0})
    for category in categories:
        scheduler(db,category=category['name_en'])
    client.close()

if __name__=='__main__':
    main("mongodb://127.0.0.1:27017",'test')
