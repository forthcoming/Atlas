import requests,time,hashlib

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

if __name__=='__main__':
    print(translate('今天星期五，心情大好，吃完饭准备跟朋友去抓鱼'))
