from celery.schedules import crontab
from kombu import Exchange, Queue
import re

'''
celery multi start -A sync_task.tasks worker -l=info -B -Q todo,test -f=web_demo/logs/%n.log  # 后台启动
celery -A sync_task.tasks worker -l=info -B -s web_demo/logs/celerybeat-schedule -Q todo,test -f=web_demo/logs/%n.log
1. -B开启定时任务,Please note that there must only be one instance of this service.otherwise you’d end up with duplicate tasks. 
2. -Q,only process the todo and test queue,如果多个celery实例处理相同的queue,则任务在他们之间随机分配,不加Q则会处理task_queues中的所有queue
3. -s,Beat needs to store the last run times of the tasks in a local database file (named celerybeat-schedule by default),u can specify a custom location

 -------------- celery@macbook.local v4.4.2 (cliffs)
--- ***** ----- 
-- ******* ---- Darwin-18.7.0-x86_64-i386-64bit 2020-04-09 22:35:13
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x102f09890
- ** ---------- .> transport:   redis://localhost:6379/1
- ** ---------- .> results:     redis://localhost:6379/2
- *** --- * --- .> concurrency: 2 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> test             exchange=test(direct) key=test
                .> todo             exchange=todo(direct) key=todo

[tasks]
  . sync_task.tasks.test
  . tobedone
说明:
[tasks]包含sync_task.tasks中的所有task
[queues]包含Q指定的消息队列名
 
celery的配置, 修改配置需要重启celery 和 celery beat
celery的broker,backend,task,调用task的项目,都可以在不同机器上
If the queue name is defined in task_queues it will use that configuration
if it’s not defined in the list of queues Celery will automatically generate a new queue for you (depending on the task_create_missing_queues option)
'''


worker_concurrency = 2  # 子进程个数


task_queues = [
    Queue('celery', Exchange('celery'), routing_key='celery'),  # 默认消息队列,The routing key also called binding key.
    Queue('test', Exchange('exchange_test'), routing_key='routing_test'),

    Queue('todo', Exchange('exchange_todo',type='direct'), routing_key='routing_todo'), # smembers _kombu.binding.exchange_todo => routing_todo1\x06\x16\x06\x16todo1, routing_todo\x06\x16\x06\x16todo
    Queue('todo1', Exchange(name='exchange_todo',type='direct'), routing_key='routing_todo1'),
]
'''
If the order of matching patterns is important you should specify the router in items format instead:
task_routes = ([
    ('sync_task.tasks.*', {'queue': 'web_demo'}),
    (re.compile(r'(video|image)\.tasks\..*'), {'queue': 'media'}),
])
没有在task_routes中指定的任务用默认队列celery
交换机名称,routing_key必须与task_queues中的交换机名称,routing_key一致
交换机必须与routing_key同时出现才会有效果,这样才能定位到具体哪个queue,也可以直接指定queue,2选1
'''
task_routes = {
    'sync_task.tasks.test': {'exchange':'exchange_todo','routing_key':'routing_todo1'},
    'tobedone': {'exchange':'exchange_todo','routing_key':'routing_todo'},
    # 'tobedone': {'queue': 'test'},  # 每个queue对应broker中的一个list,用于存放任务,如果queue不存在task_queues中会自动创建,同一个queue任务按先来先消费原则
}


'''
消息代理器配置, redis用例: redis://:password@hostname:port/db_number
celery: list,无过期时间,内容对应unacked的value,celery重启后会接着执行未执行完的任务,unacked和unacked_index将被删除,并且其中的任务退回到celery列表,回写操作由worker在临死前完成,所以在关闭worker时为防止任务丢失,请务必使用正确的方法停止它
unacked_index: zset,无过期时间,score是加入时间戳,field对应unacked的field,上限默认为8,这个是被worker接收但还没开始执行的task列表(任务来自多个消息队列)
unacked: hash,无过期时间,value大致[{"body": "W1s0LCAzXSwge30sIHsiY2FsbGJhY2tzIjogbnVsbCwgImVycmJhY2tzIjogbnVsbCwgImNoYWluIjogbnVsbCwgImNob3JkIjogbnVsbH1d", "content-encoding": "utf-8", "content-type": "application/json", "headers": {"lang": "py", "task": "tobedone", "id": "d0bc737e-e5fe-4ca1-b6ee-1ab5e78e85a9", "shadow": null, "eta": null, "expires": null, "group": null, "retries": 0, "timelimit": [null, null], "root_id": "d0bc737e-e5fe-4ca1-b6ee-1ab5e78e85a9", "parent_id": null, "argsrepr": "(4, 3)", "kwargsrepr": "{}", "origin": "gen9645@macbook.local"}, "properties": {"correlation_id": "d0bc737e-e5fe-4ca1-b6ee-1ab5e78e85a9", "reply_to": "5afc8388-8624-3c0b-90f3-ba3c5c2c38d3", "delivery_mode": 2, "delivery_info": {"exchange": "", "routing_key": "celery"}, "priority": 0, "body_encoding": "base64", "delivery_tag": "02294572-2692-4176-a505-208d515e0105"}}, "", "celery"]
'''
broker_url = 'redis://localhost:6379/1'


'''
保存(前提是任务的ignore_result=False)任务return的结果,否则保存null,类型是string,过期时间由result_expires控制
127.0.0.1:6379[2]> get celery-task-meta-6c3dcd76-ce8f-43e7-89e3-486ef0054d5b
{"status": "SUCCESS", "result": 7, "traceback": null, "children": [], "date_done": "2020-04-09T05:25:06.113925", "task_id": "6c3dcd76-ce8f-43e7-89e3-486ef0054d5b"}
'''
result_backend = 'redis://localhost:6379/2'
result_expires = 2000  # 任务结果存储周期


task_annotations = {
    # 'tobedone': {'rate_limit': '3/m'},   # 3/m代表这个任务在一分钟内最多只能有3个被执行(20s内最多只有一个任务被执行)
    'sync_task.tasks.test': {'rate_limit': '4/s'},
}


'''
The visibility timeout defines the number of seconds to wait for the worker to acknowledge the task before the message is redelivered to another worker
因此耗时任务会出现被执行多次的情况,解决方案如下:
1. 任务幂等
2. celery_once
3. visibility_timeout设置大一些
'''
broker_transport_options = {'visibility_timeout': 7200}


# pickle支持比json更广的序列化类型,但需要反序列化才可读,如果任务或者返回值包含json无法序列化的数据类型,则只能用pickle
accept_content = ['json','pickle']
task_serializer = 'pickle'
result_serializer = 'pickle'


'''
使用前在 http://tool.lu/crontab/ 测试一遍
schedule指定多久往broker中发送一个指定的task,并不是多久执行一次任务,执行任务的频率由task_annotations控制
args: Positional arguments (list or tuple). 
kwargs: Keyword arguments (dict).
options: Execution options (dict).This can be any argument supported by apply_async() – exchange, routing_key, expires, and so on.
'''
beat_schedule = {
    'test_celery_beat': {
        'task': 'tobedone',
        'schedule': crontab(hour=19, minute=37, day_of_week=1),  # Executes every Monday at 19:37,如果enable_utc=True,则需要当前时间-8小时
        # 'schedule': 5,
        'args': (3,2),
        'kwargs': {},
        'options':{},
    },
}
enable_utc = False  # 默认为True,当前时间-8小时=utc时间
