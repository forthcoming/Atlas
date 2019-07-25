import json
from tutorial import Calculator,CcktvRoom
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol


transport = TSocket.TSocket('127.0.0.1', 8000)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

# 如果服务端使用TMultiplexedProcessor接收处理,客户端必须用TMultiplexedProtocol并且serviceName必须和服务端的一致
calculator_protocol = TMultiplexedProtocol(protocol, "calculator") 
ccktv_room_protocol = TMultiplexedProtocol(protocol,"ccktv_room")
calc_client = Calculator.Client(calculator_protocol)
room_client = CcktvRoom.Client(ccktv_room_protocol)

transport.open()

print(calc_client.invoke(1,'1111-2222-3333-4444',json.dumps({"name":"zhoujielun"})))
print(calc_client.sayMsg("avatar"))
res = room_client.getBannerList({'1':'11'},10)
print(res,type(res))

transport.close()





# transport = TSocket.TSocket('127.0.0.1', 8000)
# transport = TTransport.TBufferedTransport(transport)
# protocol = TBinaryProtocol.TBinaryProtocol(transport)

# room_client = CcktvRoom.Client(protocol)

# transport.open()

# res = room_client.getBannerList({'1':'11'},10)
# print(res,type(res))


# transport.close()