from celery import Celery
import time,os
from web_demo import db
from web_demo.common.model import RoomTrumpet


app = Celery('tasks')
app.config_from_object('sync_task.config')


@app.task(ignore_result=True)
def red_package(sec):
    '''
    celery子进程worker调用,db对象由celery主进程读__init__.py文件创建,由于没有shutdown_session对session做善后工作,当有异常如数据库重启导致连接丢失,需要手动rollback
    session执行过程中,如果数据库重启或其他原因导致连接丢失时,sqlalchemy会将当前连接返回到连接池(此时需要手动rollback回滚代码层事务),下次再取出时被丢弃
    如果查询完不提交,连接会在当前进程一直处于checkout状态(不进入连接池),事物也会一直存在
    '''
    connection_id = 0
    print('pid:{} connection_id:{},status:{}'.format(os.getpid(), connection_id, db.engine.pool.status()))
    try:
        # RoomTrumpet.query.count()  # 禁止使用该条语句,效率很低
        RoomTrumpet.query.with_entities(RoomTrumpet.amount,RoomTrumpet.user_id).filter(RoomTrumpet.user_id == 1).first()
        connection_id = db.session.execute('select connection_id();').first()[0]
        print('pid:{} connection_id:{},status:{}'.format(os.getpid(),connection_id,db.engine.pool.status()))
        time.sleep(sec)
        RoomTrumpet.query.filter(RoomTrumpet._id == 1).update({'amount':sec})  # 只会update,不会select
        db.session.commit()
    except Exception as e:
        print('Exception:{}'.format(e))
        print('pid:{} connection_id:{},status:{}'.format(os.getpid(),connection_id,db.engine.pool.status()))
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


