import datetime
import time
from pymongo import MongoClient
from bson import ObjectId
from atlas.config.settings import *
from atlas.datamodel.categoryInfo import CategoryInfo, SubCategory
from atlas.utils.sendemail.sendemail import sendEmail
from atlas.utils.timeformat.TimeFormat import getDayBefore

######################################################
# 模板中替换内容
TEMPLATE_BODYKEY = '{TABLE_REPLACE_POS}'
TEMPLATE_COLUMNKEY = '{PLATFORM_NUM}'
TEMPLATE_HEADERPLATFORMKEY = '{HEADER_PLATFORM}'
TEMPLATE_CLUSTER_PLUS_1 = '{PLATFORM_NUM_PLUS_1}'


TEMPLATE_WAITHUMANPROCESS = '{WAITPROCESS_INFO}'

TEMPLATE_PRODUCT_COST = '{TABLE_REPLACE_PRODUCT_COST}'

TEMPLATE_COST = '{TABLE_REPLACE_COST_DETAIL}'

#####################################################

# @desc: 汇总Atlas当前数据状态
class ReportAtlas:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_ATLAS]
        self.htmlBody = open('template/monitoratlas.html').read()
        pass


    def getMachine2Categorys(self):
        machine2Categorys = {}
        for category in self.db['category_info'].find():
            categoryObj = CategoryInfo.modelFromDict(category)

            subCategoryList = []
            for item in categoryObj.sub_category:
                subCategoryList.append(SubCategory.modelFromDict(item))

            categoryObj.sub_category = subCategoryList

            categoryList = []

            if machine2Categorys.has_key(categoryObj.machine_id):
                categoryList = machine2Categorys[categoryObj.machine_id]

            categoryList.append(categoryObj)

            machine2Categorys[categoryObj.machine_id] = categoryList

        return machine2Categorys


    def getProductNumWithCategoryAndPlatform(self, categoryEnname, platformlist):
        productName = 'product_' + categoryEnname
        retNumList = []
        retNumList.append('<td>%d</td>' % self.db[productName].count())
        return retNumList


    def getpHashCount(self, categoryEnname, platformlist):
        phashTablePre = 'image_phash_' + categoryEnname + '_'
        fliter = {}
        retNumList = []

        for platform in platformlist:
            fliter['match_' + platform] = True

        for platform in platformlist:
            total = self.db[phashTablePre + platform].count()
            match = self.db[phashTablePre + platform].count(fliter)

            retNumList.append('<td>%d/%d</td>' % (match, total))

        return retNumList


    def getPicPairNum(self, categoryEnname):
        setName = 'image_match_result_' + categoryEnname
        return str(self.db[setName].count())


    def getItemMatchResult(self, categoryEnname):
        setName = 'item_match_result_' + categoryEnname

        retDataList = []

        nTotal = self.db[setName].count()

        retDataList.append('<td>%d</td>' % nTotal)

        nHumanNotProcessNum = self.db[setName].count({'human_processed' : False})
        retDataList.append('<td>%d</td>' % nHumanNotProcessNum)

        if (nTotal - nHumanNotProcessNum) == 0:
            retDataList.append('<td>100%</td>')
        else:
            retDataList.append('<td>%.2f%%</td>' % (self.db[setName].count({'human_processed' : True, 'human_match' : 1}) * 100 / float(nTotal - nHumanNotProcessNum)))

        return retDataList


    def getClusterInfo(self, categoryName, platformList):
        strName = 'cluster_node_' + categoryName

        retDataList = []

        retDataList.append('<td>%d</td>' % len(self.db[strName].distinct('cluster_id')))

        return retDataList


    def report(self):
        machine2Categorys = self.getMachine2Categorys()
        strBody = ''
        strHeader = ''

        # add product num
        platformList = [subcategory.platform for subcategory in machine2Categorys.values()[-1][-1].sub_category]

        self.htmlBody = self.htmlBody.replace(TEMPLATE_COLUMNKEY, str(len(platformList)))
        self.htmlBody = self.htmlBody.replace(TEMPLATE_CLUSTER_PLUS_1, str(len(platformList) + 1))

        strHeader = strHeader + '<th>' + '</th><th>'.join(platformList) + '</th>'
        self.htmlBody = self.htmlBody.replace(TEMPLATE_HEADERPLATFORMKEY, strHeader)

        # add machine、category
        for machine in machine2Categorys.keys():
            bMutAdd = False
            for category in machine2Categorys[machine]:
                mutLineMachine = ''

                if not bMutAdd:
                    mutLineMachine = '<td rowspan=%d>%s</td>' % (len(machine2Categorys[machine]), machine)
                    bMutAdd = True

                lineInfo = '<tr>' +\
                            mutLineMachine + \
                           '<td>%s</td>' % category.name +\
                            ''.join(self.getProductNumWithCategoryAndPlatform(category.name_en, platformList)) + \
                            '<td>%s</td>' % self.getPicPairNum(category.name_en) + \
                            ''.join(self.getItemMatchResult(category.name_en)) + \
                            ''.join(self.getClusterInfo(category.name_en, platformList)) + \
                           '</tr>'

                strBody = strBody + lineInfo




        # 获取总数信息
        nTotal = 0
        nWaitHuman = 0
        for machine in machine2Categorys.keys():
            for category in machine2Categorys[machine]:
                setName = 'item_match_result_' + category.name_en

                nTotal = nTotal + self.db[setName].count()
                nWaitHuman = nWaitHuman + self.db[setName].count({'human_processed': False})



        self.htmlBody = self.htmlBody.replace(TEMPLATE_WAITHUMANPROCESS, '商品匹配对总数 ： %d  人工待匹配： %d' % (nTotal, nWaitHuman))

        reportData = ''
        # 获取近七天生产消费情况
        for i in range(1, 7):
            day = getDayBefore(i)
            day = day.split(' ')[0]


            startObj = ObjectId.from_datetime(generation_time=datetime.datetime.strptime('%s 00:00:00' % day, "%Y-%m-%d %H:%M:%S"))
            endObj = ObjectId.from_datetime(generation_time=datetime.datetime.strptime('%s 23:59:59' % day, "%Y-%m-%d %H:%M:%S"))

            nAddCount = 0
            nProcessCount = 0

            for categorys in machine2Categorys.values():
                for cat in categorys:
                    setName = 'item_match_result_' + cat.name_en

                    nAddCount = nAddCount + self.db[setName].count({"_id" : {"$gt" : startObj, "$lt" : endObj}})
                    nProcessCount = nProcessCount + self.db[setName].count({'human_processed': True, 'updated_at' : {"$gt" : '%s 00:00:00' % day.replace('/', '-'), "$lt" : '%s 23:59:59' % day.replace('/', '-')}})

            reportData = reportData + '<tr><td>%s</td><td>%d</td><td>%d</td></tr> '% (day, nAddCount, nProcessCount)


        self.htmlBody = self.htmlBody.replace(TEMPLATE_PRODUCT_COST, reportData)



        #日确认匹配情况
        day = getDayBefore(1)
        day = day.split(' ')[0]

        costMap = {}

        for machine in machine2Categorys.keys():
            for category in machine2Categorys[machine]:
                setName = 'item_match_result_' + category.name_en

                # userList = self.db[setName].distinct('oa_user_name', {'human_processed': True})
                userList = self.db[setName].distinct('oa_user_name', {'human_processed': True, 'updated_at' : {"$gt" : '%s 00:00:00' % day, "$lt" : '%s 23:59:59' % day}})


                for user in userList:
                    nCount = self.db[setName].count({'oa_user_name' : user ,'human_processed': True, 'updated_at' : {"$gt" : '%s 00:00:00' % day, "$lt" : '%s 23:59:59' % day}})

                    if costMap.has_key(user):
                        costMap[user] = costMap[user] + nCount
                    else:
                        costMap[user] = nCount

        # 人员消费
        strDetail = ''

        for key in costMap.keys():
            strDetail = strDetail + '<tr><td>%s</td><td>%d</td></tr>' % (key, costMap[key])


        self.htmlBody = self.htmlBody.replace(TEMPLATE_COST, strDetail)



        sendEmail(['tao@qq.com', 'lei@qq.com', 'chen@qq.com'], self.htmlBody.replace(TEMPLATE_BODYKEY, strBody), 'Atlas汇总统计')









if __name__ == '__main__':
    reportHandle = ReportAtlas()
    reportHandle.report()