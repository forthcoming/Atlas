# coding=utf-8
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
# 邮箱配置
SP_MAIL_ADDRESS = 'itnotitfysercices@stosz.com'
SP_MAIL_SENDER = 'Asoulwangxiaohei'
SP_MAIL_SMTP = 'smtp.qiye.163.com'
SP_MAIL_SMTP_PORT = '465'
SP_MAIL_LOGINNAME = 'itnotitfysercices@stosz.com'
SP_MAIL_PASSWORD = 'Love2017!'

reload(sys)
sys.setdefaultencoding('utf-8')

def sendEmail(arrayRecive, strHtmlBody, strTitle,
              sender_addr=SP_MAIL_ADDRESS,
              sendername=SP_MAIL_LOGINNAME,
              password=SP_MAIL_PASSWORD,
              host=SP_MAIL_SMTP,
              port=SP_MAIL_SMTP_PORT ):

    msgRoot = MIMEMultipart('related')
    msgRoot.attach(MIMEText(strHtmlBody, 'html', 'utf-8'))
    msgRoot['Subject'] = Header(strTitle, 'utf-8')
    msgRoot['From'] = Header("CUCKOO-综合项目部", 'utf-8')
    # msgRoot['To'] = Header("Python组", 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(host, port)  # 发件人邮箱中的SMTP服务器，端口
        smtpObj.login(sendername, password)  # 括号中对应的是发件人邮箱账号、邮箱密码
        smtpObj.sendmail(sender_addr, arrayRecive, msgRoot.as_string())
        smtpObj.quit()
        print "邮件发送成功"

    except smtplib.SMTPException as e:
        print e, "Error: 无法发送邮件"

if __name__ == '__main__':
    mail_msg = """
    <p>Python Atlas-%s程序运行异常</p>
    <p>
        告警主机:{HOSTNAME1}
        告警时间:{EVENT.DATE} {EVENT.TIME}
        告警等级:{TRIGGER.SEVERITY}
        告警信息:{TRIGGER.NAME}
        告警项目:{TRIGGER.KEY1}
        问题详情:{ITEM.NAME}:{ITEM.VALUE}
        当前状态:{TRIGGER.STATUS}:{ITEM.VALUE1}
        事件ID:{EVENT.ID}
    </p>
    <p>请及时登录%s服务器查看程序状态</p>
    """ % ('xxxx', '192.168.105.xx')
    # 标题
    subject = 'Python 程序运行异常！'
    sendEmail('qiang@qq.com', mail_msg, subject)