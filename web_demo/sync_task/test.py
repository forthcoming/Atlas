from .tasks import *


result=test.delay(5)
# celery的broker,backend,task,调用task的项目,都可以在不同机器上
# result=app.send_task('tobedone',[3,4],{})  # 任务名错了不报错,字典传param=param型参数,适于远程调用
print(result.get(timeout=4))
print(result.id)
print(result.ready())  # returns whether the task has finished processing or not
# print(result.traceback)

