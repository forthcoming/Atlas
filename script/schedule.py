from plan import Plan
import os

cron = Plan()

crontabDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crontab')

########################################################################
# 定时spider
name = 'cron_1688_spider'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.minute')



########################################################################
# phash计算
name = 'cron_phash'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.minute')


########################################################################
# 匹配计算
name = 'cron_match'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.minute')


########################################################################
# 匹配计算
name = 'cron_itemmatch'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.minute')


########################################################################
# cluster计算
name = 'cron_cluster'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='1.minute')

if __name__ == '__main__':
    cron.run('update')