from sync_task.tasks import *

result = todo.delay(4,3)
print('task_id: ',result)  # 返回的是任务ID: 6c3dcd76-ce8f-43e7-89e3-486ef0054d5b
