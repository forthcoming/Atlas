# Flask
import multiprocessing

bind = "127.0.0.1:7000"  # 只能通过127.0.0.1:7000访问
# bind = ['10.1.2.143:7600','127.0.0.1:7600']
workers = multiprocessing.cpu_count()*2 +1  # 子进程个数,gunicorn主进程不对外提供服务
errorlog='./error.log'  # 提前建好目录
accesslog='./access.log'
loglevel='debug'
daemon=True   # 注意: 如果配置了daemon=True或者有类似nohup &之类命令启动时,会看不到print输出信息
pidfile='/run/gunicorn.pid'
timeout=120
threads = 4
worker_connections=100  # The maximum number of simultaneous clients.This setting only affects the Eventlet and Gevent worker types.
max_requests=1000 # The maximum number of requests a worker will process before restarting.This is a simple method to help limit the damage of memory leaks.


# nohup gunicorn web:app -c conf.py  # 导入了app的文件web.py所在目录
# kill -HUP `cat /run/gunicorn.pid`

