"""
Provide Node Engine
"""

import inspect
from pprint import pprint
from typing import List, Optional, Union

import cafram.nodes.errors as errors
from cafram.lib.utils import import_module #, merge_dicts, merge_keyed_dicts
from cafram.nodes.ctrl import NodeCtrl, WrapperPatcher

NODE_METHODS = [
    "__init__",
    "__getattr__",
    "__getitem__",
    "__call__",
]


# Node Wrapper Class Builder
################################################################




# This is a class method
# @functools.cache
def node_class_builder(
    prefix,
    name="NodeWrapper",
    bases=None,
    clsmethods=None,
    module=None,
    doc=None,
    attrs=None,
):
    """Build a generic node wrapper

    :param prefix: Name of the Node prefix
    :type prefix: str

    :param name: _description_, defaults to None
    :type name: _type_, optional

    :param bases: _description_, defaults to None
    :type bases: _type_, optional

    :param clsmethods: List, defaults to None
    :type clsmethods: Union[List[str],None], optional

    :param module: _description_, defaults to None
    :type module: _type_, optional

    :param doc: _description_, defaults to None
    :type doc: _type_, optional

    :param attrs: _description_, defaults to None
    :type attrs: _type_, optional

    :raises errors.BadArguments: _description_
    :raises errors.CaframAttributeError: _description_
    :raises errors.CaframException: _description_
    :raises errors.CaframException: _description_
    :raises errors.CaframException: _description_

    :return: _description_
    :rtype: _type_


    :Explanations:



    :Code Example 1:

        >>> class Node(CaframNode, metaclass=NodeMetaclass,
            node_prefix='__node__', node_override=False
            ):
                "My DocString"
                ATTR1 = True

    :Code Example 2:

        Yoloo This version has not metadata for children classes

        >>> Node1 = NodeMetaclass(
                "Node", (), {"ATTR1":True, "__doc__":"My DocString"},
                node_override=True,
                node_prefix='__node__',
                node_bases=[CaframNode])

        TOFIX: This version has not metadata *for* **children** classes

        >>> Node2 = node_class_builder("__node__", name="Node",
                doc="My DocString", bases=[CaframNode])
                # => node_override=False

        # Expected result:

        >>> assert Node == Node1
        >>> assert Node == Node2


        # And for the subsequent Nodes:

        # Ex1:

        >>> class AppObj():
            "Parent class"

        # Ex1.a:

        >>> class MyApp(AppObj, Node):
            "App class"

    """

    # Test arguments
    attrs = attrs or {}
    if clsmethods is None:
        clsmethods = NODE_METHODS
    clsmethods = list(clsmethods)

    bases = bases or []  # Example: (CaframNode, Fake)
    if not isinstance(bases, tuple):
        bases = tuple(bases)
    assert isinstance(bases, tuple), f"Got: {bases} (type={type(bases)})"


    class _NodeSkeleton(*bases):
        """Dynamic Node Class

        Node ctrl access:
        node(): Return Node instance
        node("MIXIN"): Return mixin instance
        node.ALIAS: Return requested ALIAS

        """

        def __init__(self, *args, **kwargs):
            "Attach a NodeCtrl to this instance"

            NodeCtrl(
                self,
                *args,
                obj_attr=prefix,
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

    BETA_MODE = "v2"

    if BETA_MODE == "v1":

        for met in NODE_METHODS:
            if met not in clsmethods:
                delattr(_NodeSkeleton, met)

        ret = _NodeSkeleton

    else:
        # pprint(clsmethods)

        node_methods = {}
        for _name in clsmethods:
            node_methods[_name] = getattr(_NodeSkeleton, _name)

        ret = type(name, bases, node_methods)


    clsbuilder = WrapperPatcher(prefix=prefix)

    clsbuilder.prepare_wrapper_cls_attrs(ret, clsmethods=clsmethods, attrs=attrs)
    clsbuilder.prepare_wrapper_cls_settings(ret)
    clsbuilder.prepare_wrapper_cls(ret, name=name, module=module, doc=doc)

    return ret





# Node Metaclass
################################################################


NODE_PREFIX = "__node__"


class NodeMetaclass(type):
    """NodeMetaClass"""

    node_prefix = "__node__"

    def __new__(
        mcs,
        name,
        bases,
        dct,
        node_cls=None,
        node_prefix=None,  # "__DEFAULT__",
        node_methods=None,
        node_bases=None,
        node_name=None,
        node_attrs=None,
        node_override=True,
        node_doc=None,
    ):

        name = node_name or name
        node_prefix = node_prefix or mcs.node_prefix
        node_attrs = node_attrs or {}

        # Create a root Node if not provided
        if not node_cls:
            node_cls = node_class_builder(
                node_prefix,
                bases=node_bases,
                clsmethods=node_methods,
                name=name,
                attrs=node_attrs,
            )


        # Generate type arguments
        clsbuilder = WrapperPatcher(prefix=node_prefix)
        ret = clsbuilder.prepare_wrapper_cls_inherit(mcs, node_cls, bases=bases, attrs=dct, name=name, override=node_override)
        if ret:
            name, bases, dct = ret


        if node_doc:
            dct["__doc__"] = node_doc

        # Return a new class
        return super().__new__(mcs, name, bases, dct)


# Decorators
################################################################


class NodeWrapper:
    "Wrap any object"

    node_prefix = "__NodeWrapper__"

    def __init__(
        self,
        prefix=None,
        name=None,
        bases=None,
        methods=None,
        override=None,
        attrs=None,
    ):
        "Init params"

        self.node_prefix = prefix or NODE_PREFIX
        name = name or "NodeDeco"


        self._override = override if isinstance(override, bool) else True
        attrs = attrs or {}

        self._base_node_cls = node_class_builder(
            self.node_prefix,
            bases=bases,
            clsmethods=methods,
            name=name,
            attrs=attrs,
        )
        self._clsbuilder = WrapperPatcher(prefix=self.node_prefix)

    def newNode(self, override=None, patch=True):  # , *args, **kwargs):
        """
        Transform a class to a NodeClass WITH LIVE PATCH

        Forward all kwargs to NodeCtrl()
        """

        # Decorator arguments
        base_cls = self._base_node_cls
        if not isinstance(override, bool):
            override = self._override

        
        clsbuilder = self._clsbuilder

        def _decorate(cls):

            ret = cls
            if patch:
                ret = clsbuilder.node_patch_params(cls, base_cls, override=override)
            else:
                ret = clsbuilder.prepare_wrapper_cls_inherit(cls, base_cls, name=cls.__qualname__, override=override)
                if ret:
                    name, bases, dct = ret
                ret = type(name, bases, dct)

            return ret

        return _decorate

    def addMixin(self, mixin, mixin_key=None, mixin_conf=None, **kwargs):
        "Add features/mixins to class"

        # Get mixin config
        mixin_conf = mixin_conf or kwargs

        clsbuilder = self._clsbuilder

        # Validate data
        assert isinstance(mixin_conf, dict)
        # assert isinstance(mixin_key, str)

        mixin_def = dict(mixin_conf)
        mixin_def.update({"mixin": mixin})
        if mixin_key is not None:
            mixin_def.update({"mixin_key": mixin_key})


        def _decorate(cls):

            cls = clsbuilder.node_patch_mixin(cls, mixin_def)
            return cls

        return _decorate
