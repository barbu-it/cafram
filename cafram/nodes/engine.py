"""
Provide Node Engine
"""

import inspect
from pprint import pprint
from typing import List, Optional, Union

from cafram import errors
from cafram.lib.utils import import_module, merge_dicts, merge_keyed_dicts
from cafram.nodes.ctrl import NodeCtrl, get_mixin_loading_order

NODE_METHODS = [
    "__init__",
    "__getattr__",
    "__getitem__",
    "__call__",
]


# Node Wrapper Class Builder
################################################################


def _obj_filter_attrs_by(
    obj, prefix=None, suffix=None, strip=True, rtrim="_", level_max=0, level_split="__"
):
    "Filter all class attributes starting/ending with and return a dict with their value"

    ret = {}
    for attr in dir(obj):

        # Skip unmatching names
        if prefix and not attr.startswith(prefix):
            # print ("IGNORE prefix", prefix, attr)
            continue
        if suffix and not attr.startswith(suffix):
            # print ("IGNORE sufix", suffix, attr)
            continue

        # Remove prefix and suffix
        name = attr
        if strip:
            if prefix:
                name = attr[len(prefix) :]
            if suffix:
                name = attr[: len(suffix)]

        # Remove extra end chars
        if rtrim:
            name = name.rstrip(rtrim)

        if name:

            if level_max:
                parts = name.split(level_split, level_max)

                target = ret
                for part in parts[:-1]:
                    if not part in target:
                        target[part] = {}
                    target = target[part]
                # print ("PROCESS part", prefix, attr, name)
                target[parts[-1]] = getattr(obj, attr)

            else:

                # print ("PROCESS flat", prefix, attr, name)
                # If value is None, then replace
                assert (
                    name not in ret
                ), f"Duplicate key: {attr}/{name} for object: {obj}"
                ret[name] = getattr(obj, attr)

    if None in ret:
        assert "BUG", ret

    return ret


