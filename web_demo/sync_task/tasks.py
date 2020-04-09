from celery import Celery
import time


app = Celery('tasks')
app.config_from_object('sync_task.config')


@app.task(name='tobedone',ignore_result=False)  # ignore_result是否保存结果到backend
def todo(x,y):
    '''
    [2020-04-09 13:05:53,794: INFO/MainProcess] Received task: tobedone[6c3dcd76-ce8f-43e7-89e3-486ef0054d5b]
    [2020-04-09 13:05:53,795: WARNING/ForkPoolWorker-2] result: 7
    [2020-04-09 13:05:53,795: INFO/ForkPoolWorker-2] Task tobedone[6c3dcd76-ce8f-43e7-89e3-486ef0054d5b] succeeded in 0.000496389999625535s: 7
    '''
    print(f'result: {x+y}')

    '''
    设置了backend前提下,return变量保存到redis,否则null会保存到redis,类型是string,且有过期时间
    127.0.0.1:6379[2]> get celery-task-meta-6c3dcd76-ce8f-43e7-89e3-486ef0054d5b
    "{\"status\": \"SUCCESS\", \"result\": 7, \"traceback\": null, \"children\": [], \"date_done\": \"2020-04-09T05:25:06.113925\", \"task_id\": \"6c3dcd76-ce8f-43e7-89e3-486ef0054d5b\"}"
    '''
    return x+y

@app.task
def test(sec):
    time.sleep(sec)
    print(f'I have waited {sec} seconds')
    return sec