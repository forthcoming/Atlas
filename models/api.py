# -*- coding: utf-8 -*-  
from pymongo import MongoClient,ASCENDING
from datetime import datetime
from flask import Flask,request,jsonify
from atlas.models.tool.graph import Graph
from atlas.models.tool.common import on_off_sale,check
from settings import MONGO_URI,MONGO_ATLAS,MONGO_BI

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/cluster/disassociation",methods=['POST'])
def split_cluster(): # to is to be deleted
    params=request.form
    _category=params.get('category')
    come=params.get('come')
    to=params.get('to')
    try:  
        client=MongoClient(MONGO_URI)
        atlas=client[MONGO_ATLAS]
        if _category.isdigit():
            category=atlas['category_info'].find_one({'sub_category.source':'erp','sub_category.keyword':int(_category)},{'_id':0,'name_en':1})['name_en']
        else:     
            category=_category
        edge=atlas['cluster_edge_{}'.format(category)]
        node=atlas['cluster_node_{}'.format(category)]
        cluster_id=node.find_one({'system_id':to},{'cluster_id':1,'_id':0})['cluster_id']   
        system_ids=[each['system_id'] for each in node.find({'cluster_id':cluster_id},{'system_id':1,'_id':0})]
        graph=Graph(kind='DG')
        # for each in edge.find({'is_effective':True,'from_node_id':{'$in':system_ids}},{'from_node_id':1,'to_node_id':1,'_id':0}):
        for each in edge.find({'is_effective':True,'$or':[{'from_node_id':{'$in':system_ids}},{'to_node_id':{'$in':system_ids}}]},{'from_node_id':1,'to_node_id':1,'_id':0}):
            graph.add(each['from_node_id'],each['to_node_id'])
        for vertex in graph.get_vertices(come,to): 
            edge.update_one({'from_node_id':vertex,'to_node_id':to},{'$set':{'is_effective':False}})
            edge.update_one({'from_node_id':to,'to_node_id':vertex},{'$set':{'is_effective':False}})
            graph.delete(vertex,to)
            graph.delete(to,vertex)

        vertices=graph.BFS(to)
        serial_num=node.find({'system_id':{'$in':vertices}},{'serial_num':1,'_id':0}).sort('serial_num').limit(1)
        serial_num=next(serial_num)['serial_num']
        if serial_num!=cluster_id:
            node.update_many({'system_id':{'$in':vertices}},{'$set':{'cluster_id':serial_num,'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}})
            check(node,serial_num)
        else:
            system_ids=list(set(system_ids)-set(vertices))
            serial_num=node.find({'system_id':{'$in':system_ids}},{'serial_num':1,'_id':0}).sort('serial_num').limit(1)
            serial_num=next(serial_num)['serial_num']
            node.update_many({'system_id':{'$in':system_ids}},{'$set':{'cluster_id':serial_num,'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}})
            check(node,serial_num)
        check(node,cluster_id)
        client.close()
        return jsonify({
            "code" : 0,
            "msg" : 'success',
            "result" : ''
        })
    except Exception as e:
        return jsonify({
            "code" : 1,
            "msg" : str(e),
            "result" : ''
        })

@app.route("/product/offsale",methods=['POST'])
def off_sale():
    params=request.form
    system_id=params.get('system_id')
    _category=params.get('category')
    try:
        client=MongoClient(MONGO_URI)
        atlas=client[MONGO_ATLAS]
        if _category.isdigit():
            category=atlas['category_info'].find_one({'sub_category.source':'erp','sub_category.keyword':int(_category)},{'_id':0,'name_en':1})['name_en']
        else:     
            category=_category
        node=atlas['cluster_node_{}'.format(category)]
        on_off_sale(node,system_id,False)
        return jsonify({
            "code" : 0,
            "msg" : 'success',
            "result" : ''
        })
    except Exception as e:
        return jsonify({
            "code" : 1,
            "msg" : str(e),
            "result" : ''
        })

@app.route("/select",methods=['GET','POST'])
def select():
    if request.method=='GET':
        params=request.args
    else:
        params=request.form
    category=params.get('category')
    product_id=params.get('product_id')
    try:
        client=MongoClient(MONGO_URI)
        atlas=client[MONGO_ATLAS]
        source=atlas['product_{}'.format(category)]
        target=atlas['cluster_node_{}'.format(category)]
        result=source.find_one({'product_id':product_id},{'_id':0,'platform':1})
        system_id='{}_{}'.format(result['platform'],product_id)
        result=target.find_one({'system_id':system_id},{'_id':0,'cluster_id':1})
        cluster_id=result['cluster_id']
        data=[]
        for each in target.find({'cluster_id':cluster_id},{'_id':0,'system_id':1}):
            _=source.find_one(each)
            _.pop('_id','')  # pay attention
            data.append(_)     
        return jsonify({
            "code": 1,
            "msg": 'Success',
            "result": data
        })
    except Exception as e:
        return jsonify({
            "code" : 1,
            "msg" : str(e),
            "result" : ''
        })

if __name__=='__main__':
    app.run(
        host = '0.0.0.0',
        port = 8080
    )
    
    '''
    import requests
    data={
        'category':'digital_office',
        'product_id':'540554959138',
    }
    r=requests.post('http://localhost:5000/select',data=data)
    print(r.json())
    '''
