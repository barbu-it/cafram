"""
Cafram Default Nodes
"""

from pprint import pprint

from cafram.nodes.engine import NodeDecorator, NodeFactory, NodeMetaclass

# Common default instance
################################################################


# class Node(CaframNode, metaclass=NodeMetaclass):
class Node(metaclass=NodeMetaclass, node_prefix="__node__", node_root=True):
    "Default Cafram Node"


# Test v1 -- OK
# Node = NodeMetaclass("Node", (), {}, node_prefix="__node__")

# Test v2 -- FAIL
# Node = NodeFactory(prefix="__node__").node_class_builder(name="Node")

# Test v3 -- OK

# Node2 = NodeFactory(prefix="__node__").node_class_builder(name="Node")

# class Node(metaclass=NodeMetaclass, node_prefix="__node__", node_cls=Node2):
#     "Default Cafram Node"


node_wrapper = NodeDecorator(
    node_cls=Node,
    override=True,  # THIS IS THE DEFAULT BEHAVIOR !
)
newNode = node_wrapper.new_node
addMixin = node_wrapper.add_comp
