from celery import Celery
import time

app = Celery('task')
app.config_from_object('sync.config')

@app.task(name='tobedone',ignore_result=False)
def todo(x,y):
    print(f'result: {x+y}')
    return x+y # return变量保存数据到redis

@app.task
def test(sec):
    time.sleep(sec)
    print(f'I have waited {sec} seconds')
    return sec
