# Flask
import multiprocessing

bind = "127.0.0.1:7000"
workers = multiprocessing.cpu_count()*2 +1  # 子进程个数,gunicorn主进程不对外提供服务
errorlog='./error.log'  # 提前建好目录
accesslog='./access.log'
loglevel='debug'
daemon=True
pidfile='/run/gunicorn.pid'
timeout=120
threads = 4