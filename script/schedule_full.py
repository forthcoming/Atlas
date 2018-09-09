from plan import Plan
import os
from schedule import *

cron = Plan()

crontabDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crontab')

########################################################################

# 定时 cuckoo spider
name = 'cron_cuckoo_spider'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='6.hour')


########################################################################

# 定时 cuckoo spider
name = 'cron_bi_spider'
cron.command('flock -xn /tmp/%s.lock -c %s.sh' % (name, os.path.join(crontabDir, name)), every='8.hour')




if __name__ == '__main__':
    cron.run('update')