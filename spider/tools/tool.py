import requests,time,hashlib
from lxml.html import fromstring
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

ADDRESS = 'itnotitfysercices@qq.com'
NAME='itnotitfysercices@qq.com'
PASSWORD = 'Love2017!'
HOST = 'smtp.qiye.163.com'
PORT = '465'

def send_mail(content, receive, title,sender_addr=ADDRESS,sendername=NAME,password=PASSWORD,host=HOST,port=PORT):

    msg = MIMEMultipart('related')
    msg.attach(MIMEText(content, 'html', 'utf-8'))
    msg['Subject'] = Header(title, 'utf-8')
    msg['From'] = Header("综合项目部", 'utf-8')
    msg['To'] = Header("Python组", 'utf-8')

    smtp = smtplib.SMTP_SSL(host, port)  # 发件人邮箱中的SMTP服务器,端口
    smtp.login(sendername, password)  # 括号中对应的是发件人邮箱账号、邮箱密码
    smtp.sendmail(sender_addr, receive, msg.as_string())
    smtp.quit()
    print("邮件发送成功")

def alibaba(keywords):
    res=requests.get('http://h5api.m.1688.com/h5/mtop.1688.offerservice.getoffers/1.0/?jsv=2.4.11&appKey=12574478')  # 获取_m_h5_tk和cookies信息
    
    h5_tk=res.cookies.get_dict()['_m_h5_tk'].split('_')[0]
    t=int(time.time()*1000)
    data='{"sortType":"pop","keywords":"'+keywords+'","filtId":"","appName":"wap","beginPage":1,"pageSize":20}'
    string=f"{h5_tk}&{t}&12574478&{data}"
    sign=hashlib.md5(bytes(string,'utf-8')).hexdigest()
    r=requests.get(
        url=f'http://h5api.m.1688.com/h5/mtop.1688.offerservice.getoffers/1.0/?jsv=2.4.11&appKey=12574478&t={t}&sign={sign}&api=mtop.1688.offerService.getOffers&v=1.0&type=jsonp&dataType=jsonp&callback=mtopjsonp20&data={data}',
        headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        },
        cookies=res.cookies.get_dict(),
    )
    return r.text

def translate(word):
    s=requests.Session()
    s.get('http://fanyi.youdao.com')   #作用是获取cookie
    s.headers.update({                 #cookie,referer,user-agent缺一不可
        'Referer':'http://fanyi.youdao.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.39 Safari/537.36',
    })
    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    data = {
        'i':word,
        'from':'AUTO',
        'to':'AUTO',
        'smartresult':'dict',
        'client':'fanyideskweb',
        'salt':str(int(time.time()*1000)),
        'doctype':'json',
        'version':'2.1',
        'keyfrom':'fanyi.web',
        'action':'FY_BY_REALTIME',
        'typoResult':'false',
    }
    data['sign'] = hashlib.md5(bytes(data['client']+data['i']+data['salt']+"ebSeFb%=XZ%T[KZ)c(sy!",'utf-8')).hexdigest()
    r=s.post(url=url,data=data,)
    return r.json()

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
    # foo=V2ex()
    # foo.login()
    # foo.sign()
    print(translate('今天星期五，心情大好，吃完饭准备跟朋友去抓鱼'))

    content = """
    <p>Python 数据部程序运行异常</p>
    <b>请及时登录服务器查看程序状态</b>
    """
    send_mail(content, 'tao@qq.com','这是标题')
