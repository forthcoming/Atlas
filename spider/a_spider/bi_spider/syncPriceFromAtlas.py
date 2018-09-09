#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/26 上午10:29
# @Author  : Jiangtao
# @Site    : 
# @File    : syncPriceFromAtlas
# @Software: PyCharm

# coding=utf-8
from pymongo import MongoClient,HASHED
from atlas.config.settings import *


class SyncPriceFromAtlas:
    def __init__(self):
        self._db = MongoClient(MONGO_URI)
        self._dbBI = self._db[MONGO_BI]
        self._dbAtals = self._db[MONGO_ATLAS]


    def _getRootID(self, keyID, dict):
        if dict.has_key(keyID) and keyID != dict[keyID]:
            next = self._getRootID(dict[keyID], dict)

            if next != None:
                return next
            else:
                return dict[keyID]

        return None


    def fetchCategoryIDToAtlasENName(self):
        categoryID2AtlasEnname = {}

        # read categoryInfo to parentID
        categoryId2RootId = {}

        categoryInfo2Parent = {}
        for categoryInfo in self._dbBI['category'].find({}, {"category_id" : 1, "parent_id" : 1}):
            if categoryInfo['parent_id'] != 0:
                categoryInfo2Parent[categoryInfo['category_id']] = categoryInfo['parent_id']
            else:
                categoryInfo2Parent[categoryInfo['category_id']] = categoryInfo['category_id']

        for key in categoryInfo2Parent.keys():
            categoryId2RootId[key] = self._getRootID(key, categoryInfo2Parent)

            if not categoryId2RootId[key]:
                categoryId2RootId[key] = key

        for key in categoryId2RootId.keys():
            categoryID2AtlasEnname[key] = self._dbBI['bi_map_erp'].find_one({'bi_cat_id' : categoryId2RootId[key]}, {"name_en" : 1})['name_en']

        return categoryID2AtlasEnname


    def sync(self):
        catID2ENName = self.fetchCategoryIDToAtlasENName()

        nIndex = 0

        webSiteMap = {}

        for each in self._dbBI['website'].find():
            webSiteMap[each['web_id']] = each['platform']

        for biProduct in self._dbBI['product_bi_final'].find({}, {"_id" : 1, "goods_sn" : 1, 'category_id' : 1, 'dw_web_id' : 1}, no_cursor_timeout=True):
            if nIndex % 10000 == 0:
                print 'Flag : %d' % nIndex
            nIndex = nIndex + 1

            hash_url = biProduct['goods_sn']
            category_id = biProduct['category_id']
            websiteId = biProduct['dw_web_id']


            if not catID2ENName.has_key(category_id):
                print biProduct["_id"]

            # 获取供应商信息
            result = {
                'supplier_num' : 0,
                'min_price' : 0,
                'max_price' : 0
            }

            nodeInfo = self._dbAtals['cluster_node_%s' % catID2ENName[category_id]].find_one({'system_id' : '%s_%s' % (webSiteMap[websiteId], hash_url)}, {"cluster_id" : 1})

            if nodeInfo:
                systemsCur = self._dbAtals['cluster_node_%s' % catID2ENName[category_id]].find(
                    {'cluster_id': nodeInfo['cluster_id'], 'system_id' : {"$regex" : "^1688.*"}, "on_sale" : True}, {"system_id": 1})

                listID = []
                for systemID in systemsCur:
                    listID.append(systemID['system_id'])

                result['supplier_num'] = len(listID)

                dataListCur = self._dbAtals['product_%s' % catID2ENName[category_id]].find({"system_id" : {"$in" : listID}}, {"price" : 1, "ext_price" : 1})

                for each in dataListCur:
                    if not isinstance(each['price'], int):
                        continue


                    if result['min_price'] == 0:
                        result['min_price'] = each['price']
                    else :
                        result['min_price'] = min(result['min_price'], each['price'])

                    result['max_price'] = max(result['max_price'], each['price'])
                    # # max price
                    # if each.has_key('ext_price') and isinstance(each['ext_price'], list) and len(each['ext_price']) > 0 and not isinstance(each['ext_price'][0], list):
                    #     for prictItem in each['ext_price']:
                    #         result['max_price'] = max(result['max_price'], int(float(prictItem['price']) * 100))

            self._dbBI['product_bi_final'].update_one({"_id" : biProduct["_id"]}, {"$set" : result})






#


# for each in bi_final.find({'supplier_num' : None}, {"_id" : 1, "hash_url" : 1, "category_id" : 1}):




if __name__ == '__main__':
    sync = SyncPriceFromAtlas()
    print sync.sync()


