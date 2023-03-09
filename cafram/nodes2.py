"""
Node Controlled Classes
"""

from . import errors
from .common import CaframNode
from .ctrl2 import NodeCtrl

from pprint import pprint


class Node(CaframNode):
    """
    Generic Node Class v2

    Use this class as the base of your instances.
    """

    ## Public class conf API
    # _node__log__mixin = "MyMixin"
    # _node__log__logger_name = "MyLogger"
    # _node__conf__children = "MyLogger"
    # _node__conf__schema = "MyLogger"

    ## Public class methods hooks API (for mixins)
    # def (node_)(conf)_default(self, payload):
    # def (node_)(conf)_transform(self, payload):
    # def (node_)(conf)_validate(self, payload):
    # def (node_)(children)_create(self, payload) or in hook object ? Nope, in mixins ...

    ## Public obj hooks
    # __getattr__
    # __getitems__
    # _node
    # children_create ?

    _node_conf = {
        # "KEY": {
        #     "mixin": "MyMixin",
        #     "setting1": "value1",
        # }
    }


    # Set a string for logger name prefix, if None, detected automatically
    #_node_logger_prefix = None

    # By default, cafram logs are not visible, because logs are below 'cafram2'.
    # To show cafram logs, set this to True.
    # False: Set logger_prefix to cafram.<Obj>
    # True: Set logger_prefix to your/this Node name Node.<Obj> 
    #_node_logger_integrate = False
    #_node_logger_integrate = True
    
    

    def __init__(self, *args, **kwargs):
        """
        Create a new Node object.
        """


        # logger_prefix = self._node_logger_prefix
        # if not logger_prefix:
        #     logger_prefix = self.__class__.__name__ if self._node_logger_integrate else None


        NodeCtrl(
            node_obj=self, 
            node_attr="_node", 
            #node_logger_prefix=logger_prefix,
            **kwargs)

        # Instanciate class
        self._init(*args, **kwargs)


    def _init(self, *args, **kwargs):
        """
        Placeholder for custom class __init__ without requiring usage of `super`.
        """
        pass

    def __getattr__(self, name):
        """Dunder to foward all unknown attributes to the NodeCtrl instance"""

        #print ("GET ATTR NODE:", self,  name)

        if "_node" in self.__dict__:
            return getattr(self._node, name )
            #return self._node.__dict__[name]

        msg = f"No such node attribute '{name}' in {self}"
        raise errors.AttributeError(msg)



        # if name in self._node.__dict__:
        #     return self._node.__dict__[name]
        return None
        return self.__dict__["_node"][name]

    # def _node_init(self, payload):
    #     print ("Node Conf Transform !!!")
    #     return payload