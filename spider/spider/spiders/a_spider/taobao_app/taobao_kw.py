# coding=utf-8
import os
import re
import time
import copy
import json
import Queue
import random
import hashlib
import logging
import datetime
import requests
import jsonpath
import threading
import linecache
from lxml import etree
from urllib import quote
from pymongo import MongoClient
from multiprocessing.dummy import Pool
from pvs_analyze import product_details
from taobao_comment_spider import Taobao_Comment
from atlas.log.log import Log
from atlas.config.settings import *
from atlas.log.atlas_log import atlas_Log
from atlas.models.tool.common import on_off_sale
from atlas.utils.request_tools.request_tool import *
from atlas.database.atlasDatabase import AtlasDatabase
from atlas.datamodel.product import Product, HistoryProduct
from atlas.utils.httprequest.many_request import ManyRequest
from atlas.utils.analyze_match.taobao_match import TaobaoMatch

mutex = threading.Lock()  


class AutoSpider:
    def __init__(self, keywordQueue, AtlasDatabase):
        self.manyreq = ManyRequest()
        self.tmatch = TaobaoMatch()
        self.atlas_log = atlas_Log()
        self.tc = Taobao_Comment()

        self.kwQueue = keywordQueue
        self.Database = AtlasDatabase

        self.headers = copy.copy(tbheaders)
        self.params = tbparams
        try:
            self.sum = int(PRODUCT_SUM)
        except Exception:
            self.sum = float('inf')

    def __integer(self, prices):
        price = int(prices * 100) if prices else 0
        return price

    def __float(self, num):
        price = float(num) if num else 0
        return price

    def __get_pid(self, kw_name):
        begin_page = 1
        no_value = False
        p_id_big_li = []
        name = quote(kw_name)

        while True:
            link = 'https://s.m.taobao.com/search?q={}&search=%E6%8F%90%E4%BA%A4&tab=all&sst=1&n=40&buying=buyitnow&m=api4h5&page={}'.format(
                name, begin_page)
            p_id_li = self.__analyze_list_info(link)
            if not p_id_li:
                if no_value:
                    print '[INFO]: 已无更多商品！！！'
                    break
                else:
                    print "[INFO]: warnning!!! 没找到与“%s”相关的商品" % kw_name
                    # TODO 此处可以写入日志
                    break

            p_id_big_li.extend(p_id_li)
            length = len(p_id_big_li)

            print "[INFO]: 当前商品数量：{}".format(length)

            if length > 0:
                no_value = True

            if length >= self.sum:
                print '-' * 100
                break
            else:
                begin_page += 1
        return p_id_big_li

    def __getsign(self, h5_tk, millis, data):
        string = h5_tk + '&' + str(millis) + "&12574478&" + data
        m2 = hashlib.md5()
        m2.update(string)
        sign = m2.hexdigest()
        print "[INFO]: sign：", sign
        return sign

    def __geth5tk(self):
        print "[INFO]: thread_name", threading.current_thread().getName(), 'start'
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.baichuan.smb.get/1.0/?jsv=2.4.11&appKey=12574478&t=1530602967150&sign=26d11c649f073b356e453a95743911aa&api=mtop.taobao.baichuan.smb.get&v=1.0&type=originaljson&dataType=jsonp&timeout=10000"
        res = self.manyreq.many_request(url, match_func=self.tmatch.match_h5tk,
                                        headers=self.headers,
                                        **self.params)
        cookies = res.cookies.get_dict()
        h5_tk = cookies['_m_h5_tk'].split('_')[0]
        print '[INFO]: h5_tk: ', h5_tk
        return h5_tk

    def __construct_detailurl(self, millis, sign, data):
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?"
        data = {
            "jsv": "2.4.8",
            "appKey": "12574478",
            "t": str(millis),
            "sign": sign,
            "api": "mtop.taobao.detail.getdetail",
            "v": "6.0",
            "dataType": "jsonp",
            "ttid": "2017@taobao_h5_6.6.0",
            "AntiCreep": "true",
            "type": "jsonp",
            "callback": "mtopjsonp2",
            "data": data,
        }
        data = '&'.join(key + "=" + quote(value) for key, value in data.items())
        url += data
        return url

    # 清洗Json
    def __wash_json(self, res):
        res = re.search(r'mtopjsonp2\((.*)\)', res, re.S).group(1)
        json_obj = json.loads(res)
        apistack = json_obj.get("data", {}).get("apiStack", [])
        for api_dict in apistack:
            stack_data = api_dict.get("value", '')
            json_obj['data'].pop('apiStack', "404")
            json_obj['splice'] = stack_data
        return json_obj

    def on_off_sale(self, judge_mark, node, system_id):
        if judge_mark == "off_sales":
            on_off_sale(node, system_id, False)
            print '\n'
            print "[INFO]: 商品已下架！！！！！"
            print '+-' * 40
            return True

    def scheduler(self):
        # 通过关键字获取列表页ID
        # 判断列表页ID数量
        # 循环ID列表，每个ID获取一次sign值
        # 构建商品详情url参数
        # 清洗Json
        # 调用Product_details() 提取详情数据
        # 判断上下架
        # 获取商品评论数据
        # 整理以上所有数据（商品数据，以及历史数据）入库
        pass

    def extract_queue(self):
        info = self.kwQueue.get(block=False)
        kw_name = info[1].replace('"', '').replace("'", '')
        kw_name = kw_name.replace('\n', '').replace('\r', '')
        kw_name = kw_name.replace('\t', '').replace('\\', '').encode('utf-8')
        category = info[0]
        set_name = "product_%s" % category
        history_set_name = "history_taobao_%s" % category
        print '*' * 100, self.sum
        return kw_name, category, set_name, history_set_name

    def __analyze_list_info(self, link):
        p_res = self.manyreq.many_request(link,
                                          match_func=self.tmatch.match_list,
                                          headers=self.headers,
                                          **self.params).text
        print p_res
        json_obj = json.loads(p_res)
        listitem = json_obj.get("listItem", [])
        # flag = jsonpath.jsonpath(json_obj, expr='$..listItem[*]')
        if listitem:
            p_id_li = [item.get("item_id", '') for item in listitem]
            contact_address = [item.get("sellerLoc", '') for item in listitem]
            # p_id_li = jsonpath.jsonpath(json_obj, expr='$..listItem[*].item_id')
            # contact_address = jsonpath.jsonpath(json_obj, expr='$..listItem[*].sellerLoc')
            list_page_data = [x for x in zip(p_id_li, contact_address)]
            return list_page_data
        else:
            return False

    def dummy_func(self, p_id_li):
        if isinstance(self.sum, int):
            p_id_li = p_id_li[:self.sum]
        print ('[INFO]: dummy_func内测试长度：'), len(p_id_li)

        index_li = [i + 1 for i in range(len(p_id_li))]
        info = zip(index_li, p_id_li)
        # 创建10个线程的线程池
        pool = Pool(11)
        # map()高阶函数，用来批量处理函数传参
        pool.map(self.__product_detail, info)
        # 关闭线程池
        pool.close()
        # 阻塞主线程，等待子线程结束
        pool.join()

    def __product_detail(self, p_id_big_li, category, kw_name):
        p_id_big_li = p_id_big_li[:self.sum]
        length = len(p_id_big_li)
        for n in range(length):
            product_dict = Product()
            history_dict = HistoryProduct()
            pid = p_id_big_li[n][0]
            contact_address = p_id_big_li[n][1]
            # pid = "566603286049"
            system_id = "taobao_%s" % pid
            node = self.Database.db['cluster_node_{}'.format(category)]
            data = '{"itemNumId":"%s"}' % pid

            print "[INFO]: 正在请求 >>> “%s”关键字的第%s件商品。。。。。。" % (kw_name, str(n+1))
            print "[INFO]: system_id : %s" % system_id
            print "[INFO]: data：{}".format(data)

            millis = int(time.time() * 1000)

            h5_tk = self.__geth5tk()

            sign = self.__getsign(h5_tk, millis, data)

            url = self.__construct_detailurl(millis, sign, data)

            res = self.manyreq.many_request(url, match_func=self.tmatch.match_details,
                                            headers=self.headers,
                                            **self.params).text

            print "[INFO]: 商品详情：", res
            json_obj = self.__wash_json(res)
            print json_obj
            p_info_dict = product_details(json_obj)

            if self.on_off_sale(p_info_dict, node, system_id):
                print "[INFO]: 无法购买ID：", pid
                continue

            contact_address = p_info_dict['contact_address'] or contact_address
            contact_information = {"contact_address": contact_address}

            product_dict.currency = "¥"
            product_dict.is_hash = False
            product_dict.product_id = pid
            product_dict.keywords = kw_name
            product_dict.platform = "taobao"
            product_dict.system_id = system_id
            product_dict.title = p_info_dict['p_name']
            product_dict.contact = contact_information
            product_dict.price = p_info_dict['lt_price']
            product_dict.image = p_info_dict['image_list']
            product_dict.sales = p_info_dict['sell_count']
            product_dict.ext_price = p_info_dict['ext_price']
            product_dict.seller_name = p_info_dict['seller_name']
            product_dict.product_url = "https://detail.tmall.com/item.htm?&id=%s" % pid

            history_dict.category = category
            history_dict.keywords = kw_name
            history_dict.system_id = system_id
            history_dict.price = p_info_dict['lt_price']
            history_dict.inventory = p_info_dict['stock_dict']
            history_dict.seller_name = p_info_dict['seller_name']
            history_dict.record_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 最好是插入成功后传入
            on_off_sale(node, system_id, True)
            print '\n'
            yield product_dict, history_dict

    def __comment_info(self, pid, product_dict):
        comment_info_li = self.tc.comment(self.manyreq.many_request,
                               self.tmatch.match_comments,
                               pid,
                               **self.params
                               )
        print "[INFO]: 评论内容：", comment_info_li
        product_dict.comment = comment_info_li


    def storage(self, product_dict, history_dict):
        system_id = product_dict.system_id.encode('utf-8')
        old_record = self.Database.findOneProduct(history_dict.category, {"system_id": system_id})
        if not old_record:
            self.Database.insertOrUpdateProduct(history_dict.category, product_dict)
        else:
            self.Database.insertOrUpdateProduct(history_dict.category, product_dict, exclude_keys=["is_hash"])

        self.Database.insertHistory(history_dict.category, history_dict, product_dict.platform)

    @Log(level=logging.INFO, name='taobao.log')
    def main(self):
        while not self.kwQueue.empty():
            kw_name, category, set_name, history_set_name = self.extract_queue()
            p_id_big_li = self.__get_pid(kw_name)
            for product_dict, history_dict in self.__product_detail(p_id_big_li, category, kw_name):
                self.__comment_info(product_dict.product_id, product_dict)
                self.storage(product_dict, history_dict)


if __name__ == '__main__':
    MONGO_URI = "mongodb://192.168.105.20:27017"
    MONGO_ATLAS = "atlas_test1"
    keywordQueue = Queue.Queue()
    Database = AtlasDatabase(MONGO_URI, MONGO_ATLAS)
    keywordQueue.put(("women", "连衣裙"))
    As = AutoSpider(keywordQueue, Database)
    As.main()
    # atlas.main(As.db_host, As.db_port, As.db_database)

