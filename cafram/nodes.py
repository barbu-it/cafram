"""
Node Controlled Classes
"""

from .common import CaframNode
from .ctrl import NodeCtrl

from pprint import pprint


class Node(CaframNode):
    """
    Generic Node Class

    Use this class as the base of your instances.
    """

    _node_conf = []
    # _node_attr = "_node"
    # _test_conf = []

    def __init__(
        self, *args, node_obj=None, node_attr="_node", node_conf=None, **kwargs
    ):
        """
        Create a new Node object.

        Can be configured through basic arguments:
        - node_attr
        - node_obj
        - node_conf = CONFIG

        At the class level:
        - _node_conf = CONFIG
        """

        # Create NodeCtrl instance
        node_conf = node_conf or self.__class__._node_conf
        node_obj = node_obj or self
        self._node = NodeCtrl(
            node_obj=node_obj, node_attr=node_attr, node_conf=node_conf, *args, **kwargs
        )

        # Instanciate class
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        """
        Placeholder for custom class __init__ without requiring usage of `super`.
        """
        pass

    def __getattr__(self, name):
        """Dunder to foward all unknown attributes to the NodeCtrl instance"""

        if name in self._node.__dict__:
            return self._node.__dict__[name]
        return self.__dict__["_node"][name]


class NodeOld(CaframNode):

    _node_confs = []
    _node_attr = "_node"

    def __init__(self, *args, obj=None, attr=None, **kwargs):

        # obj = obj or self
        attr = attr or self._node_attr
        mixin_confs = list(self._node_confs)

        assert isinstance(attr, str), f"GOT: {attr}"
        NodeCtrl(obj=self, attr=attr, mixin_confs=mixin_confs, *args, **kwargs)

        # Instanciate class
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

    def dump(self):

        self._node.dump()

    # def __repr__(self):

    #     return f"Node: <{self.__class__.__name__}:{hex(id(self))}>"
