import json,redis
import numpy as np
from multiprocessing import Manager,Process

def storage(storage_config, index):    
    if 'dict' in storage_config:
        return InMemoryStorage()
    elif 'redis' in storage_config:
        storage_config['redis']['db'] = index
        return RedisStorage(storage_config['redis'])
    else:
        raise ValueError("Only in-memory dictionary and Redis are supported.")

class InMemoryStorage:
    def __init__(self):
        self.storage = Manager().dict()

    def keys(self):
        return self.storage.keys()

    def set_val(self, key, val):
        self.storage[key] = val

    def get_val(self, key):
        return self.storage[key]

    def append_val(self, key, val):
        # self.storage.setdefault(key, []).append(val)  # 不适用于Manager()

        # t=self.storage.setdefault(key, []) # !!!
        # t.append(val)
        # self.storage[key]=t
        if key in self.storage:
            self.storage[key]+=[val]
        else:
            self.storage[key]=[val]

    def get_list(self, key):
        return self.storage.get(key, [])

class RedisStorage:
    def __init__(self, config):
        self.name = 'redis'
        self.storage = redis.StrictRedis(**config)

    def keys(self, pattern="*"):
        return self.storage.keys(pattern)

    def set_val(self, key, val):
        self.storage.set(key, val)

    def get_val(self, key):
        return self.storage.get(key)

    def append_val(self, key, val):
        self.storage.rpush(key, json.dumps(val)) # !!!

    def get_list(self, key):
        return self.storage.lrange(key, 0, -1)  # 1. decode() 2. json.loads() 

class LSHash:
    def __init__(self, hash_size, input_dim, num_hashtables=1,storage_config={'dict': None}):
        """ 
        :param hash_size:
            The length of the resulting binary hash in integer. E.g., 32 means the resulting binary hash will be 32-bit long.
        :param input_dim:
            The dimension of the input vector. E.g., a grey-scale picture of 30x30 pixels will have an input dimension of 900.
        :param num_hashtables:
            (optional) The number of hash tables used for multiple lookups.
        :param storage_config:
            (optional) A dictionary of the form `{backend_name: config}` where`backend_name` is the either `dict` or `redis`, 
            and `config` is the configuration used by the backend. For `redis` it should be in the format of `{"redis": {"host": hostname, "port": port_num}}`, 
            where `hostname` is normally `localhost` and `port` is normally 6379.
        """
        self.uniform_planes = [np.random.randn(hash_size,input_dim) for i in range(num_hashtables)]  # shape: hash_size × input_dim
        self.hash_tables = [storage(storage_config, i) for i in range(num_hashtables)]


    def _hash(self, planes, input_point):
        try:
            input_point = np.array(input_point)  # for faster dot product
            projections = np.dot(planes, input_point)
        except TypeError as e:
            print("{} error, the input point needs to be an array-like object with numbers only elements".format(e))
            raise # raise an error
        except ValueError as e:
            print("{} error, the input point needs to be of the same dimension as input_dim when initializing this LSHash instance".format(e))
            raise
        else:
            return int("".join(['1' if i > 0 else '0' for i in projections]),2)

    def _as_np_array(self, json_or_tuple):
        # Takes either a JSON-serialized data structure or a tuple that has the original input points stored, and returns the original input point in numpy array format.
        if isinstance(json_or_tuple, str):  # JSON-serialized in the case of Redis
            try:
                tuples = json.loads(json_or_tuple)[0] # Return the point stored as list, without the extra data
            except TypeError:
                print("The value stored is not JSON-serilizable")
                raise
        else: # If extra_data exists, `tuples` is the entire (point:tuple, extra_data).
            tuples = json_or_tuple
        if isinstance(tuples[0], tuple):  # ((1, 2, 3, 4, 5, 6, 7, 8), 1)
            return np.array(tuples[0])  # in this case extra data exists
        elif isinstance(tuples, tuple):   # (1, 2, 3, 4, 5, 6, 7, 8)
            return np.array(tuples)
        else:
            raise TypeError("query data is not supported")

    def index(self, input_point, extra_data=None):
        # extra_data:(optional) in InMemoryStorage Needs to be a JSON-serializable object,RedisStorage dont need
        value=(tuple(input_point), extra_data)  # must be hashable cause it will be added into candidates later
        for i, table in enumerate(self.hash_tables):
            table.append_val(self._hash(self.uniform_planes[i], input_point),value)

    def query(self, query_point, distance_func='hamming',dis=4):
        candidates = set()

        if distance_func == "hamming":
            for i, table in enumerate(self.hash_tables):
                binary_hash = self._hash(self.uniform_planes[i], query_point)
                for key in table.keys():
                    distance = self.hamming_dist(key, binary_hash)
                    if distance < 2:
                        candidates.update(table.get_list(key))  # cant use add here
            query_point=self.list_to_num(query_point)
            result=[]
            for each in candidates:
                distance=self.hamming_dist(query_point,self.list_to_num(each[0]))
                if distance<=dis:
                    result.append((each,distance))
            return result

        else:
            if distance_func == "euclidean":
                d_func = LSHash.euclidean_dist_square
            elif distance_func == "centred_euclidean":
                d_func = LSHash.euclidean_dist_centred
            elif distance_func == "cosine":
                d_func = LSHash.cosine_dist
            else:
                raise ValueError("The distance function name is invalid.")
            for i, table in enumerate(self.hash_tables):
                binary_hash = self._hash(self.uniform_planes[i], query_point)
                candidates.update(table.get_list(binary_hash))

            candidates = [(ix, d_func(query_point, self._as_np_array(ix))) for ix in candidates]
            candidates.sort(key=lambda x: x[1])
            return candidates

    @staticmethod
    def list_to_num(query_point):
        num=0
        for each in query_point:
            num=num<<4|each
        return num

    @staticmethod
    def hex_to_dec(x):
        length=len(x)
        return [int(x[i:i+1],16) for i in range(0,length,1)]

    @staticmethod
    def hamming_dist(key1, key2):
        result=key1^key2
        count=0
        while result:
            result&=result-1
            count+=1
        return count

    @staticmethod
    def euclidean_dist_square(x, y):
        diff = np.array(x) - y
        return np.dot(diff,diff)

    @staticmethod
    def euclidean_dist_centred(x, y):
        diff = np.mean(x) - np.mean(y)
        return np.dot(diff,diff)

    @staticmethod
    def cosine_dist(x, y):
        return 1 - x@y / ((x@x * y@y) ** .5)

def test_shared_memory(lsh):
    storage=lsh.hash_tables[0]
    storage.set_val('avatar','nickname')
    storage.append_val('akatsuki','first')
    storage.append_val('akatsuki','second')

if __name__=='__main__':
    lsh = LSHash(6, 8)
    lsh.index([1,2,3,4,5,6,7,8],1)
    lsh.index([2,3,4,5,6,7,8,9],2)
    lsh.index([10,12,99,1,5,31,2,3],3)
    lsh.index([1,2,3,4,5,7,7,8],4)
    lsh.index([1,2,3,43,5,6,7,8],5)
    lsh.index([1,2,2,4,5,6,7,8],6)
    lsh.index([1,2,3,4,55,6,7,8],7)
    lsh.index([1,2,3,4,5,66,7,8],8)
    print(lsh.query([1,2,3,4,5,6,7,7],distance_func='hamming',dis=4))
    
    storage=lsh.hash_tables[0]
    print(storage.keys())
    print(storage.storage)
    p = Process(target=test_shared_memory, args=(lsh,))
    p.start()
    p.join()
    print(storage.keys())
    print(storage.get_val('avatar'))
    print(storage.get_list('akatsuki'))
