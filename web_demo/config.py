class Config:
    # flask配置
    JSON_AS_ASCII = False

    # sqlalchemy配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/web_demo?charset=utf8mb4'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 600
    SQLALCHEMY_POOL_SIZE = 3
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_MAX_OVERFLOW = 1
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False  # 请求结束flask_sqlalchemy自动提交当前线程事务

    # redis集群配置
    STARTUP_NODES = [
        {"host": "localhost", "port": "8001"},
        {"host": "localhost", "port": "8002"},
        {"host": "localhost", "port": "8003"},
        {"host": "localhost", "port": "8004"},
        {"host": "localhost", "port": "8005"},
        {"host": "localhost", "port": "8006"},
    ]
    REDIS_CLUSTER_MAX_CONNECTIONS_PER_NODE = True
    REDIS_CLUSTER_MAX_CONNECTIONS = 100

    # redis单节点配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = ''
    REDIS_DB = 0

    # mongo配置
    MONGO_URI = "mongodb://127.0.0.1:27017" # 无密码模式mongodb://{ip}:{port}  用户密码模式mongodb://{user}:{password}@{ip}:{port}

