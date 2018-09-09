#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 下午4:44
# @Author  : Jiangtao
# @Site    : 
# @File    : AliSpider
# @Software: PyCharm

import alibaba_kw
from Queue import Queue
from threading import Thread
from atlas.spider.base.AtlasSpider import AtlasSpider


class AliSpider(AtlasSpider):

    def __init__(self):
        super(AliSpider, self).__init__('1688')
        self._queue = Queue()

    def run(self):
        # step 1 : construct queue
        for part in self.getKeyword():
            self._queue.put(part)

        # step 2 : start thread
        self.start_thread()

    def start_thread(self, num=10):
        _threadList = []
        for i in range(num):
            ka = alibaba_kw.AutoSpider(self._queue)
            t = Thread(target=ka.main, args=())

            t.daemon = True
            _threadList.append(t)


            t.start()

        for t in _threadList:
            t.join()



As = AliSpider()
As.run()