"""
Provide Node Engine
"""

import inspect
from pprint import pprint
from typing import List, Optional, Union

import cafram.nodes.errors as errors
from cafram.lib.utils import import_module #, merge_dicts, merge_keyed_dicts
from cafram.nodes.ctrl import NodeCtrl, PrefixMgr






# Node NodeFactory
################################################################


class NodeFactory(PrefixMgr):
    "Helpers to patch wrapper config"


    ####### BETAAAA

    def node_class_builder2(self,
        name="NodeWrapper",
        module=None,
        doc=None,

        # bases=None,
        clsmethods=None,

        attrs=None,
    ):
        """Build a generic node wrapper

        """

        prefix = self.prefix


        # NODE_METHODS = [
        #     "__node__",
        #     "__init__",
        #     "__getattr__",
        #     "__getitem__",
        #     "__call__",
        # ]


        class _NodeWrapper():
            """Dynamic Node Class

            Node ctrl access:
            node(): Return Node instance
            node("MIXIN"): Return mixin instance
            node.ALIAS: Return requested ALIAS

            """

            __node_class__ = None
            __node_prefix__ = prefix
            __node_attrs__ = [
                    prefix,

                    # "__node__",
                    "__node_prefix__",
                    "__node_attrs__",
                    "__node_class__",

                    "__init__",
                    "__getattr__",
                    "__getitem__",
                    "__call__",
                ]

            def __init__(self, *args, **kwargs):
                "Attach a NodeCtrl to this instance"

                NodeCtrl(
                    self,
                    *args,
                    obj_attr=self.__node_prefix__,
                    obj_wrapper_class=self.__node_class__,
                    **kwargs,
                )


            def __getattr__(self, name):
                """Dunder to foward all unknown attributes to the NodeCtrl instance"""

                extra_help = ""
                if prefix in self.__dict__:
                    try:
                        return getattr(self, prefix).alias_get(name)
                    except errors.MissingAlias:
                        extra_help = " " + getattr(self, prefix).dev_help()

                msg = f"Getattr '{name}' is not available for '{self}' as there is no nodectrl yet.{extra_help}"
                raise AttributeError(msg)

            def __setattr__(self, name, value):
                """Dunder to update things"""

                if prefix in self.__dict__:
                    try:
                        return getattr(self, prefix).set_alias(name, value)
                    except errors.MissingAlias:
                        pass

                self.__dict__[name] = value

            def __getitem__(self, name):
                "Handle dict notation"

                if hasattr(self, prefix):
                    try:
                        return getattr(self, prefix).node_get(name)
                    except errors.MissingCtrlAttr:
                        pass

                msg = (
                    "Getitem is not available as there is no nodectrl yet,"
                    f"can't look for: {name}"
                )
                raise errors.MissingCtrlAttr(msg)

            def __call__(self, *args):
                "Return node or mixin/alias"

                if hasattr(self, prefix):
                    count = len(args)
                    if count == 0:
                        return getattr(self, prefix).mixin_get(None)
                    if count == 1:
                        return getattr(self, prefix).mixin_get(args[0])

                    msg = "Only 0 or 1 argument is allowed"
                    raise TypeError(msg)

                msg = "Call is not callable as there is no nodectrl yet"
                raise TypeError(msg)


        # Class manipulation 
        ########################


        # Test arguments
        attrs = attrs or {}
        clsmethods = list( _NodeWrapper.__node_attrs__ if clsmethods is None else clsmethods)

        # Fetch all method from template Wrapper
        _node_methods = {}
        for _name in clsmethods:
            _node_methods[_name] = getattr(_NodeWrapper, _name, None)

        for key, val in attrs.items():
            _node_methods[key] = val
            clsmethods.append(key)

        _node_methods["__node_attrs__"] = clsmethods

        # Instanciate Node
        ret = type(name, (), _node_methods)
        ret.__node_class__ = ret

        # Prepare Node
        self._prepare_wrapper_cls_settings(ret, name=name, module=module, doc=doc)

        return ret



    # Methods for class generation
    # -----------------------------


    def _prepare_wrapper_cls_settings(self, cls, name=None, module=None, doc=None):
        "Set name, module and documentation of the class"

        # Prepare Class
        if name:
            # See: https://answall.com/a/339521/
            setattr(cls, "__name__", name)
            setattr(cls, "__qualname__", name)
        if module:
            setattr(cls, "__module__", module)
        if doc:
            setattr(cls, "__doc__", doc)

        # Prepare __node__ attribute
        prefix = self.prefix
        if prefix:

            # NodeCtrl attrs
            # setattr(cls, prefix, None)
            setattr(cls, f"{prefix}_prefix__", prefix)

            # Class attrs
            # setattr(cls, f"{prefix}_param_obj_wrapper_class__", cls)

            # Decorator attrs
            setattr(cls, f"{prefix}_params__", {})
            setattr(cls, f"{prefix}_mixins__", {})

            


    # Methods for class patching
    # -----------------------------



    def node_patch_params(self, cls, node_cls, override=True):
        "Patch a class to become a node"

        # Patch object if not patched
        # ------------------------
        if node_cls in cls.__mro__:
            print(f"Skipping Wrapping Node {cls} with {node_cls}")
            return cls


        # print(f"Wrapping Node {cls} with {node_cls} (Override={override})")
        prefix = self.prefix
        node_prefix = getattr(node_cls, "__node_prefix__")
        node_attrs = getattr(node_cls, "__node_attrs__")


        for attr_name in node_attrs:

            if override is False:
                if hasattr(cls, attr_name):
                    tot = getattr(cls, attr_name)
                    print("Skip method patch", attr_name, tot)
                    continue

            method = getattr(node_cls, attr_name)
            setattr(cls, attr_name, method)

        # setattr(cls, f"{node_prefix}_param_obj_wrapper_class__", node_cls)

        return cls


    def node_patch_mixin(self, cls, conf):
        "Add a mixin configuration to class"

        prefix = self.prefix

        # Fetch mixin class
        assert "mixin" in conf

        mixin = conf["mixin"]
        if isinstance(mixin, str):
            mixin_cls = import_module(mixin)
        else:
            mixin_cls = mixin

        mixin_key = conf.get("mixin_key", mixin_cls.mixin_key)
        if mixin_key is True:
            mixin_key = mixin_cls.mixin_key

        assert isinstance(mixin_key, str)

        mixin_confs = getattr(cls, f"{prefix}_mixins__", {})
        # mixin_confs2 = getattr(cls, f"{prefix}_mixins2__", [])

        mixin_confs[mixin_key] = conf
        # mixin_confs2.append(conf)

        setattr(cls, f"{prefix}_mixins__", mixin_confs)
        # setattr(cls, f"{prefix}_mixins2__", mixin_confs2)

        return cls


    # # OLD: node_inherit
    # #@staticmethod
    # def prepare_wrapper_cls_inherit(self, obj, node_cls, name=None, bases=None, override=True, attrs=None):
    #     "Create a new class from any class and make the node as it's ancestors"

    #     # Assert obj is a class

    #     # print("CALLL node_inherit", node_cls, obj, name, attrs)

    #     dct = attrs or {}
    #     bases = list(bases or [])
    #     name = name or obj.__qualname__
    #     prefix = self.prefix

    #     # Do not reinject class if already present
    #     # base_names = [node_cls.__name__ for node_cls in bases]
    #     # if not w_name in base_names:
    #     if node_cls not in bases:

    #         if name:
    #             dct["__qualname__"] = name

    #         if override:
    #             # Create a new class WrapperClass that inherit from defined class

    #             # print("NODE OVERRIDE", name, node_cls.__qualname__, tuple(bases), dct)
    #             bases.insert(0, node_cls)

    #             # Pros:
    #             #   * Easy and ready to use
    #             #   * Important methods are protected
    #             # Cons:
    #             #   * BREAK standard inheritance model
    #             #   * All your attributes disapears on __dir__, unless dct=node_cls.__dict__
    #             #   * HIgh level of magic
    #         else:
    #             # Append in the end WrapperClass inheritance

    #             # print("NODE INHERIT", name, node_cls.__module__, tuple(bases), dct)
    #             bases.append(node_cls)

    #             # Pros:
    #             #   * Respect standard inheritance model
    #             #   * All your attributes/methods apears on __dir__
    #             #   * Not that magic
    #             # Cons:
    #             #   * Important methods  NOT protected

    #         setattr(
    #             obj,
    #             f"{prefix}_attrs__",
    #             getattr(node_cls, f"{prefix}_attrs__", {}),
    #         )
    #         setattr(obj, f"{prefix}_prefix__", prefix)
    #         # setattr(obj, f"{prefix}_class__", node_cls)
    #         setattr(obj, f"{prefix}_param_obj_wrapper_class__", node_cls)

    #         # 

    #         return (name, tuple(bases), dct)
    #     return None




