"""
Cafram Default Nodes
"""

from pprint import pprint

from cafram import errors
from cafram.common import CaframNode
from cafram.nodes.ctrl import NodeCtrl
from cafram.nodes.engine import NodeMetaclass, NodeDecorator

# Globals
################################################################


# Common default instance
################################################################



# Generic default node class with metaclass
# class NodeV2(Node, metaclass=NodeMetaclass, node_prefix="__nodev2__"):
# class Node( metaclass=NodeMetaclass, node_prefix="__nodev2__"):


#class Node(CaframNode, metaclass=NodeMetaclass):
class Node(metaclass=NodeMetaclass):
    "Default Cafram Node"



# # Equivalent as above !!!
Node2 = NodeMetaclass(
    "Node",
    (),
    {
        "__module__":__name__,
        "__doc__": "Default Cafram Node",
    },
    #{}, #{"ATTR1": True, "__doc__": "Custom doc"},
    # node_bases=[CaframNode],
    # node_override=True,
    # node_module="TOTO",
    # module=__name__,
    # # node_name="NodeWrapper2",
    # doc="Default Cafram Node2",
)




print ("FIRST INIT")
node_wrapper = NodeDecorator(
    node_cls=Node,

    # prefix="__node__",
    # name="Node",
    override=True,  # THIS IS THE DEFAULT BEHVIOR !

)

print ("FIRST INIT EOF")


# nw = NodeDecorator(prefix="__node__")

newNode = node_wrapper.new_node
addMixin = node_wrapper.add_comp



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
