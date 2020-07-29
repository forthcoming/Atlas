import requests,time,hashlib,smtplib
from lxml.html import fromstring 
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
    smtp.login(sendername, password)  # 括号中对应的是发件人邮箱账号|邮箱密码
    smtp.sendmail(sender_addr, receive, msg.as_string())
    smtp.quit()
    print("邮件发送成功")

def alibaba(keywords):
    res=requests.get('http://h5api.m.1688.com/h5/mtop.1688.offerservice.getoffers/1.0/?jsv=2.4.11&appKey=12574478')  # 获取_m_h5_tk和cookies信息
    cookies=res.cookies.get_dict()
    h5_tk=cookies['_m_h5_tk'].split('_')[0]
    t=int(time.time()*1000)  # t可以是任意整数,但必须保证url中的t跟string中的t一样,其他变量也类似,可以看出服务器也是用同样规则生成sign并同客户端传过来的sign进行对比
    data='{"sortType":"pop","keywords":"'+keywords+'","filtId":"","appName":"wap","beginPage":1,"pageSize":20}'
    string=f"{h5_tk}&{t}&12574478&{data}"
    sign=hashlib.md5(bytes(string,'utf-8')).hexdigest()
    r=requests.get(
        url=f'http://h5api.m.1688.com/h5/mtop.1688.offerservice.getoffers/1.0/?jsv=2.4.11&appKey=12574478&t={t}&sign={sign}&api=mtop.1688.offerService.getOffers&v=1.0&type=jsonp&dataType=jsonp&callback=mtopjsonp20&data={data}',
        headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        },
        cookies=cookies,
    )
    return r.text
    '''
    import requests,json
    from urllib.parse import urlencode
    from lxml.html import fromstring
    
    keywords=[
        '调制解调器',
        '充电器',
    ]
    headers={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'cookie': '_bl_uid=Chjwegy6zXv2ht1zkw9R9InpXahU; __sw_ktsz_count__=1; UM_distinctid=16344c8947110db-0467889a00c728-3c3c5905-1fa400-16344c8947217a; cna=MIBTEx27h2ICAS9LSR2fQyLi; __last_loginid__=avatar10086; last_mid=b2b-1863067459; ali_ab=47.52.203.97.1525867383322.3; JSESSIONID=5S8ZQfY-48eZ4LDGgjTiabrZX8-zS2GYrQ-mo37; cookie2=1e07bec3921cfa1c6bae8cd6e9c02f12; t=36d71d71aae435537f07280dbb8679b1; _tb_token_=e7f8b8e1be773; lid=avatar10086; alisw=swIs1200%3D1%7C; __cn_logon_id__=avatar10086; __cn_logon__=true; hng=CN%7Czh-CN%7CCNY%7C156; csg=13fc0c4d; ali_apache_track=c_mid=b2b-1863067459|c_lid=avatar10086|c_ms=1; ali_apache_tracktmp=c_w_signed=Y; LoginUmid=dGKw6Kz%2BE9ii5pE0au50fzwGRpCoSIsWdaY0AND%2B8dy89QAyb6jGqQ%3D%3D; tbsnid=6OHRvE29cPnvTFKpKuMc6gCFYYzknWlhbjJyCRge1Ws6sOlEpJKl9g%3D%3D; cn_tmp="Z28mC+GqtZ3vyGuZxZA+PFbUvF+qqQGLIMh3SxVeX9NbNdZ2IhiqyQbVBLGri8jW54wGDPlJkOHxdPyVafHyaxElP+6AIaUl+sMbuzCXtHJCSQOSIxhtCgF6+ZxNK9riqis50waLv/m/kAvylLhBynM51Bhsr29ctGWlz5e2lipVnZMxl2hyFGdKiDBhXuxbGd0NVh6zH08HL06WhIkLwZQavmZEektQI/zK2SOuoCxckUWNZpQwbQ=="; userID=4d6Tt8Q3nPAQ6sRcDanFBkV%2FvNql7OT%2BkbDbkKjOjk46sOlEpJKl9g%3D%3D; userIDNum=JBZ1q4Yd%2B5zPePDjweXi2A%3D%3D; _cn_slid_=InO19c2ocg; _csrf_token=1526003948601; h_keys="%u8c03%u5236%u89e3%u8c03%u5668#%u7537%u978b#%C4%D0%D0%AC#%u9422%u70fd%u7037#%u5973%u88c5#%u7537%u978b44-48%u7801#%u70ed%u6c34%u5668#%u70ed"; alicnweb=homeIdttS%3D65334365880598888314397053956155791822%7ChomeIdttSAction%3Dtrue%7Clastlogonid%3Davatar10086%7Ctouch_tb_at%3D1526005507726%7Cshow_inter_tips%3Dfalse; ad_prefer="2018/05/11 10:54:28"; _tmp_ck_0="LUGYM4%2BaK%2FXE7vd5cGGIYvrkprmwfAHPnYwPiWJh7ShOqRagovRse91%2FG0dNUTJOgVJ5SsIjLv7LJqw5%2FP1faNKrXcvmmDquttH392ulgTdboGxSrLkfIy8g0OSVYIrIVDF4ZkOoEovLxY7%2BpUAYg0nYeOV%2FV%2B0oKLY3SISQQuHVVErkO8j4TVtlQKCzxXg9nT9S3k3muqZwKfF6sX8th42BNU5tSdzEA9tVdZRLusfgUWPGmSpvsVo3QPboJMWit0DxcSI5cHJRfZcjgrb9wFUzJvK0BOCH20gKxMVutslZAiJiqI3BtYHS5DmwkgZk2mRAF0Ce7ZLGD1AP1pap14dhwlkv2lP6c6%2B7chS%2BgJJLb5hDlsq4ffd485t4teWNeB26yEe4IOcoSsAGwqmjm06YLuqiS6Ij3hwubf%2FvDXVahwVmBkcTxMeht0eR2fcuWoTDz29U%2FaojAZvjNp1g82ZaRE%2FMd80DdTt0dLODb6PriPcY8gkj5IW3irB9htJRO1o2rAdxWdUVO%2F18Hxhm9g%3D%3D"; isg=BIiIasRgRl57Y6rdEVMLlneMWfZamYduXAw7lUI51YP2HSiH6kG8yx6fkf1tLaQT',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    }
    
    params={
        'pageSize':'100',
        'asyncCount':'100',
        'startIndex':'0',
        'descendOrder':'true',
        'sortType':'va_rmdarkgmv30',
    }
    with open('1688.json','w',encoding='utf-8') as f:
        for keyword in keywords:
            for page in range(1,2):
                params['keywords']=keyword
                params['beginPage']=page
                r=requests.get(headers=headers,url=f"https://s.1688.com/selloffer/offer_search.htm?{urlencode(params,encoding='gbk')}")
                res=fromstring(r.content)
                for li in res.xpath('//*[@id="sm-offer-list"]/li'):
                    data={
                        'rank':li.xpath("@t-rank")[0],
                        'url':li.xpath("div[2]/div[1]/a/@href")[0],
                        'title':li.xpath("div[2]/div[1]/a/@title")[0],
                        'img':li.xpath("div[2]/div[1]/a/img/@src")[0],
                        'price':li.xpath("string(div[2]/div[2]/span)"),
                    }
                    f.write(json.dumps(data)+'\n')
    '''


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
    print(translate('今天星期五,心情大好,吃完饭准备跟朋友去抓鱼.'))

    content = """
    <p>Python 数据部程序运行异常</p>
    <b>请及时登录服务器查看程序状态</b>
    """
    send_mail(content, 'tao@qq.com','这是标题')
