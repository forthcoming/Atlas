from sync_task.tasks import *

result = todo.delay(0,3)   # 如果celery服务没起来也不会报错,这些任务会先保存到任务队列celery中
print('task_id: ',result)  # 返回的是任务ID: 6c3dcd76-ce8f-43e7-89e3-486ef0054d5b


print(test.delay(1))

app.send_task()