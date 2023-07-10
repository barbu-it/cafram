


# Example 2

# In library: node3/py
# -------------------


from pprint import pprint

import cafram.errors as errors
from cafram.ctrl2 import NodeCtrl
#from cafram.nodes2 import Node

from cafram.common import CaframNode

import inspect 

# Globals
################################################################




NODE_METHODS = [
        "__init__",
        "__getattr__",
        "__getitem__",
        "__call__",
    ]


import functools


class Fake():
    "Hello"





# Node Wrapper Class Builder
################################################################


# This is a class method
#@functools.cache
def node_class_builder(prefix, name=None, bases=None, clsmethods=None, module=None, doc=None, attrs=None):
    """Build a generic node wrapper

    Args:
        prefix (_type_): _description_
        name (_type_, optional): _description_. Defaults to None.
        bases (_type_, optional): _description_. Defaults to None.
        clsmethods (_type_, optional): _description_. Defaults to None.
        module (_type_, optional): _description_. Defaults to None.
        doc (_type_, optional): _description_. Defaults to None.
        attrs (_type_, optional): _description_. Defaults to None.

    Raises:
        errors.BadArguments: _description_
        errors.CaframAttributeError: _description_
        errors.CaframException: _description_
        errors.CaframException: _description_
        errors.CaframException: _description_

    Returns:
        _type_: A NodeWrapper Class


    Typical usage example:

        class Node(CaframNode, metaclass=NodeMetaclass, node_prefix='__node__', node_override=False):
            "My DocString"
            ATTR1 = True

        # TOFIX: This version has not metadata for children classes
        Node1 = NodeMetaclass("Node", (), {"ATTR1":True, "__doc__":"My DocString"}, 
                node_override=True,                        
                node_prefix='__node__',
                node_bases=[CaframNode])

        # TOFIX: This version has not metadata for children classes
        Node2 = node_class_builder("__node__", name="Node", doc="My DocString", bases=[CaframNode])
            # => node_override=False  

        # Expected result:
        assert Node == Node1
        assert Node == Node2


        # And for the subsequent Nodes:

        # Ex1: 
        class AppObj():
            "Parent class"

        # Ex1.a: 
        class MyApp(AppObj, Node):
            "App class"

    """

    # Test arguments
    attrs = attrs or {}
    clsmethods = list(clsmethods or NODE_METHODS)
    bases = bases or tuple([])   # Example: (CaframNode, Fake)
    if not isinstance(bases, tuple):
        bases = tuple(bases)


    assert isinstance(bases, tuple), f"Got: {bases} (type={type(bases)})"
    print (f"Build new _NodeSkeleton: name={name}, prefix='{prefix}', bases={bases}, methods:", clsmethods)


    class _NodeSkeleton(*bases):
        "Dynamic Node Class"

        # def DYN_NODE_ALWAYS(self):
        #     print("ALWAYS HERE !")


        #__node__params__ = {}
        #__node__params__ = {}
        __node__mixins__ = {}

        # __node__attrs__ =  clsmethods
        # __node__prefix__ =  prefix


        # This should not be hardcoded !!!
        @classmethod
        def tmp__patch__(self, cls, override=True):
            "Patch an object to become a node"


            if not self in cls.__mro__:
                print (f"Wrapping Node {cls} with {self}")

                node_attrs = getattr(_NodeSkeleton, f"{prefix}_attrs__")

                for method_name in node_attrs:
                    print ("IMPORT METHOD", method_name)

                    if override is False:
                        if hasattr(cls, method_name):
                            tot = getattr(cls, method_name)
                            print ("Skip method patch", method_name, tot)
                            continue

                    method = getattr(self, method_name)
                    setattr(cls, method_name, method)


                setattr(cls, f"{prefix}_attrs__", node_attrs)
                setattr(cls, f"{prefix}_prefix__", prefix)
            else:
                print (f"Skipping Wrapping Node {cls} with {self}")

            return cls

        @classmethod
        def tmp__inherit(cls, obj, name=None, bases=None, override=True, attrs=None):

            # Assert obj is a class
            

            print ("CALLL tmp__inherit", cls, obj, name, attrs)

            ret = cls
            dct = attrs or {}
            bases = list(bases or [])
            name = name or f"{obj.__qualname__}WrapperTMP"

            # Do not reinject class if already present
            # base_names = [cls.__name__ for cls in bases]
            # if not w_name in base_names:
            if  cls not in bases:

                if name:
                    dct["__qualname__"] = name

                if override:
                    # Create a new class WrapperClass that inherit from defined class

                    print ("NODE OVERRIDE", name, cls.__qualname__, tuple(bases), dct)
                    bases.insert(0, cls)

                    # Pros:
                    #   * Easy and ready to use
                    #   * Important methods are protected
                    # Cons: 
                    #   * BREAK standard inheritance model
                    #   * All your attributes disapears on __dir__, unless dct=cls.__dict__
                    #   * HIgh level of magic
                else:
                    # Append in the end WrapperClass inheritance

                    print ("NODE INHERIT", name, cls.__module__, tuple(bases), dct)
                    bases.append(cls)
                    
                    # Pros:
                    #   * Respect standard inheritance model
                    #   * All your attributes/methods apears on __dir__
                    #   * Not that magic
                    # Cons: 
                    #   * Important methods  NOT protected


                return (name, tuple(bases), dct)

                #ret = type(name, tuple(bases), dct)
                #ret = super().__new__(cls, name, tuple(bases), dct)

                # if override:
                #     ret = type(name, tuple(bases), dct)

                    
                # else:
                    

                #     # AKA in classmethof: x = super().__new__(cls, name, tuple(cls_bases), dct)


                #setattr(ret, "__qualname__", name)

            return None












        if "__init__" in clsmethods:
            def __init__(self, *args, **kwargs):

                print ("RUN INIT", args, kwargs)

                __node__params__ =  {}
                #__node__params__.update(self.__node__params__)
                __node__params__.update(getattr(self, f"{prefix}_params__", {}))
                __node__params__.update(kwargs)

                tmp = NodeCtrl(
                    self,
                    obj_attr=prefix,
                    **__node__params__,
                        # Contains:
                        #  obj_conf: {}
                        #  obj_attr: "__node__"
                        #  obj_prefix
                        #  obj_prefix_hooks
                        #  obj_prefix_class_params
                        #  obj_prefix
                )
                setattr(self, prefix , tmp)

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


        if "__getattr__" in clsmethods:
            def __getattr__(self, name):
                """Dunder to foward all unknown attributes to the NodeCtrl instance"""

                if prefix in self.__dict__:
                    return getattr(self, prefix).mixin_get(name)

                msg = f"Getattr '{name}' is not available for '{self}' as there is no nodectrl yet"
                raise errors.CaframAttributeError(msg)


        if "__getitem__" in clsmethods:
            def __getitem__(self, name):
                "Handle dict notation"

                if hasattr(self, prefix):
                    return getattr(self, prefix).mixin_get(name)
                #if self.__node__:
                    #return self.__node__.mixin_get(name)

                msg = f"Getitem is not available as there is no nodectrl yet, can't look for: {name}"
                raise errors.CaframException(msg)


        if "__call__" in clsmethods:
            def __call__(self, *args):
                "Return node or mixin/alias"

                if hasattr(self, prefix):
                #if self.__node__:
                    count = len(args)
                    if count == 0:
                        #return self.__node__
                        return getattr(self, prefix).mixin_get(name)
                    if count == 1:
                        #return self.__node__.mixin_get(args[0])
                        return getattr(self, prefix).mixin_get(args[0])

                    msg = "Only 1 argument is allowed"
                    raise errors.CaframException(msg)

                msg = "Call is not available as there is no nodectrl yet"
                raise errors.CaframException(msg)

    clsmethods.extend([
        prefix,
        f"{prefix}_prefix__",
        f"{prefix}_params__",
    ])


    for key, val in attrs.items():
        setattr(_NodeSkeleton, key, val)
        #_NodeSkeleton.__node__attrs__.append(key)
        #getattr(_NodeSkeleton, f"{prefix}_attrs__").append(key)
        clsmethods.append(key)


    # Prepare __node__ attribute
    setattr(_NodeSkeleton, prefix, None)
    setattr(_NodeSkeleton, f"{prefix}_prefix__", prefix)
    setattr(_NodeSkeleton, f"{prefix}_params__", {})
    setattr(_NodeSkeleton, f"{prefix}_attrs__", clsmethods)
    #setattr(_NodeSkeleton, f"{prefix}_attrs__", list(_NodeSkeleton.__dict__.keys()))




    # Prepare Class
    if name:
        setattr(_NodeSkeleton, "__name__", name) # useless
        setattr(_NodeSkeleton, "__qualname__", name)
    if module:
        setattr(_NodeSkeleton, "__module__", module)
    if doc:
        setattr(_NodeSkeleton, "__doc__", doc)

    # setattr(_NodeSkeleton, "__metaclass__", NodeMetaclass)
    #print ("TOFIX METADATA INHERITANCE")

    return _NodeSkeleton





