from celery import Celery
import time
from web_demo import db
from web_demo.common.model import RoomTrumpet

app = Celery('tasks')
app.config_from_object('sync_task.config')


@app.task(ignore_result=True)
def red_package(sec):
    result = RoomTrumpet.query.with_entities(RoomTrumpet.amount,RoomTrumpet.user_id).filter(RoomTrumpet.user_id == 1).first()
    time.sleep(sec)
    print(f'I have waited {sec} seconds')
    result1 = RoomTrumpet.query.filter(RoomTrumpet.id == 1).update({'amount':sec})  # 直接用result可以吗
    try:
        db.session.commit()
    except:
        db.session.rollback()


@app.task(name='tobedone',ignore_result=False)  # ignore_result是否保存结果到backend
def todo(x,y):
    '''
    celery控制台输出:
    [2020-04-09 13:05:53,794: INFO/MainProcess] Received task: tobedone[6c3dcd76-ce8f-43e7-89e3-486ef0054d5b]
    [2020-04-09 13:05:53,795: WARNING/ForkPoolWorker-2] result: 7
    [2020-04-09 13:05:53,795: INFO/ForkPoolWorker-2] Task tobedone[6c3dcd76-ce8f-43e7-89e3-486ef0054d5b] succeeded in 0.000496389999625535s: 7
    '''
    print(f'result: {x+y}')

    return x+y


@app.task
def test(sec):
    time.sleep(sec)
    print(f'I have waited {sec} seconds')
    return sec


'''
任务最多执行1+max_retries次
When you call retry it’ll send a new message, using the same task-id, and it’ll take care to make sure the message is delivered to the same queue as the originating task.
When a task is to be retried, it can wait for default_retry_delay time before doing so
'''
@app.task(max_retries=3,name='tasks.retry',default_retry_delay=4,autoretry_for=(Exception,))
def retry(sec):
    print('in retry')
    time.sleep(sec)
    1/0
    return sec