# This is a class method
# @functools.cache
def node_class_builder(
    prefix,
    name=None,
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
    clsmethods = list(clsmethods or NODE_METHODS)
    bases = bases or []  # Example: (CaframNode, Fake)
    if not isinstance(bases, tuple):
        bases = tuple(bases)

    assert isinstance(bases, tuple), f"Got: {bases} (type={type(bases)})"

    class _NodeSkeleton(*bases):
        "Dynamic Node Class"

        if "__init__" in clsmethods:

            def __init__(self, *args, **kwargs):

                # print("RUN INIT", args, kwargs)

                ### NEW V2

                # 1. From inheritable attributes
                param_cls_prefix = _obj_filter_attrs_by(self, prefix=f"{prefix}_param_")
                mixin_cls_prefix = _obj_filter_attrs_by(
                    self, prefix=f"{prefix}_mixin__", level_max=1
                )
                mixin_cls_prefix = get_mixin_loading_order(mixin_cls_prefix)

                assert isinstance(mixin_cls_prefix, dict)
                mixin_cls_prefix = merge_keyed_dicts(
                    mixin_cls_prefix, param_cls_prefix.get("obj_mixins", {})
                )

                # 2. From decorator attributes
                param_cls_attrs = getattr(self, f"{prefix}_params__", {})
                mixin_cls_attrs = getattr(self, f"{prefix}_mixins__", {})
                mixin_cls_attrs = get_mixin_loading_order(mixin_cls_attrs)
                assert isinstance(mixin_cls_attrs, dict)
                # mixin_cls_attrs = merge_keyed_dicts(mixin_cls_attrs, param_cls_attrs.get("obj_mixins", {}))
                # V2: Make params obj_conf as default instead of override like in attrs
                mixin_cls_attrs = merge_keyed_dicts(
                    param_cls_attrs.get("obj_mixins", {}), mixin_cls_attrs
                )

                # 3. From kwargs
                param_kwargs = kwargs  # {key: val for key, val in kwargs.items() if key.startswith("obj_")}
                mixin_kwargs = kwargs.get("obj_mixins", None)
                mixin_kwargs = get_mixin_loading_order(mixin_kwargs)

                # 4. Build final configuration
                node_params2 = merge_dicts(
                    param_cls_prefix, param_cls_attrs, param_kwargs
                )
                mixin_conf2 = merge_keyed_dicts(
                    mixin_cls_prefix, mixin_cls_attrs, mixin_kwargs
                )
                node_params2["obj_mixins"] = mixin_conf2

                pprint([mixin_cls_prefix, mixin_cls_attrs, mixin_kwargs])

                tmp = NodeCtrl(
                    self,
                    obj_attr=prefix,
                    **node_params2,
                    # Contains:
                    #  obj_conf: {}
                    #  obj_attr: "__node__"
                    #  obj_prefix
                    #  obj_prefix_hooks
                    #  obj_prefix_class_params
                    #  obj_prefix
                )
                setattr(self, prefix, tmp)

                # Ensure __post__init__
                if hasattr(self, "__post_init__"):
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

                msg = (
                    "Getitem is not available as there is no nodectrl yet,"
                    f"can't look for: {name}"
                )
                raise errors.CaframException(msg)

        if "__call__" in clsmethods:

            def __call__(self, *args):
                "Return node or mixin/alias"

                if hasattr(self, prefix):
                    count = len(args)
                    if count == 0:
                        return getattr(self, prefix).mixin_get(name)
                    if count == 1:
                        return getattr(self, prefix).mixin_get(args[0])

                    msg = "Only 1 argument is allowed"
                    raise errors.CaframException(msg)

                msg = "Call is not available as there is no nodectrl yet"
                raise errors.CaframException(msg)

        ########################

        @classmethod
        def node_inherit(cls, obj, name=None, bases=None, override=True, attrs=None):
            "Create a new class from any class and make the node as it's ancestors"

            # Assert obj is a class

            # print("CALLL node_inherit", cls, obj, name, attrs)

            dct = attrs or {}
            bases = list(bases or [])
            name = name or obj.__qualname__

            # Do not reinject class if already present
            # base_names = [cls.__name__ for cls in bases]
            # if not w_name in base_names:
            if cls not in bases:

                if name:
                    dct["__qualname__"] = name

                if override:
                    # Create a new class WrapperClass that inherit from defined class

                    # print("NODE OVERRIDE", name, cls.__qualname__, tuple(bases), dct)
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

                    # print("NODE INHERIT", name, cls.__module__, tuple(bases), dct)
                    bases.append(cls)

                    # Pros:
                    #   * Respect standard inheritance model
                    #   * All your attributes/methods apears on __dir__
                    #   * Not that magic
                    # Cons:
                    #   * Important methods  NOT protected

                return (name, tuple(bases), dct)
            return None

        # This should not be hardcoded !!!
        @classmethod
        def node_patch_params(cls, obj, override=True):
            "Patch a class to become a node"

            # Patch object if not patched
            # ------------------------
            if cls in obj.__mro__:
                print(f"Skipping Wrapping Node {obj} with {cls}")
                return obj

            # print(f"Wrapping Node {obj} with {cls} (Override={override})")

            node_attrs = getattr(_NodeSkeleton, f"{prefix}_attrs__")
            for method_name in node_attrs:

                if override is False:
                    if hasattr(obj, method_name):
                        tot = getattr(obj, method_name)
                        print("Skip method patch", method_name, tot)
                        continue

                try:
                    method = getattr(cls, method_name)
                except AttributeError:
                    method = getattr(_NodeSkeleton, method_name)

                setattr(obj, method_name, method)

            setattr(obj, f"{prefix}_attrs__", node_attrs)
            setattr(obj, f"{prefix}_prefix__", prefix)

            return obj

        @classmethod
        def node_patch_mixin(cls, obj, conf):
            "Add a mixin configuration to class"

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

            mixin_confs = getattr(obj, f"{prefix}_mixins__", {})
            # mixin_confs2 = getattr(obj, f"{prefix}_mixins2__", [])

            mixin_confs[mixin_key] = conf
            # mixin_confs2.append(conf)

            setattr(obj, f"{prefix}_mixins__", mixin_confs)
            # setattr(cls, f"{prefix}_mixins2__", mixin_confs2)

            return obj

            ########################

    clsmethods.extend(
        [
            prefix,
            "node_patch_params",
            "node_patch_mixin",
        ]
    )

    for key, val in attrs.items():

        setattr(_NodeSkeleton, key, val)
        clsmethods.append(key)

    # Prepare __node__ attribute
    setattr(_NodeSkeleton, prefix, None)
    setattr(_NodeSkeleton, f"{prefix}_prefix__", prefix)
    setattr(_NodeSkeleton, f"{prefix}_params__", {})
    setattr(_NodeSkeleton, f"{prefix}_attrs__", clsmethods)

    # Prepare Class
    if name:
        setattr(_NodeSkeleton, "__name__", name)  # useless
        setattr(_NodeSkeleton, "__qualname__", name)
    if module:
        setattr(_NodeSkeleton, "__module__", module)
    if doc:
        setattr(_NodeSkeleton, "__doc__", doc)

    return _NodeSkeleton


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
        ret = node_cls.node_inherit(
            mcs, bases=bases, attrs=dct, name=name, override=node_override
        )
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

        # print("PREFIX", prefix)

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

    def newNode(self, override=None, patch=True):  # , *args, **kwargs):
        """
        Transform a class to a NodeClass WITH LIVE PATCH

        Forward all kwargs to NodeCtrl()
        """

        # Decorator arguments
        base_cls = self._base_node_cls
        if not isinstance(override, bool):
            override = self._override

        def _decorate(cls):

            # print("==== DECORATOR CLS INFO", cls, patch)
            # print("== Type", type(cls))
            # print("== Name", cls.__name__)
            # print("== QUALNAME", cls.__qualname__)
            # print("== MODULE", cls.__module__)
            # print("== DICT", cls.__dict__)

            ret = cls
            if patch:
                ret = base_cls.node_patch_params(ret, override=override)
            else:
                ret = base_cls.node_inherit(
                    cls, name=cls.__qualname__, override=override
                )
                if ret:
                    name, bases, dct = ret
                ret = type(name, bases, dct)

            return ret

        return _decorate

    def addMixin(self, mixin, mixin_key=None, mixin_conf=None, **kwargs):
        "Add features/mixins to class"

        # Get mixin config
        mixin_conf = mixin_conf or kwargs

        # Validate data
        assert isinstance(mixin_conf, dict)
        # assert isinstance(mixin_key, str)

        mixin_def = dict(mixin_conf)
        mixin_def.update({"mixin": mixin})
        if mixin_key is not None:
            mixin_def.update({"mixin_key": mixin_key})

        base_cls = self._base_node_cls

        def _decorate(cls):

            cls = base_cls.node_patch_mixin(cls, mixin_def)

            return cls

        return _decorate
