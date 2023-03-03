from .common import CaframNode
from .ctrl import NodeCtrl


class NodeOLD(CaframNode):

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


from pprint import pprint


class Node(CaframNode):

    # , _node_attr = "_test"
    _node_conf = []
    # _node_attr = "_node"
    # _test_conf = []

    def __init__(
        self, *args, node_obj=None, node_attr="_node", node_conf=None, **kwargs
    ):

        # if len(args) > 0:
        #     node_obj = node_obj or args[0] or self
        node_obj = node_obj or self

        self._node = NodeCtrl(
            node_obj=node_obj, node_attr=node_attr, node_conf=node_conf, *args, **kwargs
        )

        # Instanciate class
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        # assert hasattr(self, "_node")
        # print ("SEARCH ATTR", name)

        if name in self._node.__dict__:
            return self._node.__dict__[name]
        return self.__dict__["_node"][name]

    # def __repr__(self):

    #     return f"Node: <{self.__class__.__name__}:{hex(id(self))}>"
