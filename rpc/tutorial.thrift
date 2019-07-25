// thrift --gen py tutorial.thrift

struct RpcResult{
    1:i32 status=0, //0成功,失败时填写业务错误码
    2:string msg,   //错误信息
    3:string data   //结果数据,json字符串
}

service Calculator {  // 对应一个类
    string sayMsg(1:string message),
    string invoke(1:i32 command 2:string token 3:string data)
}


service CcktvRoom
{    
    RpcResult getBannerList(1:map<string, string> krbMap, 2:i32 index)  // krbMap对应python键值都是字符串类型的字典
}