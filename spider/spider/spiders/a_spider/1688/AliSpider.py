import alibaba_kw
from Queue import Queue
from threading import Thread
from atlas.spider.base.AtlasSpider import AtlasSpider


class AliSpider(AtlasSpider):

    def __init__(self):
        super(AliSpider, self).__init__('1688')
        self._queue = Queue()

    def run(self):
        for part in self.getKeyword():
            self._queue.put(part)

        _threadList = []
        for i in range(10):
            ka = alibaba_kw.AutoSpider(self._queue)
            t = Thread(target=ka.main)
            _threadList.append(t)
            t.start()

        for t in _threadList:
            t.join()

As = AliSpider()
As.run()