# Node Wrapper Class Builder
################################################################




# # This is a class method
# # @functools.cache
# def node_class_builder(
#     prefix,
#     name="NodeWrapper",
#     module=None,
#     doc=None,

#     # bases=None,
#     clsmethods=None,

#     attrs=None,
# ):
#     """Build a generic node wrapper

#     :param prefix: Name of the Node prefix
#     :type prefix: str

#     :param name: _description_, defaults to None
#     :type name: _type_, optional

#     :param bases: _description_, defaults to None
#     :type bases: _type_, optional

#     :param clsmethods: List, defaults to None
#     :type clsmethods: Union[List[str],None], optional

#     :param module: _description_, defaults to None
#     :type module: _type_, optional

#     :param doc: _description_, defaults to None
#     :type doc: _type_, optional

#     :param attrs: _description_, defaults to None
#     :type attrs: _type_, optional

#     :raises errors.BadArguments: _description_
#     :raises errors.CaframAttributeError: _description_
#     :raises errors.CaframException: _description_
#     :raises errors.CaframException: _description_
#     :raises errors.CaframException: _description_

#     :return: _description_
#     :rtype: _type_


#     :Explanations:



#     :Code Example 1:

#         >>> class Node(CaframNode, metaclass=NodeMetaclass,
#             node_prefix='__node__', node_override=False
#             ):
#                 "My DocString"
#                 ATTR1 = True

