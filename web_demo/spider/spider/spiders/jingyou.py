import requests,re,time
from lxml.html import fromstring
from selenium import webdriver
from sqlalchemy import create_engine,text
from sqlalchemy.exc import IntegrityError
from random import random

# -- https://www.jyeoo.com
# DROP TABLE IF EXISTS `subject`;
# CREATE TABLE `subject`  (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `grade` varchar(32)  NOT NULL DEFAULT "",
#   `subject` varchar(32)  NOT NULL DEFAULT "",
#   `url` varchar(255)  NOT NULL DEFAULT "",
#   PRIMARY KEY (`id`)
# ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

# -- https://www.jyeoo.com/physics2/ques/search
# DROP TABLE IF EXISTS `navigation`;
# CREATE TABLE `navigation`(
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `pk` varchar(128) NOT NULL DEFAULT "",
#   `title` varchar(128) NOT NULL DEFAULT "",
#   `position` INT UNSIGNED, -- 位置
#   `pid` int UNSIGNED NOT NULL, -- 关联父id
#   `sid` int UNSIGNED NOT NULL, -- 关联subject的id
#   PRIMARY KEY (`id`)
# ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

# DROP TABLE IF EXISTS `degree`;
# CREATE TABLE `degree`  (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `setting` varchar(32)  NOT NULL DEFAULT "",
#   `detail` varchar(32)  NOT NULL DEFAULT "",
#   `filter_name` varchar(32)  NOT NULL DEFAULT "",
#   `filter_value` varchar(16) NOT NULL DEFAULT "",
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `uniq_filter` (`filter_name`,`filter_value`)
# ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

# 后面还需要根据degree表给题目打标签
# DROP TABLE IF EXISTS `question`;
# CREATE TABLE `question`  (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `nid` int NOT NULL,  -- 关联navigation的id
#   `is_completed` tinyint NOT NULL default 0,
#   `question_id` varchar(128) NOT NULL DEFAULT "",
#   `detail_url` varchar(128) NOT NULL DEFAULT "",
#   `content` text,
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `uniq_question_id` (`question_id`)
# ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

engine = create_engine(
    "mysql+pymysql://root:root@127.0.0.1:3306/test?charset=utf8mb4",
    echo=False,      # 是否记录日志,True我们会看到所有生成的SQL
    max_overflow=1, # 超过连接池大小外最多创建的连接(即最大连接数=max_overflow+pool_size),对应QueuePool的max_overflow构造参数
    pool_timeout=30, # 对应QueuePool的timeout构造参数,Queue的self.get的超时时间,The number of seconds to wait before giving up on returning a connection.
    pool_size=3,    # 连接池大小,对应QueuePool的pool_size构造参数,Queue的self.maxsize;With QueuePool, a pool_size setting of 0 indicates no limit; to disable pooling, set poolclass to NullPool instead.
    pool_recycle=4, # MySQL有关闭(连续wait_timeout时间内未操作过)闲置一段时间连接行为,默认8小时,为避免出现此问题,pool_recycle可确保在池中连续存在固定秒数的连接在下次取出时将被丢弃并替换为新的连接(惰性检测,将pool_recycle改小,pool_use_lifo=False,然后show processlist观察id很好验证)
    pool_pre_ping=True,
    pool_use_lifo=False,  # lifo mode allows excess connections to remain idle in the pool, allowing server-side timeout schemes to close these connections out.
)


host="http://www.jyeoo.com"

def main():
    r=requests.get(host)
    tree = fromstring(r.content)
    for li in tree.xpath("//ul[@class='sub-cont']/li"):
        grade=li.xpath("string(div[@class='sub-tlt']/b)")
        for sub_li in li.xpath("div[@class='sub-list']//li"):
            subject=sub_li.xpath("string(span)")
            for detail in sub_li.xpath(".//a"):
                url=host+detail.xpath("@href")[0]
                if "report" in url:
                    continue # 过滤掉试卷类型的网页
                with engine.connect() as conn:
                    sql = text("insert into subject(grade,subject,url) values('{}','{}','{}');".format(grade,subject,url))
                    result = conn.execute(sql)
                    pid = result.lastrowid
                extract_category(url,pid)

