from sync_task.tasks import *


'''
如果celery服务没起来也不会报错,这些任务会先保存到任务队列celery中,任务名错了不报错,字典传param=param型参数,适于远程调用
the task will execute, at the earliest, countdown seconds after the message was sent.
'''
# result=app.send_task('tobedone',[3],{'y':5},countdown=1)
# print('task_id: ',result.id)             # 任务ID: 6c3dcd76-ce8f-43e7-89e3-486ef0054d5b
# print('is_ready: ',result.ready())       # returns whether the task has finished processing or not
# print('traceback:',result.traceback)     # If the task raised an exception, you can also gain access to the original traceback,只有任务执行到了异常处,才会有返回值
# print('state: ', result.state)           # A task can only be in a single state, but it can progress through several states. PENDING -> STARTED -> SUCCESS
# print('return: ', result.get(timeout=4)) # 阻塞等待任务结果,等待超出timeout抛异常


# retry.delay(1)


(todo.s(1,2)|test.signature()).delay()  # a simple chain, the first task executes passing its return value to the next task in the chain, and so on.

