"""
Node Controlled Classes
"""

import inspect
from pprint import pprint
from types import MappingProxyType

from . import errors

from .common import CaframNode
from .ctrl2 import NodeCtrl
from .lib.utils import update_classattr_from_dict


# NodeCtrl Public classe
################################################################


def scan_class_attr_config(obj, prefix="__node__obj_"):

    right_part = "__"
    ret = {}
    reduced = [item for item in dir(obj) if item.startswith(prefix)]
    pprint (reduced)
    for attr in reduced:

        attr_name = attr.replace(prefix, "")
        print ("SCAN", attr_name)
        attr_name = attr_name.rtrim(right_part)
        if attr_name:
            print ("SCAN", attr_name)


class NodeBase(CaframNode):
    """
    Generic Node Class v2

    Use this class as the base of your instances.
    """

    __node__ = None
    __node__params__ = {}
    #__node__mixins__ = {}


    def __init__(self, *args, **kwargs):
        """
        Create a new Node object.
        """


        self.__node__ = None

        # Config Read process:
        # =================
        # 1. Read mixin_conf from cls inherited (self._node_mixin__NAME__ATTR) # Inheritable, mixin_conf
        # 2. Read mixin_conf from decorators  self.__node__mixins_ # Not inheritable
        # 3. Read mixin_conf from kwargs  # Override

        # 1. Read nodectrl_conf from cls inherited (self._node__ATTR)             # Override, nodectrl conf
        # 2. Read nodectrl_conf from decorators __node__params_ # Not inheritable
        # 3. Read nodectrl_conf from kwargs  # Override
        #     if mixin_conf in those, then it override completely inherited conf


        # 0. init
        __node__params__ =  {}

        # 1.Update from inherited
        #inherited = update_classattr_from_dict(self, kwargs, prefix="__node__")

        inherited = scan_class_attr_config(self, prefix="__node__obj_")
        if inherited:
            print ("================== INHERITED PARAMS")
            pprint (inherited)
            assert False, "WIP"

        # assert False, "WIPPP HERE"
        #__node__params__.update(inherited)

        # 2.Update from decorators
        __node__params__.update(self.__node__params__)

        # 3.Update from kwargs
        __node__params__.update(kwargs)

        # if not __node__params__:
        #     # This happen when use without decorators
        #     pprint (dir(self))
        #     print ("2. Pre-Init new NodeCtrl", self)
        #     assert __node__params__, f"__node__param is empty !!! => {self.__node__params__}"

        print (f"NEW NODECTRL: {self}")
        pprint (__node__params__)

        NodeCtrl(
            self,
            **__node__params__,
                # Contains:
                #  obj_conf: {}
                #  obj_attr: "__node__"
                #  obj_prefix
                #  obj_prefix_hooks
                #  obj_prefix_class_params
                #  obj_prefix

        )

        # Ensure __post__init__ 
        if hasattr(self, "__post_init__"):
            # pprint(inspect.getargspec(self.__post_init__))
            try:
                self.__post_init__(*args, **kwargs)
            except TypeError as err:
                
                fn_details = inspect.getfullargspec(self.__post_init__)
                msg = f"{err}. Current {self}.__post_init__ function specs: {fn_details}"
                if not fn_details.varargs or not fn_details.varkw:
                    msg = f"Missing *args or **kwargs in __post_init__ method of {self}"

                raise errors.BadArguments(msg)


    # def __post_init__(self, *args, **kwargs):
    #     """
    #     Placeholder for custom class __init__ without requiring usage of `super`.
    #     """
        
    #     print(f"DEFAULT __INIT__ !: {args}, {kwargs}")

    #     pprint(super())
    #     super(NodeBase, self).__post_init__(*args, **kwargs)


class Node(NodeBase):
    """
    Full featured Node based from NodeBase
    """

    def __call__(self, *args):
        "Return node or mixin/alias"

        if self.__node__:
            count = len(args)
            if count == 0:
                return self.__node__
            if count == 1:
                return self.__node__.mixin_get(args[0])

            msg = "Only 1 argument is allowed"
            raise errors.CaframException(msg)

        msg = "Call is not available as there is no nodectrl yet"
        raise errors.CaframException(msg)

    def __getitem__(self, name):
        "Handle dict notation"

        if self.__node__:
            return self.__node__.mixin_get(name)

        msg = f"Getitem is not available as there is no nodectrl yet, can't look for: {name}"
        raise errors.CaframException(msg)

    def __getattr__(self, name):
        """Dunder to foward all unknown attributes to the NodeCtrl instance"""

        if self.__node__:
            return self.__node__.mixin_get(name)

        msg = f"Getattr '{name}' is not available for '{self}' as there is no nodectrl yet"
        raise errors.CaframAttributeError(msg)





        # if "_node" in self.__dict__:
        #     return self.__node__[name]

        # msg = f"No such node attribute '{name}' in {self}"
        # raise errors.AttributeError(msg)

        # # if name in self.__node__.__dict__:
        # #     return self.__node__.__dict__[name]
        # return None
        # return self.__dict__["_node"][name]

    # def _node_init(self, payload):
    #     print ("Node Conf Transform !!!")
    #     return payload



