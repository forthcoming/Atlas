from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from rediscluster import RedisCluster
from redis import Redis

from web_demo.config import Config

app = Flask(__name__)
app.config.from_object(Config)
# app.config['JSON_AS_ASCII'] = False


db = SQLAlchemy(app)
'''
db.session类型是ScopedRegistry,不是ThreadLocalRegistry
db.engine对应sqlalchemy中的create_engine实例engine,autocommit=True
db.session对应sqlalchemy中的scoped_session实例session,autoflush=True,autocommit=False
db.session.add, Model.query.filter不会产生事务,Model.query.filter.first/all才会产生事务
db.init_app有一个shutdown_session函数,用于接口请求结束后结束事务(不会提交更新到数据库,SQLALCHEMY_COMMIT_ON_TEARDOWN=True除外),释放链接到连接池,删除当前线程session
'''

# redis-py-cluster 2.0.0 has requirement redis<3.1.0,>=3.0.0,但celery需要更高的redis-py版本
# rc = RedisCluster(
#     startup_nodes=Config.STARTUP_NODES,
#     max_connections=Config.REDIS_CLUSTER_MAX_CONNECTIONS,
#     max_connections_per_node=Config.REDIS_CLUSTER_MAX_CONNECTIONS_PER_NODE,
#     skip_full_coverage_check=True,
#     socket_timeout=10,
# )
rds = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    password=Config.REDIS_PASSWORD,
    db=Config.REDIS_DB,
    socket_timeout=10,
)


@app.teardown_appcontext
def get_info(response_or_exc):  # 不管是否有异常,注册的函数get_info都会在每次请求完之后执行,早于flask_sqlalchemy的shutdown_session执行
    print('db.session.registry.registry', len(db.session.registry.registry))
    print('db.engine.pool.status', db.engine.pool.status())
    return response_or_exc


from web_demo.service.test_celery_api import test_celery_bp

app.register_blueprint(test_celery_bp, url_prefix='/ccktv/v1/test_celery/')

# 客户端以requests.get/post(json={...})形式提交(浏览器默认行为)时,服务端只能接受request.json(dict类型)和request.data(bytes类型)
# 客户端以requests.get(params={...})形式提交时,服务端只能接受request.args(ImmutableMultiDict类型)
# 客户端以requests.post(data={...})形式提交时,服务端只能接受request.form(ImmutableMultiDict类型)
# request.view_args(dict类型)用于接受地址栏形如<int:account_id>的变量,跟客户端如何提交无关
# 每次请求过来flask都会产生一个新的线程
# post
# request.path       /select
# request.full_path  /select?
# get
# request.path       /select
# request.full_path  /select?name=avatar&product_id=540554959138
