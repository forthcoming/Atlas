class ThreadKWSpider:
    def __init__(self, queue):
        self._kwQueue = queue


    def main(self):

        while True:
            try:
                info = self._kwQueue.get(block=False)
            except Exception, e:
                break

            self.spiderKW(info[0], info[1])

    def spiderKW(self, categoryENName, keyword):
        raise 'impl to 1688 or taobao'

