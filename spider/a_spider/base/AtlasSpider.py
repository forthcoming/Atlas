#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 下午1:48
# @Author  : Jiangtao
# @Site    : 
# @File    : baseSpider
# @Software: PyCharm

from atlas.database.atlasDatabase import AtlasDatabase

class AtlasSpider(object):
    def __init__(self, platform, source):
        self._platform = platform
        self._source = source

    #@desc : 通过平台返回爬虫相关关键字，返回categoryEnName : keyword 的映射
    #@param : platform: 标明爬虫类型
    #return : 返回[(categoryEnName, keyword), (categoryEnName, keyword)]

    def getKeyword(self):
        # MONGO_URI = "mongodb://192.168.105.20:27017"
        # MONGO_ATLAS = "atlas_test1"
        # AD = AtlasDatabase(MONGO_URI, MONGO_ATLAS)
        AD = AtlasDatabase()
        categoryInfos = AD.categoryInfo()
        # categoryInfos = AtlasDatabase().categoryInfo()

        categoryNameToKeywords = []

        for category in categoryInfos:
            for subcategory in category.sub_category:
                if subcategory.platform == self._platform and subcategory.source == self._source:
                    if isinstance(subcategory.keyword, list):
                        for keyword in subcategory.keyword:
                            categoryNameToKeywords.append((category.name_en, keyword))
                    else:
                        categoryNameToKeywords.append((category.name_en, subcategory.keyword))


        return categoryNameToKeywords


    # 业务逻辑，不存在插入，存在则更新，更新的时候不复写is_hash
    @staticmethod
    def insertOrUpdateProduct(categoryEnName, product):
        db = AtlasDatabase()
        if db.findOneProduct(categoryEnName, {'system_id' : product.system_id}):
            db.insertOrUpdateProduct(categoryEnName, product, exclude_keys=['is_hash'])
        else:
            db.insertOrUpdateProduct(categoryEnName, product)







if __name__ == '__main__':
    atlasSpider = AtlasSpider('1688')
    li = atlasSpider.getKeyword()
    print len(li)
    # n = 0
    # for i in li:
    #     n += 1
    #     print i, n











