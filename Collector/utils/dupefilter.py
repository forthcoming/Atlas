import time
from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import request_fingerprint
from Collector.utils import connection

class RFPDupeFilter(BaseDupeFilter):
  """Redis-based request duplication filter"""

  def __init__(self, server, key):
    """
    Parameters
    ----------
    server : Redis instance
    key : str
    Where to store fingerprints
    """
    self.server = server
    self.key = key

  @classmethod
  def from_settings(cls, settings):
    server = connection.from_settings(settings)
    # create one-time key. needed to support to use this
    # class as standalone dupefilter with scrapy's default scheduler
    # if scrapy passes spider on open() method this wouldn't be needed
    key = "dupefilter:{}".format(time.time())
    return cls(server, key)

  def request_seen(self, request):
    fp = request_fingerprint(request)
    added = self.server.sadd(self.key, fp)
    return not added

  def close(self, reason):
    """Delete data on close. Called by scrapy's scheduler"""
    self.server.delete(self.key)  #Clears fingerprints data
