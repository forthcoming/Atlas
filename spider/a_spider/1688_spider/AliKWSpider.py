#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 下午5:03
# @Author  : Jiangtao
# @Site    : 
# @File    : AliKWSpider.py
# @Software: PyCharm

from atlas.spider.base.ThreadKWSpider import ThreadKWSpider

class AliKWSpider(ThreadKWSpider):

    def spiderKW(self, categoryENName, keyword):
        self.zhunbcookie()
        for product in self.getList():
            Detail.getByProductID(product.product_id)


            AtlasSpider.insertOrUpdateProduct(categoryENName, product)


    def zhunbcookie(self):
        pass


    def getList(self):
        pass
