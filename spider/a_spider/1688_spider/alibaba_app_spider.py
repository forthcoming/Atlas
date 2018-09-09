import sys
import time
import alibaba_kw
from Queue import LifoQueue
from threading import Thread
from atlas.config.settings import *
from multiprocessing.dummy import Pool
from atlas.spider.base.AtlasSpider import AtlasSpider
from atlas.database.atlasDatabase import AtlasDatabase
reload(sys)
sys.setdefaultencoding('utf-8')
'''
Created on 2018年06月20日
@author: lwq
'''


class AliSpider(AtlasSpider):

    def __init__(self):
        super(AliSpider, self).__init__('1688', "atlas")
        self._queue = LifoQueue()
        self.thread_sum = THREAD_NUM
        self.Database = AtlasDatabase(MONGO_URI, MONGO_ATLAS)

    def run(self):
        # step 1 : construct queue
        for part in self.getKeyword():
            self._queue.put(part)

        # step 2 : start thread
        self.start_thread()

    def start_thread(self):
        _threadList = []
        for i in range(self.thread_sum):
            ka = alibaba_kw.AutoSpider(self._queue, self.Database)
            t = Thread(target=ka.main, args=())

            t.daemon = True
            _threadList.append(t)

            t.start()

        for t in _threadList:
            t.join()


if __name__ == '__main__':
    start_time = time.time()
    As = AliSpider()
    As.run()
    print time.time() - start_time


