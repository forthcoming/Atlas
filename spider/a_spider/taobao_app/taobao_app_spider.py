import sys
import time
import Queue
import requests
import threading
import taobao_kw
from pymongo import MongoClient
from multiprocessing.dummy import Pool
sys.path.append('../..')
from config.settings import *
reload(sys)
sys.setdefaultencoding('utf-8')
'''
Created on 2018年06月20日
@author: lwq
'''


class Mongo_Inquire(object):
    def __init__(self):

        self.keywordQueue = Queue.Queue()

        # self.headers = ""
        # 代理服务器
        proxyHost = PROXY_HOST
        proxyPort = PROXY_PORT

        # 代理隧道验证信息
        proxyUser = PROXY_USER
        proxyPass = PROXY_PASS

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        print '[INFO]: proxy：', proxyMeta
        self.proxy = {
            "http": proxyMeta,
            "https": proxyMeta,
        }

        # DATE = datetime.datetime.now().strftime('%Y-%m-%d')
        self.db_client = MONGO_URI
        self.db_database = MONGO_ATLAS
        self.client = MongoClient(self.db_client)
        self.info = self.client[self.db_database][MONGO_SET]
        self.db_set = self.client[self.db_database]
        self.srequests = requests.Session()
        self.data_queue = Queue.Queue()
        self.cookies = ""
        self.iswubai = 0
        self.thread_sum = THREAD_NUM


    def __del__(self):
        self.client.close()
        print "[INFO]: 已成功关闭数据库连接对象！！！！！！"

    def db_select(self):
        result = self.info.find()
        for item in result:
            name_en = item['name_en']
            kw = item["sub_category"]
            # print kw
            for dc in kw:
                # print dc
                if dc["platform"] != "1688":
                    continue

                keywords = dc["keyword"]
                for keyword in keywords:
                    self.keywordQueue.put((name_en, keyword))

        self.dummy_func()

    def relay_main(self, func):
        func.main()

    def dummy_func(self):
        print self.keywordQueue.qsize()
        # # return
        # # 创建10个线程的线程池
        # pool = Pool(14)
        # # map()高阶函数，用来批量处理函数传参
        # pool.imap(self.relay_main, (kw_spider.Auto_Spider(self.keywordQueue) for _ in range(self.keywordQueue.qsize())))
        # # 关闭线程池
        # pool.close()
        # # 阻塞主线程，等待子线程结束
        # pool.join()


        tList = []

        for i in range(self.thread_sum):
            ka = taobao_kw.AutoSpider(self.keywordQueue)
            t = threading.Thread(target=ka.main, args=())
            t.daemon = True
            t.start()
            tList.append(t)

        for t in tList:
            t.join()


if __name__ == '__main__':
    start_time = time.time()
    As = Mongo_Inquire()
    As.db_select()
    print time.time() - start_time



