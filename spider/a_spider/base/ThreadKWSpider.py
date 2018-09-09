#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 下午4:57
# @Author  : Jiangtao
# @Site    : 
# @File    : ThreadKWSpider
# @Software: PyCharm



class ThreadKWSpider:
    def __init__(self, queue):
        self._kwQueue = queue


    def main(self):

        while True:
            try:
                info = self._kwQueue.get(block=False)
            except Exception, e:
                break

            self.spiderKW(info[0], info[1])

    def spiderKW(self, categoryENName, keyword):
        raise 'impl to 1688 or taobao'

