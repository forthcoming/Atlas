#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/18 下午1:53
# @Author  : Jiangtao
# @Site    :
# @File    : reportAtlasStatus.py
# @Software: PyCharm

import sys
sys.path.append('..')
sys.path.append('../..')
import datetime
import time


from pymongo import MongoClient
from bson import ObjectId

from atlas.config.settings import *
from atlas.datamodel.categoryInfo import CategoryInfo, SubCategory
from atlas.utils.sendemail.sendemail import sendEmail
from atlas.utils.timeformat.TimeFormat import getDayBefore


# @desc: 汇总Atlas当前数据状态
class ReportEveryCircle:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_ATLAS]


    def getCategorys(self):
        categorys = []
        for category in self.db['category_info'].find():
            categoryObj = CategoryInfo.modelFromDict(category)

            subCategoryList = []
            for item in categoryObj.sub_category:
                subCategoryList.append(SubCategory.modelFromDict(item))

            categoryObj.sub_category = subCategoryList

            categorys.append(categoryObj)

        return categorys



    def run(self):
        categorys = self.getCategorys()

        # 构造日期和objectid
        date2Objects = {}

        for i in range(1, 7):


            day = getDayBefore(i)
            day = day.split(' ')[0]

            startObj = ObjectId.from_datetime(
                generation_time=datetime.datetime.strptime('%s 00:00:00' % day, "%Y-%m-%d %H:%M:%S"))
            endObj = ObjectId.from_datetime(
                generation_time=datetime.datetime.strptime('%s 23:59:59' % day, "%Y-%m-%d %H:%M:%S"))

            date2Objects[day] = [startObj, endObj]

        # # step 1 : 获取爬虫新增量和消费量
        # spiderNumber = {}
        #
        # for day in date2Objects:
        #     startObj = date2Objects[day][0]
        #     endObj = date2Objects[day][-1]
        #
        #     productNum = 0
        #     costNum = 0
        #
        #     for category in categorys:
        #         setName = 'product_{}'.format(category.name_en)
        #
        #         productNum += self.db[setName].count({"_id" :  {"$gt" : startObj, "$lt" : endObj}})
        #
        #         for subCategory in category.sub_category:
        #             costNum += len(self.db['image_phash_{}_{}'.format(category.name_en, subCategory.platform)].distinct('system_id',{"_id" :  {"$gt" : startObj, "$lt" : endObj}} ))
        #
        #
        #     print '爬虫 %s 生产：%d 消费：%d' % (day, productNum, costNum)




        #step 2 : 获取phash生产和消费
        for day in date2Objects:
            startObj = date2Objects[day][0]
            endObj = date2Objects[day][-1]

            productNum = 0
            costNum = 0

            for category in categorys:
                for subCategory in category.sub_category:
                    productNum += self.db['image_phash_{}_{}'.format(category.name_en, subCategory.platform)].count({"_id" :  {"$gt" : startObj, "$lt" : endObj}})


            print 'PHASH %s 生产：%d 消费：%d' % (day, productNum, costNum)

        #step 3 : img match 生产和消费
        for day in date2Objects:
            startObj = date2Objects[day][0]
            endObj = date2Objects[day][-1]

            productNum = 0
            costNum = 0



            for category in categorys:
                setName = 'image_match_result_{}'.format(category.name_en)

                pipeline = [
                    {"$match" : {"_id": {"$gt": startObj, "$lt": endObj}}},
                    {"$group": {"_id" : None, "count": {"$sum": '$match_num'}}}
                ]

                productNum += self.db[setName].count({"_id" :  {"$gt" : startObj, "$lt" : endObj}})
                for eash in self.db['item_match_result_{}'.format(category.name_en)].aggregate(pipeline):
                    costNum += eash['count']


            print '图片比较 %s 生产：%d 消费：%d' % (day, productNum, costNum)


        # step 4 : item_match 生产和消费

        for day in date2Objects:
            startObj = date2Objects[day][0]
            endObj = date2Objects[day][-1]

            productNum = 0
            costNum = 0



            for category in categorys:
                setName = 'item_match_result_{}'.format(category.name_en)

                productNum += self.db[setName].count({"_id": {"$gt": startObj, "$lt": endObj}})
                costNum += self.db[setName].count({'human_processed': True, 'updated_at': {
                    "$gt": '%s 00:00:00' % day.replace('/', '-'), "$lt": '%s 23:59:59' % day.replace('/', '-')}})


            print '商品匹配对 %s 生产：%d 消费：%d' % (day, productNum, costNum)



if __name__ == '__main__':
    reportHandle = ReportEveryCircle()
    reportHandle.run()