# Node Metaclass
################################################################


NODE_PREFIX = "__node__"

class NodeMetaclass(type):
    """NodeMetaClass
    
    
    
    """


    def __new__(cls, name, bases, dct,

        node_cls = None,
        node_prefix=None, #"__DEFAULT__",
        node_methods=None,
        node_bases=None,
        node_name=None,
        node_attrs=None,

        node_override=True,
        node_doc=None,
        ):

        name = node_name or name
        w_name = f"{name}Wrapper"
        #w_name = name

        node_prefix = node_prefix or NODE_PREFIX
        node_attrs = node_attrs or {}

        if not node_cls:
            node_cls = node_class_builder(node_prefix, bases=node_bases, clsmethods=node_methods, name=name, attrs=node_attrs)
        


        # Select inheritance strategy



        # pprint (node_cls)
        # pprint ()
        # assert False, "WIP1"


        # ###### EOFFFF

        ret = node_cls.tmp__inherit(cls, bases=bases, attrs=dct, name=name)
        # # # pprint (tmp)
        print ("ARGUMENTS1: ", ret)

        if ret:
            name, bases, dct = ret

            # pprint (ret)
            # print (ret[0], ret[1], ret[2] )
            # pprint (type(ret))
            # pprint (ret.__dict__)
            # assert False
            #x = super().__new__(cls, ret[0], ret[1], ret[2] )

        #     # x = super().__new__(cls, name, tuple(cls_bases), dct)


            #return x

        return super().__new__(cls, name, bases, dct)


        # ###### EOFFFF


        cls_bases = list(bases)


        # Do not reinject class if already present
        base_names = [cls.__name__ for cls in cls_bases]
        if not w_name in base_names:
        #if not cls_node in bases:

            if node_override:
                cls_bases.insert(0, node_cls)
            else:
                cls_bases.append(node_cls)
        else:
            assert False, "TOFIX: Duplicate NodeWrapper"


        # Other tweaks
        if node_doc:
            dct["__doc__"] = node_doc

        # Test inhertiance !!!
        dct["metaclass"] = cls

        # print ("METACLASS NEW 2 ======================== ")
        # print ("METACLASS NEW 2.1, params:", cls, name, bases, dct)
        # # print ("METACLASS NEW 2.2, prefix:", node_prefix, f"(inherited={inherited})")
        # print ("METACLASS NEW 2.2, cls_node:", node_cls)
        # print ("METACLASS NEW 2.2, mro:", cls_bases)
        # print ("METACLASS NEW 2.2, mro:", cls.__mro__)
        # print ("METACLASS NEW 2.2, nodeattr1", getattr(cls, "_node__attr", None))
        # print ("METACLASS NEW 2.2, nodeattr2", dct.get("_node__attr", None))
        # print ("METACLASS NEW 2.2, nodeattr3", tmp)


        print ("ARGUMENTS2: ", name, tuple(cls_bases), dct)
        assert False
        x = super().__new__(cls, name, tuple(cls_bases), dct)


        print ("Actual result:")
        pprint (x)
        pprint (x.__dict__)

        if node_name:
            setattr(x, "__qualname__", node_name)
        return x

    #     # cls = type(metacls, name, bases, namespace)
    #     # cls = type.__new__(metacls, name, bases, namespace)
    #     # cls = super().__new__(metacls, name, bases, namespace)



    # def __init__(self, name, bases, namespace, **kwargs):
    #     # This will never be called because the return type of `__new__` is wrong
    #     print ("NodeMetaclass __init__ SUCCESSS", self, name, bases, namespace, kwargs)
        
    #     self.META_ATTR = "YOLOO"
    #     pass


    # def __new__WIP(cls, name, bases, dct,

    #     node_prefix=None, #"__DEFAULT__",
    #     node_override=True,
    #     #node_root=False,

    #     node_getattr=False,
    #     node_getitem=False,
    #     node_call=False,

    #     ):


    #     #node_prefix = node_prefix or getattr(cls, "_node__attr", None) or NODE_PREFIX

    #     # Look for class name atribute in mro
    #     tmp = dct.get("_node__attr", None)
    #     inherited = False
    #     if not tmp:
    #         for base in bases:
    #             tmp = getattr(base, "_node__attr", None)
    #             if tmp:
    #                 inherited = True
    #                 break

    #     node_prefix = node_prefix or tmp or NODE_PREFIX
    #     cls_node = node_class_builder(node_prefix)


    #     # WIPPP
    #     node_params = {key: val for key, val in dct.items() if key.startswith(f"_node__")}
    #     #pprint (node_params)
    #     #pprint (dir(cls))


    #     # prefix config: _node__attr
    #     # WIP ????
    #     cls_bases = list(bases)
    #     # if node_root:
    #     #     del cls_bases[0]
    #     if node_override:
    #         cls_bases.insert(0, cls_node)
    #     else:
    #         cls_bases.append(cls_node)



    #     # print ("METACLASS NEW 2 ======================== ")
    #     # print ("METACLASS NEW 2.1, params:", cls, name, bases, dct)
    #     # print ("METACLASS NEW 2.2, prefix:", node_prefix, f"(inherited={inherited})")
    #     # print ("METACLASS NEW 2.2, mro:", cls_bases)
    #     # print ("METACLASS NEW 2.2, mro:", cls.__mro__)
    #     # print ("METACLASS NEW 2.2, cls_node:", cls_node)
    #     # print ("METACLASS NEW 2.2, nodeattr1", getattr(cls, "_node__attr", None))
    #     # print ("METACLASS NEW 2.2, nodeattr2", dct.get("_node__attr", None))
    #     # print ("METACLASS NEW 2.2, nodeattr3", tmp)


    #     #x = super().__new__(cls, name, tuple(cls_bases), dct)
    #     #x = super().__new__(cls, name, bases , dct)
    #     x = super().__new__(cls, name, tuple(cls_bases), dct)

    #     return x

    #     # Minimal placeholder
    #     # cls = super().__new__(metacls, name, bases, namespace, **kwargs)
    #     # # You must return the generated class
    #     # return cls






