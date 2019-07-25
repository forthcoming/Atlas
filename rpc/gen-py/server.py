import json
from tutorial import Calculator,CcktvRoom
from thrift.transport import TSocket,TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from tutorial.ttypes import RpcResult
from thrift.TMultiplexedProcessor import TMultiplexedProcessor

class TransmitHandler:
    def sayMsg(self, msg):
        print(msg)
        return "say " + msg

    def invoke(self,cmd,token,data):
        if cmd ==1:
            return json.dumps({token:data})
        else:
            return 'cmd不匹配'

class CcktvRoomHandler:
    def getBannerList(self, dic,idx):
        print(dic)
        return RpcResult(idx,'akatsuki','data-mining')


if __name__=="__main__":

    calculator_processor = Calculator.Processor(TransmitHandler())
    ccktv_room_processor = CcktvRoom.Processor(CcktvRoomHandler())
    processor = TMultiplexedProcessor()  # 接收多个service
    processor.registerProcessor('calculator', calculator_processor)
    processor.registerProcessor('ccktv_room', ccktv_room_processor)
    transport = TSocket.TServerSocket('127.0.0.1', 8000)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()


    # handler = CcktvRoomHandler()
    # processor = CcktvRoom.Processor(handler)

    # transport = TSocket.TServerSocket('127.0.0.1', 8000)
    # tfactory = TTransport.TBufferedTransportFactory()
    # pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    # server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    # server.serve()
