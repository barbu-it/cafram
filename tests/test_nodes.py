
from pprint import pprint

from cafram.nodes.engine import NodeMetaclass, NodeDecorator, node_class_builder

from cafram.nodes import Node, node_wrapper


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
        node_cls = Node,
        override=False,
        # name="Node2",
        #attrs=node_attrs,
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

    pprint (node.__dict__)


    # print(node._base_node_cls.__node___attrs__)
    # print(node._base_node_cls.__node___prefix__)
    print(Parent.__node___attrs__)
    print(Parent.__node___prefix__)
    print(Child1.__node___attrs__)
    print(Child1.__node___prefix__)

    pprint (dir(Parent))
    assert "__getitem__" in dir(Parent)
    assert "__getitem__" in dir(Child1)

    # assert "magic" in dir(Parent)
    # assert "magic" in dir(Child1)
