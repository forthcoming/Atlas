import base64
import requests
import re
from scrapy.exceptions import CloseSpider
from random import choice
from tools.dictionary import account


class Login:
    def __init__(self, method, username=None, password=None):
        self.s = requests.Session()
        self.method = method
        self.username = username
        self.password = password
        if username is None or password is None:
            self.username, self.password = choice(account[self.method])

    def __call__(self, is_dict=True):  # just for learning __call__ method !
        func = getattr(self, self.method, None)
        if callable(func):
            func()
            cookies = {_.name: _.value for _ in self.s.cookies}  # 等价 cookies=self.s.cookies.get_dict()
            if not is_dict:
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

    def baidu(self):
        req_url = "https://passport.baidu.com/v2/api/?login"
        token_url = "https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&class=login"  # 刷新https://passport.baidu.com/v2/?login

        self.s.get(req_url)  # 得到BAIDUID
        '''
        能拿到BAIDUID的请求都可以
        s.get('https://passport.baidu.com')
        s.get('http://www.baidu.com')
        s.get(req_url,verify=False)
        请求https类型地址,出现requests SSL: CERTIFICATE_VERIFY_FAILED）时加上verify=False即可
        '''
        r = self.s.get(token_url)
        data = {
            "username": self.username,
            "password": self.password,
            'tpl': 'pp',  # 登录的是m.baidu.com，应为电脑端是'tpl':'mn'
            "token": re.search(r'"token" : "([0-9a-z]+)",', r.text).group(1),
        }
        self.s.post(req_url, data=data)  # 此时已含有BDUSS字段

    def test_cookies(self, url):
        r = requests.get(url, cookies=self.__call__())
        with open('{}.html'.format(self.method), 'wb') as f:
            f.write(r.content)
