"""
Cafram Default Nodes
"""

from pprint import pprint

# from cafram import errors
# from cafram.common import CaframNode

# from cafram.nodes.ctrl import NodeCtrl
from cafram.nodes.engine import NodeDecorator, NodeMetaclass

# Common default instance
################################################################


# class Node(CaframNode, metaclass=NodeMetaclass):
class Node(metaclass=NodeMetaclass, node_prefix="__node__"):
    "Default Cafram Node"


node_wrapper = NodeDecorator(
    node_cls=Node,
    override=True,  # THIS IS THE DEFAULT BEHAVIOR !
)
newNode = node_wrapper.new_node
addMixin = node_wrapper.add_comp
