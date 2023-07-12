"""
Cafram Default Nodes
"""

from pprint import pprint

from cafram import errors
from cafram.common import CaframNode
from cafram.nodes.ctrl import NodeCtrl
from cafram.nodes.engine import NodeMetaclass, NodeWrapper

# Globals
################################################################


# Common default instance
################################################################

nw = NodeWrapper(
    prefix="__node__",
    override=True,  # THIS IS THE DEFAULT BEHVIOR !
    name="Node",
)

# nw = NodeWrapper(prefix="__node__")

newNode = nw.newNode
addMixin = nw.addMixin


# Generic default node class with metaclass
# class NodeV2(Node, metaclass=NodeMetaclass, node_prefix="__nodev2__"):
# class Node( metaclass=NodeMetaclass, node_prefix="__nodev2__"):


class Node(CaframNode, metaclass=NodeMetaclass):
    # class Node(metaclass=NodeMetaclass):
    "Default Cafram Node"

    # ATTR1 = True

    # def node_method(self):
    #     print("Hello node_method")
    #     return True

    # def __init__(self):
    #     print ("NODE INITEDDDDDD")

    #     super().__init__()


# Equivalent as above !!!
Node2 = NodeMetaclass(
    "Node",
    (),
    {"ATTR1": True, "__doc__": "Custom doc"},
    node_bases=[CaframNode],
    node_override=True,
    node_doc="Custom doc",
)

# DECORATORS
################################################################


# print ("============== RECAP")
# pprint (Node)
# #pprint (Node.__mro__)
# pprint (Node.__dict__)
# print ("==============")


# Node2 = None
# Node = NodeMetaclass.dyn_class("__nodev2__", name="TOTO", package="TITI")
# Node = NodeMetaclass.dyn_class("__nodev2__", name="Node2")
# Node = node_class_builder("__nodev2__", name="Node2", doc="Default Cafram Nodev2", module="faked")

# Node = node_class_builder("__nodev2__", name="Node2", doc="Default Cafram Nodev2", bases=)


# CaframNode
# CaframNode

# print ("==============")
# pprint (Node2)
# pprint (Node2.__mro__)
# pprint (Node2.__dict__)

# print ("==============")
