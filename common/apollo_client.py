# -*- coding: utf-8 -*-
import json, logging, threading, time, requests


class ApolloClient:
    '''
    Namespace是配置项的集合,类似于一个配置文件的概念
    Apollo在创建项目的时候,都会默认创建一个application的Namespace
    Namespace的获取权限分为两种: private & public
    private权限的Namespace,只能被所属的应用获取到,一个应用尝试获取其它应用private的Namespace,Apollo会报404异常
    public权限的Namespace,能被任何应用获取,所以公共的Namespace的名称必须全局唯一
    '''

    def __init__(self, app_id, cluster='default', config_server_url='http://localhost:8080', timeout=35, ip=None):
        self.config_server_url = config_server_url
        self.appId = app_id
        self.cluster = cluster
        self.timeout = timeout
        self.init_ip(ip)
        self._stopping = False
        self._cache = {}
        self._notification_map = {'application': -1}  # -1保证初始化时从apollo拉取最新配置到内存,只有版本号比服务端小才认为是配置有更新

    def init_ip(self, ip):
        if ip:
            self.ip = ip
        else:  # 获取本机ip
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 53))
                ip = s.getsockname()[0]
            finally:
                s.close()
            self.ip = ip

    # Start the long polling loop.create a worker thread to do the loop. Call self.stop() to quit the loop
    def start(self, catch_signals=True):
        # First do a blocking long poll to populate the local cache, otherwise we may get racing problems
        if len(self._cache) == 0:
            self._long_poll()  # 用于更新self._cache和self._notification_map
        if catch_signals:
            import signal
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGABRT, self._signal_handler)
        t = threading.Thread(target=self._listener)
        t.start()

    def get_value(self, key, default_val=None, namespace='application', auto_fetch_on_cache_miss=False):
        if namespace not in self._notification_map:
            self._notification_map[namespace] = -1

        if namespace not in self._cache:
            self._cache[namespace] = {}
            logging.getLogger(__name__).info("Add namespace '%s' to local cache", namespace)
            # This is a new namespace, need to do a blocking fetch to populate the local cache
            self._long_poll()

        if key in self._cache[namespace]:
            return self._cache[namespace][key]
        else:
            if auto_fetch_on_cache_miss:
                return self._cached_http_get(key, default_val, namespace)
            else:
                return default_val

    def _long_poll(self):
        url = '{}/notifications/v2'.format(self.config_server_url)
        notifications = []
        for key in self._notification_map:
            notifications.append({'namespaceName': key, 'notificationId': self._notification_map[key]})
        try:
            r = requests.get(  # 如果检测到服务器的notificationId与本次提交一致,则最多等待30s,在这之间只要是服务器配置更新了,请求会立马返回
                url=url, params={'appId': self.appId, 'cluster': self.cluster,
                                 'notifications': json.dumps(notifications, ensure_ascii=False)}, timeout=self.timeout)

            if r.status_code == 304:
                logging.getLogger(__name__).debug('No change, loop...')
            elif r.status_code == 200:
                data = r.json()
                for entry in data:
                    ns = entry['namespaceName']
                    nid = entry['notificationId']
                    logging.getLogger(__name__).info("%s has changes: notificationId=%d", ns, nid)
                    self._uncached_http_get(ns)
                    self._notification_map[ns] = nid
            else:
                time.sleep(self.timeout)
        except Exception as e:
            print(e)

    def stop(self):
        self._stopping = True

    def _signal_handler(self, signal, frame):
        logging.getLogger(__name__).info('You pressed Ctrl+C!')
        self._stopping = True

    # 该接口会从缓存中获取配置,适合频率较高的配置拉取请求,如简单的每30秒轮询一次配置,缓存最多会有一秒的延时
    # ip参数可选,应用部署的机器ip,用来实现灰度发布
    def _cached_http_get(self, key, default_val, namespace='application'):
        url = '{}/configfiles/json/{}/{}/{}?ip={}'.format(self.config_server_url, self.appId, self.cluster, namespace,
                                                          self.ip)
        r = requests.get(url)
        if r.ok:  # ok?
            data = r.json()
            self._cache[namespace] = data
            logging.getLogger(__name__).info('Updated local cache for namespace %s', namespace)
        else:
            data = self._cache[namespace]
        return data.get(key, default_val)

    # 不带缓存的Http接口从Apollo读取配置,如果需要配合配置推送通知实现实时更新配置的话需要调用该接口
    def _uncached_http_get(self, namespace='application'):
        url = '{}/configs/{}/{}/{}?ip={}'.format(self.config_server_url, self.appId, self.cluster, namespace, self.ip)
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            self._cache[namespace] = data['configurations']  # dict,包含当前namespace下的所有key-value

    def _listener(self):
        while not self._stopping:
            self._long_poll()
        logging.getLogger(__name__).info("Listener stopped!")


if __name__ == '__main__':
    client = ApolloClient(app_id='ccktv', config_server_url='http://10.16.4.194:8080')
    client.start()
    conf = client.get_value('keys', 'not_exists')
    print(conf)
    client.stop()
