

from pprint import pprint
import inspect

from ..lib.utils import import_module
from cafram.nodes.ctrl import NodeCtrl
import cafram.errors as errors



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
    prefix, name=None, bases=None, clsmethods=None, module=None, doc=None, attrs=None
):
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
    bases = bases or tuple([])  # Example: (CaframNode, Fake)
    if not isinstance(bases, tuple):
        bases = tuple(bases)

    assert isinstance(bases, tuple), f"Got: {bases} (type={type(bases)})"
    print(
        f"Build new _NodeSkeleton: name={name}, prefix='{prefix}', bases={bases}, methods:",
        clsmethods,
    )

    class _NodeSkeleton(*bases):
        "Dynamic Node Class"

        # def DYN_NODE_ALWAYS(self):
        #     print("ALWAYS HERE !")

        # __node__params__ = {}
        # __node__params__ = {}
        # __node__mixins__ = {}

        # __node__attrs__ =  clsmethods
        # __node__prefix__ =  prefix

        @classmethod
        def tmp__inherit(cls, obj, name=None, bases=None, override=True, attrs=None):
            "Create a new class from any class and make the node as it's ancestors"

            # Assert obj is a class

            # print("CALLL tmp__inherit", cls, obj, name, attrs)

            ret = cls
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

                    print("NODE OVERRIDE", name, cls.__qualname__, tuple(bases), dct)
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

                    print("NODE INHERIT", name, cls.__module__, tuple(bases), dct)
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
        def tmp__patch__(cls, obj, override=True):
            "Patch a class to become a node"

            # Build parameters
            # ------------------------
            # Build NodeCtrl Config
            nodectrl_conf = getattr(obj, f"{prefix}_params__", {})
            mixin_confs = getattr(obj, f"{prefix}_mixins__", {})

            # mixin_confs2 = getattr(obj, f"{prefix}_mixins2__", [])
            nodectrl_conf["obj_mixins"] = mixin_confs
            setattr(obj, f"{prefix}_params__", nodectrl_conf)
            print("SET ATTR", obj, f"{prefix}_params__", nodectrl_conf)

            # Patch object if not patched
            # ------------------------
            if cls in obj.__mro__:
                print(f"Skipping Wrapping Node {obj} with {cls}")
                return obj

            print(f"Wrapping Node {obj} with {cls} (Override={override})")

            node_attrs = getattr(_NodeSkeleton, f"{prefix}_attrs__")
            for method_name in node_attrs:

                if override is False:
                    if hasattr(obj, method_name):
                        tot = getattr(obj, method_name)
                        print("Skip method patch", method_name, tot)
                        continue

                print("IMPORT METHOD", method_name)
                method = getattr(cls, method_name)
                setattr(obj, method_name, method)

            setattr(obj, f"{prefix}_attrs__", node_attrs)
            setattr(obj, f"{prefix}_prefix__", prefix)

            return obj

        ########################

        @classmethod
        def tmp__patch__mixin__(cls, obj, conf, key=None):

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
            mixin_confs2 = getattr(obj, f"{prefix}_mixins2__", [])

            mixin_confs[mixin_key] = conf
            mixin_confs2.append(conf)

            setattr(obj, f"{prefix}_mixins__", mixin_confs)
            # setattr(cls, f"{prefix}_mixins2__", mixin_confs2)

            return obj

        ########################

        if "__init__" in clsmethods:

            def __init__(self, *args, **kwargs):

                # print("RUN INIT", args, kwargs)

                __node__params__ = {}
                # __node__params__.update(self.__node__params__)
                __node__params__.update(getattr(self, f"{prefix}_params__", {}))
                __node__params__.update(kwargs)

                print("INIT NODECTRL WITH PARAMS", __node__params__)
                print(self, self.__class__)
                pprint(self.__dict__)
                pprint(self.__class__.__dict__)

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
                setattr(self, prefix, tmp)

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
                # if self.__node__:
                # return self.__node__.mixin_get(name)

                msg = f"Getitem is not available as there is no nodectrl yet, can't look for: {name}"
                raise errors.CaframException(msg)

        if "__call__" in clsmethods:

            def __call__(self, *args):
                "Return node or mixin/alias"

                if hasattr(self, prefix):
                    # if self.__node__:
                    count = len(args)
                    if count == 0:
                        # return self.__node__
                        return getattr(self, prefix).mixin_get(name)
                    if count == 1:
                        # return self.__node__.mixin_get(args[0])
                        return getattr(self, prefix).mixin_get(args[0])

                    msg = "Only 1 argument is allowed"
                    raise errors.CaframException(msg)

                msg = "Call is not available as there is no nodectrl yet"
                raise errors.CaframException(msg)

    clsmethods.extend(
        [
            prefix,
            # f"{prefix}_prefix__",
            # f"{prefix}_params__",
        ]
    )

    for key, val in attrs.items():
        setattr(_NodeSkeleton, key, val)
        # _NodeSkeleton.__node__attrs__.append(key)
        # getattr(_NodeSkeleton, f"{prefix}_attrs__").append(key)
        clsmethods.append(key)

    # Prepare __node__ attribute
    setattr(_NodeSkeleton, prefix, None)
    setattr(_NodeSkeleton, f"{prefix}_prefix__", prefix)
    setattr(_NodeSkeleton, f"{prefix}_params__", {})
    setattr(_NodeSkeleton, f"{prefix}_attrs__", clsmethods)
    # setattr(_NodeSkeleton, f"{prefix}_attrs__", list(_NodeSkeleton.__dict__.keys()))

    # Prepare Class
    if name:
        setattr(_NodeSkeleton, "__name__", name)  # useless
        setattr(_NodeSkeleton, "__qualname__", name)
    if module:
        setattr(_NodeSkeleton, "__module__", module)
    if doc:
        setattr(_NodeSkeleton, "__doc__", doc)

    # setattr(_NodeSkeleton, "__metaclass__", NodeMetaclass)
    # print ("TOFIX METADATA INHERITANCE")

    return _NodeSkeleton


# Node Metaclass
################################################################


NODE_PREFIX = "__node__"


class NodeMetaclass(type):
    """NodeMetaClass"""

    node_prefix = "__node__"

    def __new__(
        cls,
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
        node_prefix = node_prefix or cls.node_prefix
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
        ret = node_cls.tmp__inherit(cls, bases=bases, attrs=dct, name=name)
        if ret:
            name, bases, dct = ret

        # Return a new class
        return super().__new__(cls, name, bases, dct)

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

    #     # Minimal placeholder
    #     # cls = super().__new__(metacls, name, bases, namespace, **kwargs)
    #     # # You must return the generated class
    #     # return cls


# Decorators
################################################################


class NodeWrapper:

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

    def newNode(self, override=None, patch=True, **kwargs):  # , *args, **kwargs):
        """
        Transform a class to a NodeClass WITH LIVE PATCH

        Forward all kwargs to NodeCtrl()
        """

        # Decorator arguments
        base_cls = self._base_node_cls
        if not isinstance(override, bool):
            override = self._override

        def _decorate(cls):

            # print("==== DECORATOR CLS INFO", cls)
            # print("== Type", type(cls))
            # print("== Name", cls.__name__)
            # print("== QUALNAME", cls.__qualname__)
            # print("== MODULE", cls.__module__)
            # print("== DICT", cls.__dict__)

            ret = cls
            if patch:
                ret = base_cls.tmp__patch__(ret, override=override)
            else:
                ret = base_cls.tmp__inherit(
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

            cls = base_cls.tmp__patch__mixin__(cls, mixin_def)

            return cls

        return _decorate


