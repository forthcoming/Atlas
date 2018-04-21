import random,math,redis

class Hash:
    def __init__(self,m):
        self.m=m
        self.zoomin=random.randint(0,self.m)
        self.offset=random.randint(0,self.m)
        self.fun=random.choice(['BKDRHash','DJBHash','JSHash'])

    def BKDRHash(self,key,radix=31):
        # radix 31 131 1313 13131 131313 etc.
        hash=0
        for i in key:
            hash=hash*radix+ord(i)
        return hash

    def DJBHash(self,key):
        hash = 5381
        for i in key:
           hash = ((hash << 5) + hash) + ord(i)
        return hash

    def JSHash(self,key):
        hash = 1315423911
        for i in key:
            hash ^= ((hash << 5) + ord(i) + (hash >> 2))
        return hash
    
    def hash(self,key):
        return (self.zoomin *getattr(self,self.fun)(key) + self.offset) % self.m

class BloomFilter:
    def __init__(self, conn, name, capacity=1000000000, error_rate=.001):
        # capacity:预先估计要去重的数量,error_rate:错误率              
        m = -math.ceil(capacity*math.log2(math.e)*math.log2(error_rate)) 
        k = math.ceil(math.log1p(2)*m/capacity)
        self.name = name
        self.conn = conn
        self.hashFunc=[Hash(m) for i in range(k)]
        print(f'至少需要{m}个bit,{k}次哈希,内存占用{m>>23}M')  # m/8/1024/1024

    def add(self,key):
        for _ in self.hashFunc:
            self.conn.setbit(self.name,_.hash(key),1)

    def check(self,key):
        for _ in self.hashFunc:
            if not self.conn.getbit(self.name,_.hash(key)):
                return False
        return True

if __name__=='__main__':
    conn = redis.StrictRedis(host='localhost', port=6379, db=0)
    bf=BloomFilter(conn,'bf',20)
    for key in ['avatar','akatsuki','avatar','10086','wanted','hunter','fork',]:
        bf.add(key)
    print(bf.check('avatar'))
    print(bf.check('apple'))
    print(bf.check('10086'))