#     :Code Example 2:

#         Yoloo This version has not metadata for children classes

#         >>> Node1 = NodeMetaclass(
#                 "Node", (), {"ATTR1":True, "__doc__":"My DocString"},
#                 node_override=True,
#                 node_prefix='__node__',
#                 node_bases=[CaframNode])

#         TOFIX: This version has not metadata *for* **children** classes

#         >>> Node2 = node_class_builder("__node__", name="Node",
#                 doc="My DocString", bases=[CaframNode])
#                 # => node_override=False

#         # Expected result:

#         >>> assert Node == Node1
#         >>> assert Node == Node2


#         # And for the subsequent Nodes:

#         # Ex1:

#         >>> class AppObj():
#             "Parent class"

#         # Ex1.a:

#         >>> class MyApp(AppObj, Node):
#             "App class"

#     """

#     assert False, "DEPRECATED"
#     print ("GENERATE NEW CLASS")


#     # Test arguments
#     attrs = attrs or {}
#     if clsmethods is None:
#         clsmethods = NODE_METHODS
#     clsmethods = list(clsmethods)

#     # bases = tuple(bases or [])
#     bases = tuple([])
#     assert isinstance(bases, tuple), f"Got: {bases} (type={type(bases)})"


#     class _NodeWrapper(*bases):
#         """Dynamic Node Class

