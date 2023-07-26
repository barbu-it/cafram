

from pprint import pprint

class MyMeta(type):
    "MetaClass"


    def __new__(mcs, name, bases, dct, prefix="DEFAULT"):
        "Create new metaclass"

        mcs.prefix = prefix

        dct["prefix"] = mcs.prefix
        dct["simple_method"] = mcs.simple_method

        return super().__new__(mcs, name, bases, dct)


    def simple_method(self):
        "Simple method"

        print ("YEAHHH", self, self.prefix)




class Node1(metaclass=MyMeta, prefix="TUTU"):
    "Hello"


class Node2(metaclass=MyMeta, prefix="TATA"):
    "Hello"

    def __call__(self):
        "Call wrapper"

# cls1 = Node1()
# pprint(Node1.__dict__)
# pprint(cls1)
# pprint(cls1.__dict__)


cls1 = Node2()
pprint(Node2)
pprint(str(Node2))
pprint(Node2.__dict__)
pprint(cls1)
pprint(str(cls1))
pprint(cls1.__dict__)
pprint(cls1.simple_method())
