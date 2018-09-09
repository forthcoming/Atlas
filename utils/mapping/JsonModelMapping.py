#!/usr/bin  python
#coding: utf-8
from inspect import isfunction

class JsonModelMapping:
    def __init__(self):
        pass


    @classmethod
    def modelFromDict(cls, dictparam):
        obj = cls()
        attributesAfterFliter = JsonModelMapping._getAttributeEffective(obj)


        for key, value in dictparam.items():
            if (key in attributesAfterFliter):
                setattr(obj, key, value)

        return obj


    def dictFromModel(self):
        attributesAfterFliter = JsonModelMapping._getAttributeEffective(self)

        dictRet = {}

        for attr in attributesAfterFliter:
            dictRet[attr] = getattr(self, attr, '')

        return dictRet


    @staticmethod
    def _getAttributeEffective(obj):
        attributes = dir(obj)

        attributesAfterFliter = []

        for index in range(0, len(attributes)):
            attr = attributes[index]

            if attr.find('__') >= 0:
                # print attribute
                # attributesAfterFliter.remove(attr)
                continue

            if callable(getattr(obj, attr, None)):
                continue

            attributesAfterFliter.append(attr)

        return attributesAfterFliter


#########################################################################################################
### example
class TestModel(JsonModelMapping):
    name = ''
    age = 1

if __name__ == '__main__':
    model = TestModel.modelFromDict({'name' : 'cuckoo', 'age' : 2})
    print model.name
    print model.age
    print model.dictFromModel()

    # new model
    model = TestModel()
    model.name = 'cuckoo'
    model.age = 20

    print model.dictFromModel()