#         Node ctrl access:
#         node(): Return Node instance
#         node("MIXIN"): Return mixin instance
#         node.ALIAS: Return requested ALIAS

#         """

#         def __init__(self, *args, **kwargs):
#             "Attach a NodeCtrl to this instance"

#             print ("NODE INIT", self, kwargs)

#             NodeCtrl(
#                 self,
#                 *args,
#                 obj_attr=prefix,
#                 **kwargs,
#             )


#         def __getattr__(self, name):
#             """Dunder to foward all unknown attributes to the NodeCtrl instance"""

#             extra_help = ""
#             if prefix in self.__dict__:
#                 try:
#                     return getattr(self, prefix).alias_get(name)
#                 except errors.MissingAlias:
#                     extra_help = " " + getattr(self, prefix).dev_help()

#             msg = f"Getattr '{name}' is not available for '{self}' as there is no nodectrl yet.{extra_help}"
#             raise AttributeError(msg)

#         def __setattr__(self, name, value):
#             """Dunder to update things"""

#             if prefix in self.__dict__:
#                 try:
#                     return getattr(self, prefix).set_alias(name, value)
#                 except errors.MissingAlias:
#                     pass

#             self.__dict__[name] = value

#         def __getitem__(self, name):
#             "Handle dict notation"

#             if hasattr(self, prefix):
#                 try:
#                     return getattr(self, prefix).node_get(name)
#                 except errors.MissingCtrlAttr:
#                     pass

#             msg = (
#                 "Getitem is not available as there is no nodectrl yet,"
#                 f"can't look for: {name}"
#             )
#             raise errors.MissingCtrlAttr(msg)

#         def __call__(self, *args):
#             "Return node or mixin/alias"

#             if hasattr(self, prefix):
#                 count = len(args)
#                 if count == 0:
#                     return getattr(self, prefix).mixin_get(None)
#                 if count == 1:
#                     return getattr(self, prefix).mixin_get(args[0])

#                 msg = "Only 0 or 1 argument is allowed"
#                 raise TypeError(msg)

#             msg = "Call is not callable as there is no nodectrl yet"
#             raise TypeError(msg)


#     # Class manipulation 
#     ########################

#     BETA_MODE = "v2"

#     if BETA_MODE == "v1":
#         # Copy parent class and remove extra methods
#         for met in NODE_METHODS:
#             if met not in clsmethods:
#                 delattr(_NodeWrapper, met)

#         ret = _NodeWrapper

#     else:
#         # Build a fresh class from the template
#         node_methods = {}
#         for _name in clsmethods:
#             node_methods[_name] = getattr(_NodeWrapper, _name)

#         ret = type(name, bases, node_methods)


#     clsbuilder = NodeFactory(prefix=prefix)

#     clsbuilder.prepare_wrapper_cls_attrs(ret, clsmethods=clsmethods, attrs=attrs)
#     clsbuilder.prepare_wrapper_cls_settings(ret, name=name, module=module, doc=doc)

#     return ret




# Node Metaclass
################################################################


NODE_PREFIX = "__node__"


