from pprint import pprint

from cafram.nodes import Node, node_wrapper
from cafram.nodes.engine import NodeDecorator, NodeMetaclass

# ===================================================
# Node Instanciation
# ===================================================


def test_metaclass_simple():
    "Test node creation with metaclass"

    class Node1(metaclass=NodeMetaclass):
        "Default Cafram Node"

        custom_attr = "MyAttr"

        def custom_method(self):
            print("Hey", self)

    # Equivalent as above !!!
    Node2 = NodeMetaclass(
        "Node2",
        (),
        {
            "__module__": __name__,
            "__doc__": "Default Cafram Node",
            "custom_attr": "MyAttr",
            "custom_method": lambda self: print("Hey", self),
        },
    )

    # Checks
    assert dir(Node1) == dir(Node2)
    assert Node1.custom_attr == Node2.custom_attr


def test_metaclass_simple_inheritance():
    "Test node creation with metaclass inheritance"

    class BaseCls:
        def base_method(self):
            print("Hey", self)

    class Node1(BaseCls, metaclass=NodeMetaclass):
        "Default Cafram Node"

        custom_attr = "MyAttr"

        def custom_method(self):
            print("Hey", self)

    # Equivalent as above !!!
    Node2 = NodeMetaclass(
        "Node2",
        (BaseCls,),
        {
            "__module__": __name__,
            "__doc__": "Default Cafram Node",
            "custom_attr": "MyAttr",
            "custom_method": lambda self: print("Hey", self),
        },
    )

    # Checks
    assert dir(Node1) == dir(Node2)
    assert Node1.custom_attr == Node2.custom_attr
    assert Node1.custom_method != Node2.custom_method
    assert Node1.base_method == Node2.base_method

    assert Node1.__mro__[1:] == Node2.__mro__[1:]


def test_metaclass_prefix():
    "Test node creation with metaclass inheritance"

    class BaseCls:
        def base_method(self):
            print("Hey", self)

    class Node1(
        BaseCls, metaclass=NodeMetaclass, node_prefix="__NODE__", node_root=True
    ):
        "Default Cafram Node"

        custom_attr = "MyAttr"

        def custom_method(self):
            print("Hey", self)

    # Equivalent as above !!!
    Node2 = NodeMetaclass(
        "Node2",
        (BaseCls,),
        {
            "__module__": __name__,
            "__doc__": "Default Cafram Node",
            "custom_attr": "MyAttr",
            "custom_method": lambda self: print("Hey", self),
        },
        node_prefix="__NODE__",
    )

    # Checks
    assert dir(Node1) == dir(Node2)
    assert Node1.custom_attr == Node2.custom_attr
    assert Node1.custom_method != Node2.custom_method
    assert Node1.base_method == Node2.base_method

    # pprint (Node1.__dict__)
    assert Node1.__NODE__ == Node2.__NODE__
    assert Node1.__NODE__ is None
    assert Node2.__NODE__ is None

    assert not hasattr(Node1, "__node__")
    assert not hasattr(Node2, "__node__")

    # assert False


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
    node = NodeDecorator(
        # prefix="__node__",
        node_cls=Node,
        override=False,
        # name="Node2",
        # attrs=node_attrs,
    )

    class Normal:
        "Normal Class"

        ATTR = True

        def method_normal(self):
            "Yooo"

    @node.new_node()
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

    pprint(node.__dict__)

    # print(node._base_node_cls.__node___attrs__)
    # print(node._base_node_cls.__node___prefix__)
    print(Parent.__node_attrs__)
    print(Parent.__node_prefix__)
    print(Child1.__node_attrs__)
    print(Child1.__node_prefix__)

    pprint(dir(Parent))
    assert "__getitem__" in dir(Parent)
    assert "__getitem__" in dir(Child1)

    # assert "magic" in dir(Parent)
    # assert "magic" in dir(Child1)
