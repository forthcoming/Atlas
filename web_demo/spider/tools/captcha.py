# -*- coding: utf-8 -*-
'''
暂未加入opencv模块，后期优化会考虑加上
可用订单号如下:
177SWRAMXG0501T
578886719C

网页源代码中的charset=utf-8意思是该网页需要用utf-8格式解析，将其另存为本地网页，再用notepad++打开，也能看到其编码跟charset一致
'''

import requests,pytesseract
from lxml.html import fromstring
from PIL import Image
from io import BytesIO
from functools import partial

class Captcha():
  
  def __init__(self,im):
    if im.mode!='P':
      im=im.convert('P')
    color=[(index,i) for index,i in enumerate(im.histogram())]
    color.sort(key=lambda x:x[1],reverse=True)
    self.im=im
    self.BGCOLOR=color[0][0]
    self.denoise8=partial(self.denoise,area=[(1,0),(0,1),(-1,0),(0,-1),(-1,1),(1,1),(-1,-1),(1,-1)]) #watch it !!!

  def denoise(self,N,area=[(1,0),(0,1),(-1,0),(0,-1)]):
    pix=self.im.load()
    W,H=self.im.size 
    for i in range(W):
      for j in range(H):
        if i in (0,W-1) or j in (0,H-1):
          pix[i,j]=self.BGCOLOR
        if pix[i,j]!=self.BGCOLOR:
          count=0
          for k in area:
            if pix[i+k[0],j+k[1]]==self.BGCOLOR:
              count+=1
          if count>=N:
            pix[i,j]=self.BGCOLOR

  def __call__(self,a=4,b=8):
    self.denoise(N=a)
    self.denoise8(N=b)
    dic='0123456789qwertyuiopasdfghjklzxcvbnm'   
    captcha=pytesseract.image_to_string(self.im) #default lang='eng' 
    captcha=[_ for _ in captcha if _ in dic]
    if len(captcha)==4:
      print(captcha)     
      return ''.join(captcha)
    else:
      return False


def get_data():
  s=requests.Session()
  req_url='http://query.customs.gov.cn/MNFTQ/MQuery.aspx'
  image_url='http://query.customs.gov.cn/MNFTQ/Image.aspx'
 
  while True:
    r=s.get(image_url)  #获得sessionid
    im = Image.open(BytesIO(r.content))   #图片格式只能以二进制存储(r.content)
    #im.save('src.png')
    captcha=Captcha(im)()
    if captcha:
      break

  r=s.get(req_url)
  res=fromstring(r.content)
  data={
    '__VIEWSTATE':res.xpath('//*[@id="__VIEWSTATE"]/@value')[0],
    '__EVENTVALIDATION':res.xpath('//*[@id="__EVENTVALIDATION"]/@value')[0],
    'ScrollTop':'',
    '__essVariable':'',
    'MQueryCtrl1$ddlCustomCode':'0217',
    'MQueryCtrl1$ddlTransport':'2',
    'MQueryCtrl1$ddlBillType':'E',
    'MQueryCtrl1$txtConveyance':'',
    'MQueryCtrl1$txtVoyage':'',
    'MQueryCtrl1$txtParentNo':'578886719C',
    'MQueryCtrl1$txtParentNo':'177SWRAMXG0501T',
    'MQueryCtrl1$txtChildNo':'',
    #'MQueryCtrl1$txtCode':input('请输入验证码'),
    'MQueryCtrl1$txtCode':captcha,
    'MQueryCtrl1$btQuery':'查 询',
    'select':'中国政府网',
    'select1':'国务院部门网站',
    'select2':'地方政府网站',
    'select3':'驻港澳机构网站',
    'select4':'世界海关组织',
    'select5':'在京直属事业单位',
    'select6':'社会团体',
    'select6':'资讯网',
    'select8':'媒体',  #watch it!!!(注意select[0-8]的获得方法)
  }

  head={
    'Content-Type':'application/x-www-form-urlencoded',
    'Host':'query.customs.gov.cn',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
  }
  s.headers.update(head)

  r=s.post(req_url,data=data)
  res=fromstring(r.content) 
  dic={}
  for sel in res.xpath('//*[@id="MQueryCtrl1_dgView"]/tr')[1:]:
    dic['关区代码']=sel.xpath('td[1]/text()')[0]
    dic['运输方式']=sel.xpath('td[2]/text()')[0]
    dic['提运单类型']=sel.xpath('td[3]/text()')[0]
    dic['运输工具名称']=sel.xpath('td[4]/text()')[0]
    dic['航班\航次']=sel.xpath('td[5]/text()')[0]
    dic['提运单号']=sel.xpath('td[6]/text()')[0]
    dic['进出境日期']=sel.xpath('td[7]/text()')[0]
    dic['件数']=sel.xpath('td[8]/text()')[0]
    dic['重量']=sel.xpath('td[9]/text()')[0]
    dic['进口抵港确报标志']=sel.xpath('td[10]/text()')[0]
    dic['理货状态']=sel.xpath('td[11]/text()')[0]
    dic['出口运抵状态']=sel.xpath('td[12]/text()')[0]
  return dic
   
if __name__=='__main__':
  data=get_data()
  while not data:
    data=get_data()
  print(data)