class NodeMetaclass(type):
    """NodeMetaClass"""

    # node_prefix = "__node__"
    node_prefix = NODE_PREFIX
    node_cls = None

    def __new__(
        mcs,
        name,
        bases,
        dct,

        module=None,
        doc=None,

        node_cls=None,

        node_prefix=None,
        node_name=None,
        node_module=None,
        node_methods=None,
        node_attrs=None,
        node_override=True,
        node_doc=None,
    ):


        node_prefix = node_prefix or mcs.node_prefix
        clsbuilder = NodeFactory(prefix=node_prefix)


        # Create a root Node if not provided
        if not node_cls:

            node_name = node_name or name
            node_attrs = node_attrs or {}

            node_cls = clsbuilder.node_class_builder2(
                name=node_name,
                module=node_module,
                # bases=node_bases,
                clsmethods=node_methods,
                attrs=node_attrs,
                doc=node_doc,
            )

        cls = super().__new__(mcs, name, tuple(bases), dct)
        return clsbuilder.node_patch_params(cls, node_cls, override=node_override)
        # return ret



        # patch = True
        # if patch:
        #     cls = super().__new__(mcs, name, tuple(bases), dct)
        #     ret = clsbuilder.node_patch_params(cls, node_cls, override=node_override)
        #     return ret

        # else:
        #     ret = clsbuilder.prepare_wrapper_cls_inherit(mcs, node_cls, bases=bases, attrs=dct, name=name, override=node_override)
        #     if ret:
        #         name, bases, dct = ret

        #     if doc:
        #         dct["__doc__"] = doc
        #     if module:
        #         dct["__module__"] = module

        #     # Return a new class
        #     return super().__new__(mcs, name, tuple(bases), dct)




    # def __new__V1(
    #     mcs,
    #     name,
    #     bases,
    #     dct,

    #     module=None,
    #     doc=None,

    #     node_cls=None,

    #     node_prefix=None,  # "__DEFAULT__",
    #     node_name=None,
    #     node_module=None,

    #     node_bases=None,
    #     node_methods=None,
    #     node_attrs=None,
    #     node_override=True,
    #     node_doc=None,
    # ):

    #     node_name = node_name or name
    #     node_prefix = node_prefix or mcs.node_prefix
    #     node_attrs = node_attrs or {}

    #     # Create a root Node if not provided
    #     # if not node_cls and not mcs.node_cls:
    #     if not node_cls:
    #         node_cls = node_class_builder(
    #             node_prefix,
    #             name=node_name,
    #             module=node_module,
    #             bases=node_bases,
    #             clsmethods=node_methods,
    #             attrs=node_attrs,
    #             doc=node_doc,
    #         )
    #     # mcs.node_cls = node_cls

    #     # Generate type arguments
    #     clsbuilder = NodeFactory(prefix=node_prefix)


    #     ret = clsbuilder.prepare_wrapper_cls_inherit(mcs, node_cls, bases=bases, attrs=dct, name=name, override=node_override)
    #     if ret:
    #         name, bases, dct = ret

    #     if doc:
    #         dct["__doc__"] = doc
    #     if module:
    #         dct["__module__"] = module

    #     # Return a new class
    #     return super().__new__(mcs, name, bases, dct)



# Decorators
################################################################


class NodeDecorator:
    "Wrap any object"

    # node_prefix = "__node__"
    node_prefix = NODE_PREFIX

    def __init__(
        self,
        node_cls=None,
        override=None,
    ):
        "Init Decorator"

        self.node_cls = node_cls
        self._override = override if isinstance(override, bool) else True

        assert node_cls, f"Got: {node_cls}"

        prefix = getattr(node_cls, "__node_prefix__", self.node_prefix)
        self.node_factory = NodeFactory(prefix=prefix)


    def new_node(self, override=None):
        """
        Transform a class to a NodeClass WITH LIVE PATCH

        Forward all kwargs to NodeCtrl()
        """

        # Decorator arguments
        def _decorate(cls):
            return self.node_factory.node_patch_params(cls, self.node_cls, override=override)

        return _decorate

    def add_comp(self, mixin, mixin_key=None, mixin_conf=None, **kwargs):
        "Add features/mixins to class"

        # Get mixin config
        mixin_conf = mixin_conf or kwargs

        # Validate data
        assert isinstance(mixin_conf, dict)

        mixin_def = dict(mixin_conf)
        mixin_def.update({"mixin": mixin})
        if mixin_key is not None:
            mixin_def.update({"mixin_key": mixin_key})


        def _decorate(cls):
            return self.node_factory.node_patch_mixin(cls, mixin_def)

        return _decorate
