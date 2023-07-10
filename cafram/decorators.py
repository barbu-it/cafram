import traceback
import logging
from functools import wraps
from pprint import pprint

from .lib.utils import import_module

from cafram.mixins.base import LoggerMixin, IdentMixin
from cafram.mixins.tree import ConfDictMixin, ConfListMixin, NodeConfDict, NodeConfList
#from cafram.nodes2 import Node
import cafram.errors as errors

from cafram.ctrl2 import NodeCtrl


# NodeCtrl Public classe
################################################################


# def repeat(times):
#     ''' call a function a number of times '''
#     def decorate(fn):
#         @wraps(fn)
#         def wrapper(*args, **kwargs):
#             for _ in range(times):
#                 result = fn(*args, **kwargs)
#             return result
#         return wrapper

#     return decorate

import inspect

from .nodes2 import NodeWrapperConfGenerator


# Config Scanners
################################################################




# IMPORTED FROM ctrl2.py
def nodectrl_conf_from_attr(obj, prefix=None):
    """Scan all object's attributes and return a dict of key starting with prefix

    format:
        - "(PREFIX)_(CONF)"
    """
    prefix = prefix or ""
    if not obj:
        return {}

    ret = {}
    for attr in dir(obj):
        if attr.startswith(prefix):
            short_name = attr.replace(prefix, "")
            if not short_name.startswith("_"):
                ret[short_name] = getattr(obj, attr)

    return ret

# IMPORTED FROM ctrl2.py
def mixin_conf_from_obj_attr(obj, prefix=None):
    """Scan _obj and return a dict config

    format:
        - "(PREFIX)__(MIXIN_KEY)__(CONF)"
    """
    prefix = prefix or ""

    if not obj:
        return {}

    ret = {}
    for attr in dir(obj):

        # Filter out uneeded vars
        attr_orig = attr
        if prefix:
            if not attr.startswith(prefix):
                continue

            attr = attr.replace(prefix, "", 1)

        # Parse var names
        parts = attr.split("__", 2)
        if len(parts) != 2:
            continue
        attr_name, attr_conf = parts[0], parts[1]
        if not attr_conf:
            continue

        # Save config
        if not attr_name in ret:
            ret[attr_name] = {}
        ret[attr_name][attr_conf] = getattr(obj, attr_orig)

    return ret



import json

# From chat GPT
def to_env(json_string):

    json_data = json.loads(json_string)
    env_dict = {}

    def traverse_json(data, path=''):
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                traverse_json(value, new_path)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                new_path = f"{path}[{index}]"
                traverse_json(value, new_path)
        else:
            env_dict[path] = str(data)

    traverse_json(json_data)
    return env_dict




# NEW OBJ CONF PARSER
def gen_netctrl_conf(obj, prefix=None):
    """Scan all object's attributes and return a dict of key starting with prefix

    format:
        - "(PREFIX)_(CONF)"
    """

    prefix = prefix or "node_"
    if not obj:
        return {}

    ret = {
        "obj_conf": {}
    }

    for attr in dir(obj):

        # prefix = "_node"
        if not attr.startswith(prefix):
            continue

        short_name = attr.replace(prefix, "")

        # Parse Item Config 
        if short_name.startswith("__"):
            short_name = short_name[2:]
            key, short_name = short_name.replace('__',' ').split(' ', 2)

            # TODO: Handle Dict AND lists
            # Lists => https://stackoverflow.com/a/2133116

            # Create dict if it does not exists
            if not key in ret["obj_conf"]:
                ret["obj_conf"][key] = {}

            ret["obj_conf"][key][short_name] = getattr(obj, attr)

        # Parse Top Config
        elif short_name.startswith("_"):
            short_name = short_name[1:]
            assert short_name not in ret, f"ERROR HERE"
            ret[short_name] = getattr(obj, attr)

        # Not parseable
        else:
            print (f"WARN: Ignoring class pattern: {attr}")
            assert False
        
    return ret





     









# DECORATORS
################################################################



def newNode(

    override=True,
    prefix = "__node__",

    # Only relavant if override is True, otherwise can be
    enable_getattr=None, # None=> enable if nothing present, True => Always, False => Never
    enable_getitem=None,
    enable_call=None,

    **kwargs): #, *args, **kwargs):
    """
    Transform a class to a NodeClass WITH LIVE PATCH
    
    Forward all kwargs to NodeCtrl()
    """

    assert not "obj_mixins" in kwargs, f"Usage of obj_mixins in decorator is forbidden, please use 'addMixin' instea"

    def _decorate(cls):

        # Create main parameters
        node_params = {
            "obj_clean": False,
            "obj_attr": "__node__",
        }
        node_params.update(kwargs)


        # __node__mixins__
        # __node__params__

        # Create mixin configs
        node_mixins = dict(getattr(cls, "__node__mixins__", {}))
        node_params["obj_mixins"] = node_mixins
        

        # Generate a new Node Class
        ret = NodeWrapperConfGenerator(cls,
            override=override,
            extra_attr={"__node__params__": node_params},  # Forward nodectrl init params

            enable_getattr=enable_getattr, # None=> enable if nothing present, True => Always, False => Never
            enable_getitem=enable_getitem,
            enable_call=enable_call,

        )

        # print ("1. New Wrapped Node", ret)
        # pprint (ret.__dict__)

        return ret

    return _decorate





