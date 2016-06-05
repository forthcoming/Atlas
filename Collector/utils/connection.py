import redis

# Default values.
REDIS_URL = None
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

def from_settings(settings):
  url = settings.get('REDIS_URL',  REDIS_URL)
  host = settings.get('REDIS_HOST', REDIS_HOST)
  port = settings.get('REDIS_PORT', REDIS_PORT)
  pool = redis.ConnectionPool(host=host, port=port, db=0)

  # REDIS_URL takes precedence over host/port specification.
  if url:
    return redis.from_url(url)
  else:
    return redis.StrictRedis(connection_pool=pool)
