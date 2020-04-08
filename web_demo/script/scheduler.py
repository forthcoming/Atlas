from plan import Plan
import os

cron = Plan()

crontabDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crontab')

hours = 'hour.19 hour.20 hour.21 hour.22 hour.23 hour.0 hour.1 hour.2 hour.3 hour.4 hour.5 hour.6 hour.7'

########################################################################
# 定时spider
name = 'cron_spider'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.minute')



########################################################################
# phash计算
name = 'cron_phash'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.day', at=hours)


########################################################################
# 匹配计算
name = 'cron_match'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.day',  at=hours)


########################################################################
# 匹配计算
name = 'cron_itemmatch'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.day', at=hours)


########################################################################
# cluster计算
name = 'cron_cluster'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.day', at=hours)

########################################################################
# robot计算
name = 'cron_robot'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.day', at=hours)


#########################################################################
# 添加python killlall
cron.command('killall python', every='1.day', at='8:00')

if __name__ == '__main__':
    cron.run('update')