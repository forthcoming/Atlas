# -*- coding: utf-8 -*-  
from pymongo import MongoClient
from datetime import datetime
from flask import Flask,request,jsonify
from common.graph import Graph
from common.common import check

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/cluster/disassociation",methods=['POST'])
def split_cluster(): # to is to be deleted
    params=request.form
    category=params.get('category')
    come=params.get('come')
    to=params.get('to')
    try:  
        client=MongoClient('mongodb://127.0.0.1:27017')
        atlas=client['test']
        edge=atlas['cluster_edge_{}'.format(category)]
        node=atlas['cluster_node_{}'.format(category)]
        cluster_id=node.find_one({'system_id':to},{'cluster_id':1,'_id':0})['cluster_id']   
        system_ids=[each['system_id'] for each in node.find({'cluster_id':cluster_id},{'system_id':1,'_id':0})]
        graph=Graph(kind='UDG')
        for each in edge.find({'is_effective':True,'from_node_id':{'$in':system_ids}},{'from_node_id':1,'to_node_id':1,'_id':0}):
            graph.add(each['from_node_id'],each['to_node_id'])
        for vertex in graph.get_vertices(come,to): 
            edge.update_one({'from_node_id':min(vertex,to),'to_node_id':max(vertex,to)},{'$set':{'is_effective':False}})
            graph.delete(vertex,to)

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

@app.route("/select",methods=['GET','POST'])
def select():
    if request.method=='GET':
        params=request.args
    else:
        params=request.form
    category=params.get('category')
    product_id=params.get('product_id')
    try:
        client=MongoClient('mongodb://127.0.0.1:27017')
        atlas=client['test']
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
