# celery -A sync_task.tasks worker -c 2 --loglevel=info

broker_url = 'redis://localhost:6379/1'
result_backend = 'redis://localhost:6379/2'
task_annotations = {'tobedone': {'rate_limit': '1/m'}}
