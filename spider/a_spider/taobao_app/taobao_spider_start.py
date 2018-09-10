import sys
import time
import taobao_kw
from Queue import Queue
from threading import Thread
from atlas.spider.base.AtlasSpider import AtlasSpider
from atlas.database.atlasDatabase import AtlasDatabase
from atlas.config.settings import *
reload(sys)
sys.setdefaultencoding('utf-8')


class TbSpider(AtlasSpider):

    def __init__(self):
        super(TbSpider, self).__init__('1688', "atlas")
        self._queue = Queue()
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
            ka = taobao_kw.AutoSpider(self._queue, self.Database)
            t = Thread(target=ka.main, args=())

            t.daemon = True
            _threadList.append(t)

            t.start()

        for t in _threadList:
            t.join()


if __name__ == '__main__':
    start_time = time.time()
    As = TbSpider()
    As.run()
    print time.time() - start_time
