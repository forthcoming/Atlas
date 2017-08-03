#coding=utf-8
import base64,requests,time,re
from scrapy.exceptions import CloseSpider
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from random import choice
from Spider.utils.mydict import account

class Login():

  def __init__(self,method,username=None,password=None):
    self.s = requests.Session()
    self.method=method
    self.username=username
    self.password=password
    if username is None or password is None:
      self.username, self.password = choice(account[self.method])
  
  def __call__(self,is_dict=True):  #just for learning __call__ method !
    func = getattr(self, self.method, None)
    if callable(func):
      func()
      cookies = {_.name: _.value for _ in self.s.cookies}  # 等价 cookies=self.s.cookies.get_dict()
      if is_dict == False:
        cookies = ';'.join(('{}={}'.format(_.name, _.value) for _ in self.s.cookies))
      return cookies
    else:
      raise CloseSpider('Fatal error,no such method !')

  # Both
  def sina(self):
    data = {
      "entry": "sso",
      "gateway": "1",
      "from": "null",
      "savestate": "0",
      "useticket": "0",
      "pagerefer": "",
      "vsnf": "1",
      "su": base64.b64encode(self.username.encode('utf-8')),
      "service": "sso",
      "sp": self.password,
      "sr": "1366*768",
      "encoding": "UTF-8",
      "cdult": "3",
      "domain": "sina.com.cn",
      "prelt": "0",
      "returntype": "TEXT",
    }

    r = self.s.post('https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)', data=data).json()
    if r["retcode"] == "0":
      print('Hello {}!'.format(r.get('nick', '')))
    else:
      print('Access denied：{}'.format(r["reason"]))

  def qufenqi(self):
    head = {
      'User - Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
      'Host': 'passport.qufenqi.com',
      'Origin': 'http://passport.qufenqi.com',
      'Referer': 'http://passport.qufenqi.com/login?tarurl=http%3A%2F%2Fwww.qufenqi.com&registurl=http://passport.qufenqi.com/register&entry=qufenqi.shop',
    }
    data = {
      'loginname': self.username,
      'password': self.password,
      'curdomain': 'qufenqi.shop',
      'rememberme': 'true',
      'istrust': 'true',
    }

    r = self.s.post('http://passport.qufenqi.com/sso/login', data=data,headers=head,)  #此处头信息只能加在这儿
    for url in r.json()['data'].values():  # watch it !!!
      self.s.get('http:{}'.format(url))

  def ttz(self):
    data = {
      'verify': '',
      'Action': 'indexLogin',
      'Username': self.username,
      'Password': self.password,
    }
    self.s.post('https://www.ttz.com/Member/login', data=data,)

  def baidu(self):
    req_url="https://passport.baidu.com/v2/api/?login"
    token_url="https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&class=login"  #刷新https://passport.baidu.com/v2/?login

    self.s.get(req_url)  #得到BAIDUID
    '''
    能拿到BAIDUID的请求都可以
    s.get('https://passport.baidu.com')
    s.get('http://www.baidu.com')
    s.get(req_url,verify=False)
    请求https类型地址,出现requests SSL: CERTIFICATE_VERIFY_FAILED）时加上verify=False即可
    '''
    r=self.s.get(token_url)

    data = {
      "username":self.username,
      "password":self.password,
      'tpl' : 'pp',  #登录的是m.baidu.com，应为电脑端是'tpl':'mn'
      "token":re.search(r'"token" : "([0-9a-z]+)",', r.text).group(1),
    }
    self.s.post(req_url,data=data)  #此时已含有BDUSS字段

  def test_cookies(self,url):
    r=requests.get(url,cookies=self.__call__())
    with open('{}.html'.format(self.method),'wb') as f:
      f.write(r.content)


