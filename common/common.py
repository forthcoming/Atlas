import os,requests,logging
from datetime import datetime
from pymongo import HASHED,ASCENDING,IndexModel
from .imghdr import what
import networkx as nx
import matplotlib.pyplot as plt

class Log:
    def __init__(self,level=logging.NOTSET, name='track.log'):
        '''
        # 默认情况下日志打印到屏幕,日志级别为WARNING
        # 日志级别：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
        # logging.debug('this is debug info')
        # logging.info('this is information')
        # logging.warning('this is warning message')
        # logging.error('this is error message')
        # logging.critical('this is critical message')
        '''
        logging.basicConfig(
            filename=name,
            filemode='a',
            # format='%(asctime)s %(filename)s %(lineno)d %(process)s %(levelname)s %(module)s %(message)s',
            format='%(asctime)s line:%(lineno)d pid:%(process)s level:%(levelname)s message:%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S %p',
            level=level,
        )
        logging.root.name=__name__
    def __call__(self,f):
        def wrapper(*args):
            try:
                return f(*args)
            except Exception as e:
                logging.exception(e)
        return wrapper

# 最简单的方式是实例化一个类,然后在其他地方直接导入这个类实例即可实现单例
def singleton(cls):
    _instance = None
    def _singleton(*args, **kargs):
        nonlocal _instance
        if not _instance:
            _instance = cls(*args, **kargs)
        return _instance
    return _singleton
    
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

def show_cluster(db,category,cluster_id):
    G = nx.Graph()
    edge=db['cluster_edge_{}'.format(category)]
    node=db['cluster_node_{}'.format(category)]
    system_ids=[each['system_id'] for each in node.find({'cluster_id':cluster_id},{'system_id':1,'_id':0})]
    for each in edge.find({'is_effective':True,'from_node_id':{'$in':system_ids}},{'from_node_id':1,'to_node_id':1,'_id':0}):
        G.add_edge(each['from_node_id'],each['to_node_id'],weight=1)
    nx.draw(G, with_labels=True)
    plt.show()

def img_download(url,cat,name,index,retry_times=5):
    picture='{}/{}_{}'.format(cat,name,index)
    if not os.path.exists(picture):
        for i in range(retry_times): 
            try:
                res=requests.get(url,timeout=30,stream=True,verify=False)
                chunk=next(res.iter_content(32))
                if not what(chunk):
                    return False
                with open(picture,'wb') as f:
                    f.write(chunk)
                    for chunk in res.iter_content(chunk_size=1024):
                        f.write(chunk)
                return True
            except Exception as e:
                logging.error('Error {} found in {},retry_times={}'.format(e,url,i))
        else:
            logging.error('{} download error'.format(url))
            return False
    return True

if __name__=='__main__':
    @singleton
    class TestSingleton:pass
    x=TestSingleton()
    print(id(x) == id(TestSingleton()))  # True