# Decorators
################################################################



class NodeWrapper():

    node_prefix = "__NodeWrapper__"

    def __init__(self, prefix=None, name=None, bases=None, 
        methods=None, override=None, attrs=None,
        ):
        "Init params"


        self.node_prefix = prefix or NODE_PREFIX
        name = name or "NodeDeco"

        print ("PREFIX", prefix)

        self._override = override if isinstance(override, bool) else True
        attrs = attrs or {}

        # State vars
        # self._base_node_cls = NodeMetaclass(
        #     "NodeCtx", (), {"ATTR1":True, "__doc__":"Custom doc"}, 
        #     **kwargs)

        self._base_node_cls = node_class_builder(
            self.node_prefix, 
            bases=bases, 
            clsmethods=methods, 
            name=name,
            attrs=attrs,
            )


    def newNode(self, override=None, **kwargs): #, *args, **kwargs):
        """
        Transform a class to a NodeClass WITH LIVE PATCH
        
        Forward all kwargs to NodeCtrl()
        """

        #assert not "obj_mixins" in kwargs, f"Usage of obj_mixins in decorator is forbidden, please use 'addMixin' instea"

        # Decorator arguments
        base_cls = self._base_node_cls
        if not isinstance(override, bool):
            override = self._override   

        def _decorate(cls):

            
            patch = False


            print ("==== DECORATOR CLS INFO", cls)
            print ("== Type", type(cls))
            print ("== Name", cls.__name__)
            print ("== QUALNAME", cls.__qualname__)
            print ("== MODULE", cls.__module__)
            print ("== DICT", cls.__dict__)

            ret = cls

            if patch:
                ret = base_cls.tmp__patch__(ret)
            else:


                # # ###### EOFFFF
                # self._base_node_cls

                ret = self._base_node_cls.tmp__inherit(cls, name=cls.__qualname__)
                # # # pprint (tmp)
                print ("ARGUMENTS1: ", ret)

                if ret:
                    name, bases, dct = ret

                return type(name, bases, dct)


                # #return super().__new__(cls, name, bases, dct)


                # # WIPPPPP EOF


            #     if not base_cls in cls.__mro__:

            #         dct = {}
            #         #dct = cls.__dict__
            #         #name = cls.__name__
            #         name = cls.__qualname__
            #         module = cls.__module__

            #         # This returns a new object because we change inheritance

            #         if override:
            #             # Create a new class WrapperClass that inherit from defined class
            #             print ("NODE OVERRIDE", name, tuple([base_cls, cls]), dct)
            #             ret = type(name, tuple([base_cls, cls]), dct)

            #             # Pros:
            #             #   * Easy and ready to use
            #             #   * Important methods are protected
            #             # Cons: 
            #             #   * BREAK standard inheritance model
            #             #   * All your attributes disapears on __dir__, unless dct=cls.__dict__
            #             #   * HIgh level of magic
            #         else:
            #             # Append in the end WrapperClass inheritance
            #             print ("NODE INHERIT", name, tuple([cls, base_cls]), dct)
            #             ret = type(name, tuple([cls, base_cls]), dct)
            #             # Pros:
            #             #   * Respect standard inheritance model
            #             #   * All your attributes/methods apears on __dir__
            #             #   * Not that magic
            #             # Cons: 
            #             #   * Important methods  NOT protected


            #     setattr(ret, "__module__", module)

            #     # assert False
            # return ret

            # self._base_node_cls


            # type(cls_name, (cls_base, cls), {})



            # # Create main parameters
            # node_params = {
            #     "obj_clean": False,
            #     "obj_attr": "__node__",
            # }
            # node_params.update(kwargs)


            # # __node__mixins__
            # # __node__params__

            # # Create mixin configs
            # node_mixins = dict(getattr(cls, "__node__mixins__", {}))
            # node_params["obj_mixins"] = node_mixins
            

            # # Generate a new Node Class
            # ret = "WIPPPP"
            # # ret = NodeWrapperConfGenerator(cls,
            # #     override=override,
            # #     extra_attr={"__node__params__": node_params},  # Forward nodectrl init params

            # #     enable_getattr=enable_getattr, # None=> enable if nothing present, True => Always, False => Never
            # #     enable_getitem=enable_getitem,
            # #     enable_call=enable_call,

            # # )


            # self._base_node_cls

            # ret = super().__new__(cls, name, tuple(cls_bases), dct)

            # # type(cls_name, (cls_base, cls), {})

            # if node_name:
            #     setattr(x, "__qualname__", node_name)

            # return ret

        return _decorate


    def newNode_V1(self,

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
            ret = "WIPPPP"
            # ret = NodeWrapperConfGenerator(cls,
            #     override=override,
            #     extra_attr={"__node__params__": node_params},  # Forward nodectrl init params

            #     enable_getattr=enable_getattr, # None=> enable if nothing present, True => Always, False => Never
            #     enable_getitem=enable_getitem,
            #     enable_call=enable_call,

            # )

            # print ("1. New Wrapped Node", ret)
            # pprint (ret.__dict__)

            return ret

        return _decorate





    def addMixin(self, mixin, mixin_key=None, mixin_conf=None, **kwargs):
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







# Common default instance
################################################################



# Generic default node class with metaclass
#class NodeV2(Node, metaclass=NodeMetaclass, node_prefix="__nodev2__"):
#class Node( metaclass=NodeMetaclass, node_prefix="__nodev2__"):

class Node(CaframNode, metaclass=NodeMetaclass):
#class Node(metaclass=NodeMetaclass):
    "Default Cafram Node"

    ATTR1 = True

    def node_method(self):
        print ("Hello node_method")
        return True

    # def __init__(self):
    #     print ("NODE INITEDDDDDD")

    #     super().__init__()





# DECORATORS
################################################################



# print ("============== RECAP")
# pprint (Node)
# #pprint (Node.__mro__)
# pprint (Node.__dict__)
# print ("==============")



Node2 = None
#Node = NodeMetaclass.dyn_class("__nodev2__", name="TOTO", package="TITI")
#Node = NodeMetaclass.dyn_class("__nodev2__", name="Node2")
#Node = node_class_builder("__nodev2__", name="Node2", doc="Default Cafram Nodev2", module="faked")

#Node = node_class_builder("__nodev2__", name="Node2", doc="Default Cafram Nodev2", bases=)

Node2 = NodeMetaclass("Node", (), {"ATTR1":True, "__doc__":"Custom doc"}, node_bases=[CaframNode], node_override=True, node_doc="Custom doc")

# CaframNode
# CaframNode

# print ("==============")
# pprint (Node2)
# pprint (Node2.__mro__)
# pprint (Node2.__dict__)

# print ("==============")












































# if False:



#     class Node3(metaclass=NodeMetaclass, node_prefix="__nodev2__"):
#         "Node Override"




#     # In library: myapp.py
#     # -------------------

#     from cafram.nodes2 import Node


#     def test_default_nodecls():
#         "Test default node cls"

#         print ("NEW NODE DUMP")
#         pprint(NodeV2.__dict__)
#         #pprint(dir(NodeV2))

#         anode = NodeV2()
#         pprint(anode.__dict__)

#         pprint (anode.META_ATTR)

#         assert anode.node_method() == True
#         assert False

#         print ("OLD NODE DUMP")
#         pprint (Node)
#         #pprint (dir(Node))
#         anode = Node()
#         pprint(anode.__dict__)

#         print ("OLD NODE DUMP3")
#         pprint (Node3)
#         #pprint (dir(Node3))

#     test_default_nodecls()

#     assert False, "WIPPP"

#     def test_simple_class_def():
#         "Test good functionning of MixinConfigLoader"


#         class MyParentClass(NodeV2):
#             _node__attr = "__APP_OVERRIDE__"
#             _node__debug = False

#             attr1 = True

#             def method1(self):
#                 print ("Hello method2")


#         class MyClass(MyParentClass):

#             attr2 = True

#             def method2(self):
#                 print ("Hello method1")


#         # Instanciate
#         app1 = MyParentClass()
#         app2 = MyClass()

#         # Test methods
#         app1.method1()
#         app2.method1()
#         app2.method2()


#         print ("DUMPPPP")
#         pprint (app1.__dict__)
#         pprint (app2.__dict__)
#         pprint (MyParentClass.__dict__)
#         pprint (MyClass.__dict__)
#         pprint (dir(app1))
#         pprint (dir(app2))

#         pprint (NodeV2.__dict__)
#         app1.node_method()

#         # Tests
#         app1.DYN_NODE_ALWAYS()


#     print ("START TESTS")

#     test_simple_class_def()

#     print ("OKKKKKKKK EOFFF")
#     assert False, "OOKKKK WIPPP"





#     ##########################

#     # In user code
#     # -------------------
#     #class MyParentClass(NodeV2, node_prefix="__mine__", node_getattr=True, node_override=True):
#     class MyParentClass(NodeV2):
#         "Node Override"

#         _node__attr = "__APP_OVERRIDE__"
#         _node__debug = False

#         def method2(self):
#             print ("Hello method2")


#     class MyClass(MyParentClass):

#         def method1(self):
#             print ("Hello method1")



#     #app = MyClass(prefix="__NODE666__FORBIDDEN")
#     appParent = MyParentClass()
#     app = MyClass()

#     print ("\nRESULLLLTTTT=========")
#     # app.method1()
#     # app.method2()
#     # #app.extra_method("args1")
#     # #app.metamethod()
#     pprint(appParent.__dict__)
#     pprint(app.__dict__)

#     pprint (appParent._node__attr)
#     pprint (app._node__attr)


#     # # In user code with decorators
#     # # -------------------


#     # from cafram.decorators import newNode, addMixin
#     # import logging
#     # from cafram.mixins.tree import ConfDictMixin as TOTO
#     # @newNode(prefix="__node333__")
#     # @addMixin("cafram.mixins.base:LoggerMixin")
#     # @addMixin("cafram.mixins.tree:ConfOrderedMixin", # "titi",
#     #     mixin_logger_level= logging.DEBUG,

#     #     children=True,
#     # )
#     # class MyApp2():
#     #     "This is my main app"




#     # print ("APP DECO")
#     # app = MyClass(prefix="__NODE__")
#     # app.method1()
#     # app.method2()
#     # pprint(app.__dict__)
