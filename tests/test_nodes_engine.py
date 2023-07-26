from pprint import pprint

from cafram.nodes.engine import NodeMetaclass, NodeWrapper, node_class_builder

# ===================================================
# Dynamic Class Creator
# ===================================================


def test_nodeclassbuilder__basic():
    "Test generation of basic wrapper class"

    _prefix = "__node__"
    out_cls = node_class_builder(_prefix)  # , name=_name)

    assert getattr(out_cls, f"{_prefix}_prefix__") == _prefix
    assert getattr(out_cls, f"{_prefix}") is None


def test_nodeclassbuilder__named():
    "Test generation of basic wrapper class with custom name and module"

    _prefix = "__node__"
    _name = "MyWrapper"
    _module = "MyModule"

    out_cls = node_class_builder(_prefix, name=_name, module=_module)

    assert f"{_module}.{_name}" in str(out_cls)


def test_nodeclassbuilder__other_prefix():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__MYNODE__"

    out_cls = node_class_builder(_prefix)
    assert getattr(out_cls, f"{_prefix}_prefix__") == _prefix
    assert getattr(out_cls, f"{_prefix}") is None


def test_nodeclassbuilder__extra_attr():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__node__"
    _attr = {
        "attr1": "value1",
        "fn1": lambda x: f"It works with function: {x}",
    }

    out_cls = node_class_builder(_prefix, attrs=_attr)

    assert out_cls.attr1 == "value1"
    assert out_cls.fn1("YEPP") == "It works with function: YEPP"


def test_nodeclassbuilder__bases():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__node__"
    _attr = {
        "attr1": "value1",
        "fn1": lambda x: f"It works with function: {x}",
    }

    class Base1:
        "My Base1"

    class Base2:
        "My Base2"

    out_cls = node_class_builder(_prefix, bases=[Base1, Base2])
    for base in out_cls.__mro__:
        assert base in out_cls.__mro__, f"Missing class {base} in mro"


def test_nodeclassbuilder__cls_methods():
    "Test generation of basic wrapper class with another prefix"

    _prefix = "__node__"
    _attr = {
        "attr1": "value1",
        "fn1": lambda x: f"It works with function: {x}",
    }

    out_cls = node_class_builder(_prefix)

    # No class methods
    out_cls = node_class_builder(_prefix, clsmethods=[])
    pprint(out_cls.__dict__)
    assert "__init__" not in out_cls.__dict__
    assert "__getattr__" not in out_cls.__dict__
    assert "__getitem__" not in out_cls.__dict__
    assert "__call__" not in out_cls.__dict__

    # Few class methods
    out_cls = node_class_builder(_prefix, clsmethods=["__call__", "__getitem__"])
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
    mname = __name__  # Depends on this file, ie: "tests.test_v1"
    print("obj", DynCls)
    print("TYPE", type(DynCls))
    print("Dict", DynCls.__dict__)
    print("MNANME", mname)

    assert str(DynCls) == f"<class '{mname}.Node'>"
    assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    assert DynCls.__init__
    assert DynCls.__name__ == "Node"
    assert DynCls.__qualname__ == "Node"
    assert DynCls.__module__ == mname


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

    mname = __name__  # Depends on this file, ie: "tests.test_v1"
    print("obj", DynCls)
    print("TYPE", type(DynCls))
    print("Dict", DynCls.__dict__)
    print("MNANME", mname)

    assert str(DynCls) == f"<class '{mname}.Node'>"
    assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    assert DynCls.__init__
    assert DynCls.__name__ == "Node"
    assert DynCls.__qualname__ == "Node"
    assert DynCls.__module__ == mname


def test_metaclass__with_class_inheritance_on_parent():
    "Test good functionning with metaclass and inheritance on parent"

    # assert False, "TODO !"

    class Parent(
        metaclass=NodeMetaclass,
        node_prefix="__node__",
        node_override=False,
        node_name="Node",
    ):
        "Parent Class"

    class Node(Parent):
        "My DocString"
        ATTR1 = True

    DynCls = Node
    mname = __name__  # Depends on this file, ie: "tests.test_v1"
    print("obj", DynCls)
    print("TYPE", type(DynCls))
    print("Dict", DynCls.__dict__)
    print("MNANME", mname)

    assert str(DynCls) == f"<class '{mname}.Node'>"
    assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    assert DynCls.__init__
    assert DynCls.__name__ == "Node"
    print("TYOOO", DynCls.__qualname__)
    assert DynCls.__qualname__ == f"Node"
    assert DynCls.__module__ == __name__


# ===================================================
# Node MetaClass
# ===================================================


def test_clsbuilder_decorator_base():
    "Test node creation with decorators"

    def tutu(self, *args):
        print("YO TUTUT", args)

    node_attrs = {
        "magic": tutu,
    }

    print("===" * 20)
    node = NodeWrapper(
        prefix="__node__",
        override=False,
        name="Node2",
        attrs=node_attrs,
    )

    class Normal:
        "Normal Class"

        ATTR = True

        def method_normal(self):
            "Yooo"

    @node.newNode()
    class Parent:
        "Parent Class"

        ATTR2 = True

        def method_parent(self):
            "Yooo"

    # @node.newNode()    # Not required because of Parent which is a node
    class Child1(Parent):
        "My DocString"
        ATTR1 = True

        def method_child(self):
            "Yooo"

    norm = Normal()
    app = Parent()
    child1 = Child1()

    pprint(norm)
    pprint(app)
    pprint(child1)

    pprint(norm.__dict__)
    pprint(app.__dict__)
    pprint(child1.__dict__)

    pprint(Normal.__dict__)
    pprint(Parent.__dict__)
    pprint(Child1.__dict__)

    print(node._base_node_cls.__node___attrs__)
    print(node._base_node_cls.__node___prefix__)
    print(Parent.__node___attrs__)
    print(Parent.__node___prefix__)
    print(Child1.__node___attrs__)
    print(Child1.__node___prefix__)

    assert "__getitem__" in dir(Parent)
    assert "__getitem__" in dir(Child1)

    assert "magic" in dir(Parent)
    assert "magic" in dir(Child1)
