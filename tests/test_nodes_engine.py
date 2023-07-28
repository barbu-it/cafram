from pprint import pprint

from cafram.nodes.engine import NodeDecorator, NodeFactory, NodeMetaclass

# wp = NodeFactory()
# node_class_builder =

# ===================================================
# Dynamic Class Creator
# ===================================================


def test_nodeclassbuilder__basic():
    "Test generation of basic wrapper class"

    _prefix = "__node__"
    wp = NodeFactory(_prefix)
    out_cls = wp.node_class_builder()  # , name=_name)

    assert getattr(out_cls, f"__node_prefix__") == _prefix
    assert getattr(out_cls, f"{_prefix}") is None


def test_nodeclassbuilder__named():
    "Test generation of basic wrapper class with custom name and module"

    _prefix = "__node__"
    _name = "MyWrapper"
    _module = "MyModule"

    wp = NodeFactory(_prefix)
    out_cls = wp.node_class_builder(name=_name, module=_module)

    assert f"{_module}.{_name}" in str(out_cls)


def test_nodeclassbuilder__other_prefix():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__MYNODE__"

    wp = NodeFactory(_prefix)
    out_cls = wp.node_class_builder()

    assert getattr(out_cls, f"__node_prefix__") == _prefix
    assert getattr(out_cls, f"{_prefix}") is None


def test_nodeclassbuilder__extra_attr():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__node__"
    _attr = {
        "attr1": "value1",
        "fn1": lambda x: f"It works with function: {x}",
    }

    wp = NodeFactory(_prefix)
    out_cls = wp.node_class_builder(attrs=_attr)

    assert out_cls.attr1 == "value1"
    assert out_cls.fn1("YEPP") == "It works with function: YEPP"


def test_nodeclassbuilder__cls_methods():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__node__"
    _attr = {
        "attr1": "value1",
        "fn1": lambda x: f"It works with function: {x}",
    }

    wp = NodeFactory(_prefix)
    out_cls = wp.node_class_builder(clsmethods=[])

    # No class methods
    # out_cls = node_class_builder(_prefix, clsmethods=[])
    pprint(out_cls.__dict__)
    assert "__init__" not in out_cls.__dict__
    assert "__getattr__" not in out_cls.__dict__
    assert "__getitem__" not in out_cls.__dict__
    assert "__call__" not in out_cls.__dict__

    # Few class methods
    # out_cls = node_class_builder(_prefix, clsmethods=["__call__", "__getitem__"])
    out_cls = wp.node_class_builder(clsmethods=["__call__", "__getitem__"])
    assert "__init__" not in out_cls.__dict__
    assert "__getattr__" not in out_cls.__dict__
    assert hasattr(out_cls, "__getitem__")
    assert hasattr(out_cls, "__call__")


def test_nodeclassbuilder___node_inherit():
    "TODO"


def test_nodeclassbuilder___node_patch_params():
    "TODO"


def test_nodeclassbuilder___node_patch_mixin():
    "TODO"


# ===================================================
# Node MetaClass
# ===================================================


def test_metaclass__with_class():
    "Test good functionning with metaclass classic class key"

    class DynCls(
        metaclass=NodeMetaclass,
        node_prefix="__node__",
        node_override=False,
        node_name="Node",
    ):
        "My DocString"
        ATTR1 = True

    # DynCls = Node

    # mname = Node.__module__ # Depends on this file, ie: "tests.test_v1"
    # mname = __name__  # Depends on this file, ie: "tests.test_v1"

    mnameSHORT = f"test_metaclass__with_class.<locals>"
    mname = f"{__name__}.{mnameSHORT}"
    mnameFULL = f"{mname}.DynCls"

    print("obj", DynCls)
    print("TYPE", type(DynCls))
    print("Dict", DynCls.__dict__)
    print("MNANME", mname)

    assert str(DynCls) == f"<class '{mnameFULL}'>"
    assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    assert DynCls.__init__
    assert DynCls.__name__ == "DynCls"
    assert DynCls.__qualname__ == f"{mnameSHORT}.DynCls"
    assert DynCls.__module__ == __name__


def test_metaclass__with_class_inheritance_onchildren():
    "Test good functionning with metaclass and inheritance on children"

    # assert False, "TODO !"

    class Parent:
        "Parent Class"

    class DynCls(
        Parent,
        metaclass=NodeMetaclass,
        node_prefix="__node__",
        node_override=False,
        node_name="Node",
    ):
        "My DocString"
        ATTR1 = True

    mnameSHORT = f"test_metaclass__with_class_inheritance_onchildren.<locals>"
    mname = f"{__name__}.{mnameSHORT}"
    mnameFULL = f"{mname}.DynCls"

    # mname = __name__  # Depends on this file, ie: "tests.test_v1"
    print("obj", DynCls)
    print("TYPE", type(DynCls))
    print("Dict", DynCls.__dict__)
    print("MNANME", mname)

    assert str(DynCls) == f"<class '{mnameFULL}'>"
    assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    assert DynCls.__init__
    assert DynCls.__name__ == "DynCls"
    assert DynCls.__qualname__ == f"{mnameSHORT}.DynCls"
    assert DynCls.__module__ == __name__


def test_metaclass__with_class_inheritance_on_parent():
    "Test good functionning with metaclass and inheritance on parent"

    # assert False, "TODO !"

    class ParentNode(
        metaclass=NodeMetaclass,
        node_prefix="__node__",
        node_override=False,
        node_name="Node",
    ):
        "ParentNode Class"

        toto__module__ = __name__

    class DynCls(ParentNode):
        "My DocString"
        ATTR1 = True

    # mname = __name__  # Depends on this file, ie: "tests.test_v1"
    mnameSHORT = f"test_metaclass__with_class_inheritance_on_parent.<locals>"
    mname = f"{__name__}.{mnameSHORT}"
    mnameFULL = f"{mname}.DynCls"

    print("obj", DynCls)
    print("TYPE", type(DynCls))
    print("Dict", DynCls.__dict__)
    print("MNANME", mname)

    assert str(DynCls) == f"<class '{mnameFULL}'>"
    assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    assert DynCls.__init__
    assert DynCls.__name__ == "DynCls"
    assert DynCls.__qualname__ == f"{mnameSHORT}.DynCls"
    assert DynCls.__module__ == __name__
