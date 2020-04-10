from celery import Celery
import time


app = Celery('tasks')
app.config_from_object('sync_task.config')


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
