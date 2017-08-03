# coding:utf-8
import requests
from lxml.html import fromstring

class V2ex():
  head = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'Origin': 'http://www.v2ex.com',
    'Referer': 'http://www.v2ex.com/signin',
    'Host': 'www.v2ex.com'
  }
  s = requests.Session()
  s.headers.update(head)

  def login(self,name='fucku', password='fuckufucku'):
    r = self.s.get('http://v2ex.com/signin')
    res = fromstring(r.content)
    NAME,PASSWORD = res.xpath('//input[@class="sl"]/@name')
    once = res.xpath('//input[@name="once"]/@value')
    data = {
      NAME: name,
      PASSWORD: password,
     'once': once,
     'next': '/'
    }
    self.s.post('http://v2ex.com/signin', data)

  def sign(self):
    r = self.s.get('http://v2ex.com/mission/daily')
    res = fromstring(r.content)
    _=res.xpath('//input[@type="button"]/@onclick')[0].split("'")
    url = 'http://v2ex.com{}'.format(_[1])  #地址每次都不一样（思考为什么在浏览器中看到的地址一样）
    r=self.s.get(url, headers={'Referer': 'http://www.v2ex.com/mission/daily'})  #点击签到,返回点击签到后的页面
    if '已成功领取每日登录奖励' in r.text:
      print('已成功领取每日登录奖励...')
    else:
      print('已经领取过每日登录奖励...')

if __name__ == '__main__':
    foo=V2ex()
    foo.login()
    foo.sign()
