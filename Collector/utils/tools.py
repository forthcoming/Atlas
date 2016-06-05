# -*- coding: utf-8 -*-
import requests,re
from lxml.html import fromstring

def proxy():
  urls=['http://www.xicidaili.com/nn/{}'.format(i) for i in range(1,5)]
  urls+=['http://www.xicidaili.com/nt/{}'.format(i) for i in range(1,5)]
  head={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
  }
  iplist=set()
  for url in urls:
    r=requests.get(url,headers=head)
    res=fromstring(r.text)

    for sel in res.xpath('//*[@id="ip_list"]/tr')[1:]:
      _=sel.xpath('string(.)').split()
      ip='{}://{}:{}'.format(_[4].lower(),_[0],_[1])
      speed=re.search(r'\d+',sel.xpath('td[7]/div/div/@style')[0]).group()
      conn_time=re.search(r'\d+',sel.xpath('td[8]/div/div/@style')[0]).group()
      if int(speed)>90 and int(conn_time)>90 and re.match(r'https?://((\d{1,3})\.){3}\d{1,3}:\d{1,4}',ip):  #校验ip有效性
        iplist.add(ip)
  return iplist


def translate(word):
  url='http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
  data={
    'type':'AUTO',
    'i':word,
    'doctype':'json',
    'xmlVersion':'1.8',
    'keyfrom':'fanyi.web',
    'ue':'UTF-8',
    'action':'FY_BY_CLICKBUTTON',
    'typoResult':'true'
  }
  r=requests.post(url,data)
  #return r.json()['smartResult']['entries']   用于翻译单词
  return r.json()['translateResult'][0][0]['tgt']


if __name__=='__main__':
  print(translate('今天星期五，心情大好，吃完饭准备跟朋友去抓鱼'))
