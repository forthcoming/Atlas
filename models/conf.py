# Flask
bind = "127.0.0.1:7000"
workers = 3 
errorlog='./error.log'  
accesslog='./access.log'
loglevel='debug'
daemon=True
pidfile='/run/gunicorn.pid'
timeout=120 
threads = 4
