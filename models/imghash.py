#coding: utf-8
from pymongo import MongoClient
import requests,os,logging,imagehash
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process,JoinableQueue
from tool.common import init
from tool.imghdr import what
from PIL import Image
from atlas.log.log import Log
from atlas.config.settings import MONGO_URI,MONGO_ATLAS,MACHINE_ID,OFFSET,PATH

def scheduler(db,category):
    source=db['product_{}'.format(category)]
    task=JoinableQueue()
    
    for i in range(2):
        # process=Process(target=consumer, args=(category,task),daemon=True)  # py3
        process=Process(target=consumer, args=(category,task))  # py2
        process.daemon=True
        process.start()

    blacklist=['lazada','wish','11street']
    with ThreadPoolExecutor() as executor:
        for item in source.find({'platform':{'$nin':blacklist},'$or':[{'is_hash':False},{'is_hash':{'$exists': False}}]},{'platform':1,'_id':1,'image':1,'system_id':1}):
            executor.submit(producer,item,task,source) 
    task.join()
    # while task.qsize():  # bug
    #     time.sleep(60)

def consumer(category,task):
    client=MongoClient(MONGO_URI) 
    db=client[MONGO_ATLAS]
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

def producer(item,task,source,retry_times=5):
    logging.info('processing _id:{}'.format(item['_id']))
    urls=item['image']
    if not isinstance(urls,list):
        data=source.find_one_and_delete({"_id":item['_id']})
        logging.error('error found product_url:{} image:{}'.format(data.get('product_url',''),urls))
        return
    
    name=str(item['_id'])
    cat=PATH + str(int(name,16) & OFFSET)
    for index,url in enumerate(urls):
        picture='{}/{}_{}'.format(cat,name,index)
        if not os.path.exists(picture):
            for i in range(retry_times): 
                try:
                    res=requests.get(url,timeout=30,stream=True,verify=False)
                    chunk=next(res.iter_content(32))
                    if not what(chunk):
                        return
                    with open(picture,'wb') as f:
                        f.write(chunk)
                        for chunk in res.iter_content(chunk_size=1024):
                            f.write(chunk)
                    break
                except Exception as e:
                    logging.error('Error {} found in {},retry_times={}'.format(e,url,i))
            else:
                logging.error('{} download error'.format(url))
                break
    else:
        task.put(item)

@Log(level=logging.INFO,name='imghash.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    init(db,OFFSET,PATH)
    categories=db['category_info'].find({'machine_id':MACHINE_ID},{'name_en':1,'_id':0})
    for category in categories:
        scheduler(db,category=category['name_en'])
    client.close()

if __name__=='__main__':
    main(MONGO_URI,MONGO_ATLAS)