# 未登录状态下，大概3s后会强制跳转到登陆界面(不影响数据采集)
def extract_category(url,sid):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片加载
    # options.add_argument('--proxy-server=http://127.0.0.1:6789') # 代理
    driver = webdriver.Chrome(options=options, executable_path='/usr/local/Cellar/chromedriver')
    driver.get(url)
    tree = fromstring(driver.page_source)

    for idx,li in enumerate(tree.xpath("//div[@class='divCategory']/ul/li")):
        extract_li(li, 0, sid, idx)

    for tr in tree.xpath("//table[@class='degree']//tr"):
        setting = tr.xpath("string(th)")
        for a in tr.xpath(".//a"):
            detail = a.xpath("string(.)")
            onClick = a.xpath("@onclick")[0]
            res = re.findall(r"'([a-z0-9]*)'",onClick)
            if len(res)==2:
                filter_name,filter_value=res
                with engine.connect() as conn:
                    sql = text("insert into degree(setting,detail,filter_name,filter_value) values('{}','{}','{}','{}');".format(setting,detail,filter_name,filter_value))
                    try:
                        conn.execute(sql)
                    except IntegrityError:
                        pass
    driver.quit()

def extract_li(li,pid,sid,position):
    category=li.xpath("a/@pk")[0]
    title = li.xpath("a/@title")[0]
    with engine.connect() as conn: # 每调用一次,按engine的连接池配置规则取出一条连接资源,块结束才会归还该资源,默认autocommit=True(每条语句都包含一个事务的开始与结束)
        sql = text("insert into navigation(pk,title,position,pid,sid) values('{}','{}',{},{},{});".format(category,title,position,pid,sid))
        result=conn.execute(sql)
        pid = result.lastrowid
    for idx,sub_li in enumerate(li.xpath("./ul/li")):
        extract_li(sub_li, pid, sid, idx)

