import logging
from pymongo import MongoClient
from datetime import datetime
from tool.common import check
from atlas.log.log import Log
from atlas.config.settings import MONGO_URI,MONGO_ATLAS,MACHINE_ID

def cluster_edge(db,category):
    edge=db['cluster_edge_{}'.format(category)]
    node=db['cluster_node_{}'.format(category)]
    counters=db['counters']
    source=db['item_match_result_{}'.format(category)]
    updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')     

    for each in source.find({"human_processed":True,'human_match':1,'$or':[{"added_to_cluster":False},{"added_to_cluster":{'$exists': False}}]},{'b_id':1,'c_id':1,'_id':1}):
        b_id=each['b_id']
        c_id=each['c_id']
        logging.info('b_id:{} c_id:{}'.format(b_id,c_id))
        data=node.find_one({'system_id':b_id},{'_id':0,'cluster_id':1}) # dict or None
        b_cluster_id=data['cluster_id'] if data else 0
        data=node.find_one({'system_id':c_id},{'_id':0,'cluster_id':1})
        c_cluster_id=data['cluster_id'] if data else 0
        if not(b_cluster_id or c_cluster_id):  # both false
            cluster_id=counters.find_one_and_update({'_id':'serial_num'},{ "$inc": {'seq': 1}},return_document=True)['seq']
            serial_num=counters.find_one_and_update({'_id':'serial_num'},{ "$inc": {'seq': 1}},return_document=True)['seq']
            # assert isinstance(serial_num,(int,float))
            node.insert_many([
                {'on_sale':True,'system_id':b_id,'cluster_id':cluster_id,'serial_num':cluster_id,'updated_at':updated_at},
                {'on_sale':True,'system_id':c_id,'cluster_id':cluster_id,'serial_num':serial_num,'updated_at':updated_at},
            ])
        elif not b_cluster_id:
            serial_num=counters.find_one_and_update({'_id':'serial_num'},{ "$inc": {'seq': 1}},return_document=True)['seq']
            # assert isinstance(serial_num,(int,float))
            node.insert_one({'on_sale':True,'system_id':b_id,'cluster_id':c_cluster_id,'serial_num':serial_num,'updated_at':updated_at})
            check(node,c_cluster_id)
        elif not c_cluster_id:
            serial_num=counters.find_one_and_update({'_id':'serial_num'},{ "$inc": {'seq': 1}},return_document=True)['seq']
            # assert isinstance(serial_num,(int,float))
            node.insert_one({'on_sale':True,'system_id':c_id,'cluster_id':b_cluster_id,'serial_num':serial_num,'updated_at':updated_at})
            check(node,b_cluster_id)
        elif b_cluster_id!=c_cluster_id:
            if b_cluster_id>c_cluster_id:
                b_cluster_id,c_cluster_id=c_cluster_id,b_cluster_id
            node.update_many({'on_sale':True,'cluster_id':c_cluster_id},{'$set':{'cluster_id':b_cluster_id}})
            check(node,b_cluster_id)
        else:
            check(node,b_cluster_id)  # to ensure atomic operation
            logging.info('{} and {} are in the same cluster'.format(b_id,c_id)) 
        edge.update_one({'from_node_id':b_id,'to_node_id':c_id,'is_effective':True},{'$setOnInsert':{'updated_at':updated_at}},upsert=True)                          
        edge.update_one({'from_node_id':c_id,'to_node_id':b_id,'is_effective':True},{'$setOnInsert':{'updated_at':updated_at}},upsert=True)
        source.update_one({'_id':each['_id']},{"$set":{'added_to_cluster':True}})

@Log(level=logging.INFO,name='cluster_add.log')
def main(uri,database):
    client=MongoClient(uri)
    db=client[database]
    categories=db['category_info'].find({'machine_id':MACHINE_ID},{'name_en':1,'_id':0})
    for category in categories:
        cluster_edge(db,category=category['name_en'])
    client.close()

if __name__=='__main__':
    main(MONGO_URI,MONGO_ATLAS)