def NodeWrapperConfGenerator(
    cls, # Target class to be wrapped

    extra_attr=None,        # Extra attributes to attach to generated object
    override=True,      # SHould the NodeClass override or inherit ?

    enable_getattr=None,    # None=> enable if nothing present, True => Always, False => Never
    enable_getitem=None,
    enable_call=None
    
    ):
    "Create dynamically a NodeWrapper class"

    extra_attr = extra_attr or {}
    assert isinstance(extra_attr, dict)

    # Base class to be used for inheritance
    cls_base = NodeBase
    # Optional class methods to inject
    cls_feat = Node


    # Helper to add features
    def _add_feature(ret, option, method_name, src):
        "Create a dict with methods"

        assert isinstance(ret, dict)
        assert isinstance(src, (dict, MappingProxyType)), f"{type(src)}"
        
        if option in [None, True]:
            if option is True:
                ret[method_name] = getattr(cls_feat, method_name)
            else:
                if not method_name in src:
                    ret[method_name] = getattr(cls_feat, method_name)
    # def _add_feature2(ret, option, method_name):
    #     "Create a dict with methods"
        
    #     if option in [None, True]:
    #         if option is True:
    #             setattr(ret, method_name, getattr(cls_feat, method_name))
    #         else:
    #             if not hasattr(ret, method_name):
    #                 setattr(ret, method_name, getattr(cls_feat, method_name))


    # Create base attributes
    cls_members = {}
    cls_members.update(extra_attr)                      # Inject extra_attrs
    

    # Append dynamic methods
    cls_dict = cls.__dict__ if cls else {}
    if override is True and cls_feat:
        _add_feature(cls_members, enable_getattr, "__getattr__", cls_dict)
        _add_feature(cls_members, enable_getitem, "__getitem__", cls_dict)
        _add_feature(cls_members, enable_call, "__call__", cls_dict)


    # Create new class
    #cls_name =  f"{NodeBase.__name__}.{cls.__name__}"
    cls_name =  f"{cls.__name__}.Wrapped"
    # print ("CREATE WRAPPED CLASS:", cls_name, (cls_base, cls))
    # pprint (cls_members)

     
    #ret = type(cls_name, (cls_base, cls), cls_members)
    ret = cls
    if not cls_base in cls.__mro__:
        if override is True:
            ret = type(cls_name, (cls_base, cls), {})
        else:
            ret = type(cls_name, (cls, cls_feat), {})
        
        # Update package name when class has been defined
        cls_members.update({"__module__": cls.__module__})  # Allow to keep module reference


    #pprint (ret.__dict__)

    # Update special args and methods
    for key, val in cls_members.items():
        setattr(ret, key, val)

    # if cls_feat:
    #     _add_feature2(ret, enable_getattr, "__getattr__")
    #     _add_feature2(ret, enable_getitem, "__getitem__")
    #     _add_feature2(ret, enable_call, "__call__")


    #pprint (ret.__dict__)
    return ret




class _Node_OLD(CaframNode):
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
    # _node_logger_prefix = None

    # By default, cafram logs are not visible, because logs are below 'cafram2'.
    # To show cafram logs, set this to True.
    # False: Set logger_prefix to cafram.<Obj>
    # True: Set logger_prefix to your/this Node name Node.<Obj>
    # _node_logger_integrate = False
    # _node_logger_integrate = True

    def __init__(self, *args, **kwargs):
        """
        Create a new Node object.
        """

        # logger_prefix = self._node_logger_prefix
        # if not logger_prefix:
        #     logger_prefix = self.__class__.__name__ if self._node_logger_integrate else None

        self._node = None
        _node = NodeCtrl(
            #node_obj=self,
            self,
            # node_conf=node_conf or self._node_conf,
            # node_attr="_node",
            **kwargs,
        )

        # Instanciate other parent classes
        #super().__init__(*args, **kwargs)
        super().__init__()

        # Instanciate class
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        """
        Placeholder for custom class __init__ without requiring usage of `super`.
        """

    def __call__(self, *args):
        "Return node or mixin/alias"

        if self._node:
            count = len(args)
            if count == 0:
                return self._node
            if count == 1:
                return self._node.mixin_get(args[0])

            msg = "Only 1 argument is allowed"
            raise errors.CaframException(msg)

        msg = "Call is not available as there is no nodectrl yet"
        raise errors.CaframException(msg)

    def __getitem__(self, name):
        "Handle dict notation"

        if self._node:
            return self._node.mixin_get(name)

        msg = "Getitem is not available as there is no nodectrl yet"
        raise errors.CaframException(msg)

    def __getattr__(self, name):
        """Dunder to foward all unknown attributes to the NodeCtrl instance"""

        if self._node:
            return self._node.mixin_get(name)

        msg = f"Getattr '{name}' is not available for '{self}' as there is no nodectrl yet"
        raise errors.CaframException(msg)


        # if "_node" in self.__dict__:
        #     return self._node[name]

        # msg = f"No such node attribute '{name}' in {self}"
        # raise errors.AttributeError(msg)

        # # if name in self._node.__dict__:
        # #     return self._node.__dict__[name]
        # return None
        # return self.__dict__["_node"][name]

    # def _node_init(self, payload):
    #     print ("Node Conf Transform !!!")
    #     return payload