def addMixin(mixin, mixin_key=None, mixin_conf=None, **kwargs):
    "Add features/mixins to class"


    # Fetch mixin class
    if isinstance(mixin, str):
        #mixin_name = mixin
        mixin_cls = import_module(mixin)
    else:        
        #mixin_name = mixin.__name__
        mixin_cls = mixin


    # Get mixin config
    mixin_key = mixin_key or mixin_cls.mixin_key
    mixin_conf = mixin_conf or kwargs

    # Validate data
    assert isinstance(mixin_conf, dict)
    assert isinstance(mixin_key, str)

    mixin_def = dict(mixin_conf)
    mixin_def.update({
        "mixin": mixin_cls,
        "mixin_key": mixin_key
    })

    def _decorate(cls):


        # Ensure idempotency
        if not hasattr(cls, "__node__mixins__"):
            cls.__node__mixins__ = {}

        # print ("ASSIGN MIXIN", cls, type(cls))
        assert not mixin_key in cls.__node__mixins__, f"Already assigned key: {mixin_key}" 

        cls.__node__mixins__[mixin_key] = mixin_def

        return cls

    return _decorate












# OLLLDDDD
################################################################


# from cafram.common import CaframNode
# from cafram.mixins import BaseMixin

# def NodeDef(base_name): #, *args, **kwargs):
#     "Transform a class to a NodeClass WITH NODE CLASS"

#     assert not inspect.isclass(base_name), f"Should be a string, not a class: {base_name}"

#     # Retrieve the mixin class from string
#     base_cls = None
#     if isinstance(base_name, str):
#         base_cls = import_module(base_name)

#     assert issubclass(base_cls, CaframNode), f"Class {base_cls} is not subclass of {CaframNode}"


#     def _decorate(cls):

#         try:
#             ret = type( f"{base_cls.__name__}.{cls.__name__}", 
#                     (base_cls, cls), {}
#                 )
#             print (f"DECORATE v1 {cls} with {base_cls}")
#             return ret
#         except Exception as err:
#             print ("ERRRRRRRRRRRR => ", err)
#             assert False
#         return cls

#         # @wraps(cls)
#         # def wrapper(*args, **kwargs):
#         #     print ("YOOO00000000O", cls)
#         #     return cls
#         # return wrapper

#     return _decorate

#     return cls


# # Source: https://discuss.python.org/t/how-to-add-more-operations-to-a-init-funcion-of-a-class-with-a-class-decorator/15640/8
# # def my_class_decorator(cls):
# #     class DecoratorClass(cls):
# #         @functools.wraps(cls, updated=())
# #         def __init__(self):
# #             super(DecoratorClass, self).__init__()
# #             self.foo = 42  # more operations
# #             ...    
# #     return DecoratorClass




# def NodeDef2(base_name, **kwargs): #, *args, **kwargs):
#     "Transform a class to a NodeClass WITH LIVE PATCH"

#     assert not inspect.isclass(base_name), f"Should be a string, not a class: {base_name}"

#     # Retrieve the mixin class from string
#     base_cls = None
#     if isinstance(base_name, str):

#         if ":" in base_name:
#             package, name = base_name.rsplit(':', 1)
#             base_cls = import_module_from(package, name)
#         else:
#             base_cls = import_module(base_name)
#     assert issubclass(base_cls, CaframNode), f"Class {base_cls} is not subclass of {CaframNode}"


#     def _decorate(cls):

#         # if hasattr(cls, "__init__"):
#         #     setattr()

#         # assert not hasattr(cls, "__init__"), f"FAILED: {getattr(cls, '__init__')}"
#         # print ("ASSERT")

        
#         try:
#             # ret = type( f"{base_cls.__name__}.{cls.__name__}", 
#             #         (base_cls, cls), {}
#             #     )
#             ret = type( f"{base_cls.__name__}.{cls.__name__}", 
#                 (cls, base_cls), {}
#             )
#             print (f"DECORATE {cls} with {base_cls}")
#             print ("ADD OPTIONS: ", kwargs)
#             return ret
#         except Exception as err:
#             print ("ERRRRRRRRRRRR => ", err)
#             assert False
#         return cls

#         # @wraps(cls)
#         # def wrapper(*args, **kwargs):
#         #     print ("YOOO00000000O", cls)
#         #     return cls
#         # return wrapper

#     return _decorate

#     return cls