def get_question_info(subject_id,max_page_index):
    # 怎么获取这个cookie
    header={
        'Cookie':'QS_ED=11; QS_BK=df7b4c0a-9833-49e8-a28c-1bd9ba05bb0f; QS_GD=18; remind_check=1; jyean=cIGc-aAMvL7gkfRVo3IRv0l_7kVR_IxiPrbwHcbnKqn-Wb-px2RPH_UPmC975EoIRgdwCYmRwMsR36ogVZlKpIEhYZEKLIYD_30XJXQ2jqYIo_Ov2ds0LMTaM9qEwYVc0; gr_user_id=8a97e2ef-ffcf-4c57-8500-94bd6019199f; __RequestVerificationToken=4kBgLy6t-8IIBHUE_8YZd5kn3AjZS6QsoE2t1USLY91no_gLL9ixKsO2A-ur6HflEnKrN9aeyT_9yTCiveetTYASqqWXukNcKQkmqYCsfZQ1; jye_notice_nopayfromthird=1; jy_report_index_ed=; jy_report_index_gd=; jy_user_lbs_chemistry2=; jye_cur_complete_dig_0408cb80-b9a8-4f9c-9e79-702ecbf7eee7=serverUpgrade; JYEEO:GUIDE:NEWUSER_0408cb80-b9a8-4f9c-9e79-702ecbf7eee7=1-1-0-0; challenge21=1|2022/5/31 3:02:00|0|false; jy_user_lbs_politics2=; jy_user_lbs_chinese3=; jy_user_lbs_physics=; jy_user_lbs_history2=; jy_user_lbs_math3=; resource_last_subject=1-44; 1_44_resource_edition_grade=71997-71998; jye_math3_paper_q=afd13af0-1958-4812-8441-139d2934b40a~7a7cfb0d-c485-4ec5-8e9b-f860c0e1e071~; jy_user_lbs_math2=; jy_user_lbs_math=; jy_user_lbs_chemistry=; jy_user_lbs_physics2=; jy_user_lbs_bio2=; jy_user_lbs_english3=; jy_user_lbs_math0=; jy_user_lbs_chinese=; jy_report_index_last_subject=politics3; jy_user_lbs_politics=; jy_user_lbs_geography=; jye_cur_complete_dig_b1837195-33de-4fec-aa24-e0f44af8e6ba=serverUpgrade; JYEEO:GUIDE:NEWUSER_b1837195-33de-4fec-aa24-e0f44af8e6ba=1-1-0-0; jy_user_lbs_english2=; jye_cur_complete_dig_2b88e92e-8a80-4383-9e83-ade14a0c8c0e=serverUpgrade; a8f7777aa0f1f0f8_gr_last_sent_sid_with_cs1=4930e709-182d-4f8c-9d25-73f7ffb15b61; a8f7777aa0f1f0f8_gr_last_sent_cs1=43799316; a8f7777aa0f1f0f8_gr_session_id=4930e709-182d-4f8c-9d25-73f7ffb15b61; a8f7777aa0f1f0f8_gr_session_id_4930e709-182d-4f8c-9d25-73f7ffb15b61=true; LF_Email=13189614176; jy=58CFE0F7766F0395F128EAF45C7E7C72F0D3A2F2DB4700A3B3C7B1838AA0D585750B14E9145FCB41C5B0A96C36181410FEC410F2117ACA06DC4C1B62B38241C7DFA5C2C3C37F12A5A2E204C03DA4A7E8CA7158FE3C0308C677092642D5454E6A2555D13853437C2AE62E47D0C6BDFAF8DCA44D2BC2433F2793DC816A248A0CCA8DE0A67FCD38BD63E013799894FE41ACBEDFB05FAB8109A571A63DA65AA2A1E59DDC0F3133333A04836F3108A84E50D06D899B6AEE10FDDE2BFDD33787538F5F269EE88E31C0DA9C2E2703AD97D5B14F1C2A5F33404E201C925A985B1CD63C638E51A018032DECCD19CB1B92BCAB58D824CA7D37AFA725441DFDD1E3C031A5CA72C9DEB178BAE6CFCF7CA86497917DE751261A2CCC1F2991CB6E952F1100DD28FB6F4125AC59458EBA5B78EB146BB30B83B3F23150D27CAB3418CB5B95DA08FB6F35925344A81AB4386DA0020F81AF3D; JYEEO:GUIDE:NEWUSER_2b88e92e-8a80-4383-9e83-ade14a0c8c0e=1-1-0-0; jye_cur_sub=chemistry2; a8f7777aa0f1f0f8_gr_cs1=43799316',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'max-age=0',
        'Proxy-Connection': 'keep-alive',
        'Host': 'www.jyeoo.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
    }
    session = requests.Session()
    session.headers = header

    with engine.connect() as conn:
        sql = text("select url,pk,navigation.id from subject join navigation on subject.id=navigation.sid where subject.id={};".format(subject_id))
        result = conn.execute(sql).fetchall()

    for _url,pk,nid in result:
        url=_url.replace("search","partialques") + "?f=0&lbs=&pd=1&mindg=0.1&maxdg=0.9"
        for page_index in range(1, max_page_index+1):
            page_url = "{}&q={}&pi={}".format(url,pk,page_index)
            r = session.get(page_url)
            tree=fromstring(r.text)
            print(r.text)
            for li in tree.xpath("//li[@class='QUES_LI']"):
                question_id = li.xpath("fieldset/@id")[0]
                detail_url = "{}/{}".format(_url,question_id)
                detail_url = detail_url.replace("search","detail")
                with engine.connect() as conn:
                    sql = text("insert into question(nid,question_id,detail_url) values('{}','{}','{}');".format(nid,question_id,detail_url))
                    try:
                        conn.execute(sql)
                    except IntegrityError:
                        print(sql)
                        pass
            time.sleep(8*random())

def get_question_answer():
    with engine.connect() as conn:
        sql = text("select id,detail_url from question where is_completed=0;")
        result = conn.execute(sql).fetchall()
    for _id,detail_url in result:
        print(_id,detail_url)


if __name__ == '__main__':
    # 第一步先执行main(),大概2分钟完成
    # 第一步并行执行get_question_info和get_question_answer
    # main()
    # get_question_info(5,4)
    get_question_answer()

