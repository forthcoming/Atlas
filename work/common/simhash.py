import re,hashlib,collections

class Node:
    def __init__(self,data,right=None):
        self.data=data
        self.right=right

class Simhash:

    def __init__(self, sentence, _id=None,dimension=64):
        self._id=_id
        self.dimension = dimension  # the dimensions of fingerprints
        self.build(sentence)

    def __sub__(self,other):  # compute hamming distance
        x = self.value ^ other.value
        dis = 0
        while x:
            dis += 1
            x &= x - 1
        return dis

    def build(self, sentence):
        sentence = sentence.lower()
        sentence = re.findall(r'[\w\u4e00-\u9fcc]+', sentence)
        features=collections.Counter(sentence)
        v = [0] * self.dimension
        for key in features:
            h = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) # 128 bits
            w = features[key]
            for i in range(self.dimension):
                v[i] += w if h & (1<<i) else -w
        self.value = 0
        for i in range(self.dimension):
            if v[i] > 0:
                self.value |= (1<<i)

#供参考,有一定局限性
class SimhashIndex:

    def __init__(self, dimension=64, k=3):
        self.k = k  # k is the tolerance
        self.dimension =dimension
        self.offsets=[self.dimension // (self.k + 1) * i for i in range(self.k + 1)] 
        self.tables = [{} for i in range(len(self.offsets))]

    def add(self, simhash):
        assert simhash.dimension == self.dimension
        for table,key in zip(self.tables,self.get_keys(simhash)):
            if key in table:
                table[key]=Node(simhash,table[key])
            else:
                table[key]=Node(simhash)

    def get_keys(self, simhash):
        for i, offset in enumerate(self.offsets):
            if i == (len(self.offsets) - 1):
                m = 2 ** (self.dimension - offset) - 1
            else:
                m = 2 ** (self.offsets[i + 1] - offset) - 1
            yield simhash.value >> offset & m

    def get_near_dups(self, simhash):
        assert simhash.dimension == self.dimension
        ans = set()
        for table,key in zip(self.tables,self.get_keys(simhash)):
            dups = table[key]
            while dups:
                sim2 = dups.data
                if simhash-sim2 <= self.k:
                    ans.add(sim2._id)
                dups=dups.right
        return ans


if __name__=='__main__':
    sentences = [
        'How are you? I Am fine. blar blar blar blar blar Thanks.',
        'How are you i am fine. blar blar blar blar blar than',
        'This is simhash test.',
    ]
    
    index = SimhashIndex(k=3)
    for _id, sentence in enumerate(sentences):
        index.add(Simhash(sentence,_id))
    
    s1 = Simhash('How are you i am fine. blar blar blar blar blar thank',4)
    print(index.get_near_dups(s1))
    index.add(s1)
    print(index.get_near_dups(s1))