class _Login():

  def __init__(self, method,username=None, password=None,args=None):
    self.method = method
    self.username = username
    self.password = password
    if args==None:
      args=[
        '--cookies-file=cookies.txt',  # why not come into force
        '--load-images=false',
        '--disk-cache=true',
        '--log-path=/root/Desktop/phantom.log',
        #'--ignore-ssl-errors=true',
        #'--proxy=address:port',
        #'--proxy-type=http',
        #'--proxy-type=socks5',   # tor
        #'--proxy-auth=username:password',
      ]
    self.driver = webdriver.PhantomJS(service_args=args)
    #self.driver=webdriver.Firefox()
    if username is None or password is None:
      self.username, self.password = choice(account[self.method])

  # can't use in m.jd.com
  def jd(self):
    self.driver.get('https://passport.jd.com/new/login.aspx')
    name = self.driver.find_element_by_xpath('//*[@id="loginname"]')
    name.clear()
    name.send_keys(self.username)
    pwd = self.driver.find_element_by_xpath('//*[@id="nloginpwd"]')
    pwd.clear()
    pwd.send_keys(self.password)
    self.driver.find_element_by_xpath('//*[@id="loginsubmit"]').click()
    #self.driver.save_screenshot('jd.png')  #方便调试

  # can't use in www.jd.com
  def jd_m(self):
    self.driver.get('http://m.jd.com/')
    self.driver.save_screenshot('1.png')
    login = WebDriverWait(self.driver, 5).until(lambda driver: driver.find_element_by_xpath('//*[@id="index_searchLogin"]'))
    login.click()
    QQ = WebDriverWait(self.driver, 5).until(lambda driver: driver.find_element_by_xpath('//a[@report-eventid="MLoginRegister_QQLogin"]'))
    QQ.click()
    QQ.click() #why twice here??
    time.sleep(3)
    self.driver.switch_to.frame('ptlogin_iframe')
    self.driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()
    user = self.driver.find_element_by_xpath('//*[@id="u"]')
    user.clear()
    user.send_keys(self.username)
    pwd = self.driver.find_element_by_xpath('//*[@id="p"]')
    pwd.clear()
    pwd.send_keys(self.password)
    self.driver.find_element_by_xpath('//*[@id="login_button"]').click()

  def baidu(self):
    self.driver.get("http://www.baidu.com/")
    self.driver.find_element_by_xpath('//*[@id="u1"]/a[7]').click()
    user = WebDriverWait(self.driver, 6).until(lambda _: _.find_element_by_name("userName"))  # 需要等待，否则会报错
    user.clear()
    user.send_keys(self.username)
    pwd = self.driver.find_element_by_name("password")
    pwd.clear()
    pwd.send_keys(self.password)
    self.driver.find_element_by_id("TANGRAM__PSP_8__submit").click()

  def qufenqi(self):
    self.driver.get('http://passport.qufenqi.com/login?')
    name = self.driver.find_element_by_id('loginname')
    name.clear()
    name.send_keys(self.username)
    pwd = self.driver.find_element_by_id('password')
    pwd.clear()
    pwd.send_keys(self.password)
    #self.driver.save_screenshot('1.png')
    self.driver.find_element_by_id('submit').click()

  # www.weibo.cn
  # m.weibo.cn
  # can't use in www.weibo.com
  def sina(self):
    self.driver.get("https://passport.weibo.cn/signin/login?")
    WebDriverWait(self.driver, 6).until(lambda _: _.find_element_by_link_text('第三方帐号'))  # 需要等待，否则会报错
    user = self.driver.find_element_by_id("loginName")
    user.clear()
    user.send_keys(self.username)
    pwd = self.driver.find_element_by_id('loginPassword')
    pwd.clear()
    pwd.send_keys(self.password)
    self.driver.find_element_by_id('loginAction').click()

  def Zhihu(self):
    self.driver.get('https://www.zhihu.com/#signin')
    user = self.driver.find_element_by_name('account')
    user.clear()
    user.send_keys(self.username)
    pwd = self.driver.find_element_by_name('password')
    pwd.clear()
    pwd.send_keys(self.password)
    # self.driver.find_element_by_xpath('//*[@class="view view-signin"]/form/div[3]').click()  #在这里无效，只能用submit
    self.driver.find_element_by_xpath('//*[@class="view view-signin"]/form/div[3]').submit()

  def ttz(self):
    self.driver.get('https://www.ttz.com/')
    name = self.driver.find_element_by_id('Username')
    name.clear()
    name.send_keys(self.username)
    pwd = self.driver.find_element_by_id('Password')
    pwd.clear()
    pwd.send_keys(self.password)
    self.driver.find_element_by_id('login').click()

  # m.qzone.com(https://h5.qzone.qq.com/mqzone/index),can't use in www.qzone.com
  def qzone(self):
    self.driver.get("http://m.qzone.com")
    self.driver.find_element_by_xpath('//*[@id="guideSkip"]').click()
    name = self.driver.find_element_by_xpath('//*[@id="u"]')
    name.clear()
    name.send_keys(self.username)
    pwd = self.driver.find_element_by_xpath('//*[@id="p"]')
    pwd.clear()
    pwd.send_keys(self.password)
    self.driver.find_element_by_id('go').click()

  def gen_cookies(self, is_dict=True):
    func=getattr(self,self.method,None)
    if callable(func):
      func()
      time.sleep(5)
      cookie = self.driver.get_cookies()
      self.driver.quit()
      cookies = {_['name']: _['value'] for _ in cookie}
      if is_dict == False:
        cookies = ';'.join(('{}={}'.format(_['name'], _['value']) for _ in cookie))
      return cookies
    else:
      raise CloseSpider('Fatal error,no such method !')

  def test_cookies(self, url):
    r = requests.get(url, cookies=self.gen_cookies())
    with open('{}.html'.format(self.method), 'wb') as f:
      f.write(r.content)
