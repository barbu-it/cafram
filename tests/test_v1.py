#!/usr/bin/env pytest
# -*- coding: utf-8 -*-


import os
from pprint import pprint  # noqa: F401
import logging

import pytest
import traceback
import logging
from pprint import pprint
import pytest


import cafram.errors as errors

from cafram.mixins import BaseMixin
from cafram.mixins.base import LoggerMixin, MapAttrMixin

# from cafram.mixins.tree import PayloadMixin, DictConfMixin, ListConfMixin, SimpleConfMixin #, HierMixin


# from cafram.mixins.tree import  _ContainerMixin

from cafram.nodes3 import Node
from cafram.mixins.base import PayloadMixin
from cafram.mixins.hier import HierMixin, HierParentMixin, HierChildrenMixin
from cafram.mixins.tree import NodePayload, NodeConf, NodeConfDict, NodeConfList
from cafram.mixins.tree import ConfMixin, ConfDictMixin, ConfListMixin


# from cafram.decorators import newNode, addMixin

# ConfigLoader
# ------------------------


from cafram.tools import NodeConfigLoader, MixinConfigLoader
from cafram.mixins import BaseMixin
#from cafram.ctrl2 import NodeCtrl
from cafram.nodes.ctrl import NodeCtrl
#from cafram.nodes2 import Node as OldNode
import inspect


# ===================================================
# Dynamic Class Creator
# ===================================================

#from cafram.nodes3 import node_class_builder, NodeMetaclass, NodeWrapper

from cafram.nodes.engine import node_class_builder, NodeMetaclass, NodeWrapper




def test_clsbuilder_func_basic():
    "Test good functionning of dynamic class builder function"

    Class1 = node_class_builder(
        "__node__",
        name="Class1",
        module=__name__,
    )

    assert inspect.isclass(Class1)
    assert str(Class1) == f"<class '{__name__}.Class1'>"
    assert str(type(Class1)) == "<class 'type'>"
    assert type(Class1) == type

    assert Class1.__init__
    assert Class1.__name__ == "Class1"
    assert Class1.__qualname__ == "Class1"
    assert Class1.__module__ == __name__

    # pprint (Class1.__dict__)
    # print (Class1.__name__)
    # print (Class1.__qualname__)
    # print ("MOD ", Class1.__module__)
    # print (str(Class1))
    # print (str(type(Class1)))
    # assert False


def test_clsbuilder_func_with_bases():
    "Test good functionning with parents classes"

    Class1 = node_class_builder(
        "__node__", name="Class1", module=__name__, bases=[]  # TOFIX
    )

    "Test good functionning with metaclass direct metaclass"

    # Node2 = NodeMetaclass("Node", (), {"ATTR1":True, "__doc__":"Custom doc"},
    #     node_bases=[CaframNode], node_override=True, node_doc="Custom doc")

    # DynCls = node_class_builder("__node__", name="Node",
    #     doc="My DocString", bases=[CaframNode])

    DynCls = NodeMetaclass(
        "Node",
        (),
        {"ATTR1": True, "__doc__": "My DocString"},
        node_override=True,
        node_prefix="__node__",
    )
    # ,
    # node_bases=[CaframNode])

    mname = DynCls.__module__  # Depends on this file, ie: "tests.test_v1"
    pprint(DynCls)
    pprint(type(DynCls))
    pprint(DynCls.__dict__)

    assert str(DynCls) == f"<class '{mname}.Node'>"
    assert str(type(DynCls)) == f"<class '{mname}.NodeMetaclass'>"
    # assert False

    assert DynCls.__init__
    assert DynCls.__name__ == "Node"
    assert DynCls.__qualname__ == "Node"
    assert DynCls.__module__ == mname


def test_clsbuilder_metaclass_with_class():
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


# assert False


def test_clsbuilder_metaclass_with_class_inheritance_onchildren():
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


def test_clsbuilder_metaclass_with_class_inheritance_on_parent():
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

    # print ("NEWWW")
    # pprint (node._base_node_cls.tmp__patch__)
    # pprint (app)
    # pprint (app.__class__.__mro__)
    # pprint (app.__dict__)
    # pprint (app.tmp__patch__)

    # assert False, "WIPPP OKKKKK"

    # @node.newNode()
    # @node.addMixin()
    # class Node(Parent):
    #     "My DocString"
    #     ATTR1 = True

    # DynCls = Node
    # mname = __name__ # Depends on this file, ie: "tests.test_v1"
    # prefix = "test_clsbuilder_metaclass_with_class_inheritance_on_parent.<locals>"
    # mname = f"{__name__}.{prefix}"
    # print ("obj", DynCls)
    # print ("TYPE", type(DynCls))
    # print ("Dict", DynCls.__dict__)
    # print ("MNANME", mname)

    # assert str(DynCls) == f"<class '{mname}.Node'>"
    # assert str(type(DynCls)) == f"<class 'cafram.nodes.engine.NodeMetaclass'>"

    # assert DynCls.__init__
    # assert DynCls.__name__ == "Node"
    # print ("TYOOO", DynCls.__qualname__)
    # assert DynCls.__qualname__ == f"{prefix}.Node"
    # assert DynCls.__module__ == __name__


# ===================================================
# Config Loaders test
# ===================================================

# Ensure config loader correctely read their parameters

# WIPPP MIGRATION TO v2
# from cafram.nodes2 import Node
from cafram.nodes3 import Node


def test_configloader_nodectrl():
    "Test good functionning of NodeConfigLoader"

    class NodeCls(Node):

        # Config load order, last wins:
        # - generic class attribute
        # - decorator config
        # - __init__ config

        # Node: Config via class (inherited) attributes
        # ----------------------------------------
        # Note:
        #   - Support Native Python inheritance
        # Usage:
        #   _node__<KEY> = <VALUE>                      : Configure NodeCtrl
        #   _node_mixin__<MIXIN>__<KEY> = <VALUE>       : Configure Mixin Configuration

        _node__KEY1 = True
        _node__KEY2 = True
        _node__KEY3 = True

        _node_mixin__mixin1__mixin_enabled = False
        _node_mixin__mixin1__aconf = "VALUE"

        _node_mixin__mixin9__mixin_enabled = False
        _node_mixin__mixin9__aconf = "VALUE"

        # Node: Config via decorator attrs
        # ----------------------------------------
        # Note:
        #   - Support Native Python inheritance (ONLY when inherit=True)
        # Usage:
        #   @newNode()
        #   @addMixin("MIXIN_CLS" [, "MIXIN_KEY"] [, **mixin_conf])
        # Note:
        #  When you use decorators, it works with 2 class attributes: __node_params__ and __node_mixins__
        #  If you enable inheritance, then all attributes are added to class (see above)

        __node_params__ = {"KEY1": "OVERRIDED by Decorator"}
        __node_mixins__ = {
            "mixin1": {
                "mixin_key": "NEWKEY",
            },
            "mixin2": {
                "mixin_key": "NEWKEY",
            },
            "mixin8": {
                "mixin_key": "NEWKEY",
            },
        }

    # Node: Config via mixin_conf from __init__()
    # ----------------------------------------
    # Note:
    #   - Does NOT Support Native Python inheritance
    #   - Recommended for generic live object, such as nested children
    # Usage:
    #   mixin = MixinClass(mixin_conf={})

    mixin_conf = {
        "mixin1": {
            "mixin_enabled": True,
        },
        "mixin2": {
            "mixin_enabled": True,
            "mixin_key": "NEWKEY2",
        },
        "mixin3": {
            "mixin_enabled": True,
        },
        "mixin7": {
            "mixin_enabled": True,
        },
    }

    # Direct __init__ param override
    kwargs = {
        "KEY2": "OVERRIDEDN BY KWARGS",
        "obj_attr": "__node__",
    }

    tobj1 = NodeCls()

    # Live patch for stict mode, as example are pretty bad
    STRICT = True
    if STRICT:
        setattr(tobj1.__node__, "KEY1", "test_only")
        setattr(tobj1.__node__, "KEY2", "test_only")
        setattr(tobj1.__node__, "KEY3", "test_only")
        setattr(tobj1.__node__, "obj_attr", "test_only")
        setattr(tobj1.__node__, "obj_conf", "test_only")

    # Generate the loader object
    tloader = NodeConfigLoader(tobj1.__node__, obj_src=tobj1)
    mixin_conf = tloader.build(kwargs_mixins=mixin_conf, kwargs=kwargs, strict=STRICT)

    # DEbug
    print("DEBUG")
    pprint(tobj1.__dict__)
    pprint(tobj1.__node__.__dict__)
    pprint(mixin_conf)
    print("EOOOFFF")

    # Test nodectrl configuration
    assert tobj1.__node__.KEY1 == "OVERRIDED by Decorator"
    assert tobj1.__node__.KEY2 == "OVERRIDEDN BY KWARGS"
    assert tobj1.__node__.KEY3 == True

    # Test mixin configuration
    assert mixin_conf == {
        "KEY1": "OVERRIDED by Decorator",
        "KEY2": "OVERRIDEDN BY KWARGS",
        "KEY3": True,
        "obj_attr": "__node__",
        "obj_conf": {
            "mixin1": {"aconf": "VALUE", "mixin_enabled": True, "mixin_key": "NEWKEY"},
            "mixin2": {"mixin_enabled": True, "mixin_key": "NEWKEY2"},
            "mixin3": {"mixin_enabled": True},
            "mixin7": {"mixin_enabled": True},
            "mixin8": {"mixin_key": "NEWKEY"},
            "mixin9": {"aconf": "VALUE", "mixin_enabled": False},
        },
    }


def test_configloader_mixins():
    "Test good functionning of MixinConfigLoader"

    # Mock mixin
    class MixinCls(BaseMixin):
        mixin_enabled = True
        mixin_cls = None
        mixin_key = "MyKey"
        mixin_param__ATTR1 = "attr1"  # Declare param and remap
        mixin_param__ATTR2 = "attr2"  # Declare param and remap
        mixin_param__ATTR3 = None  # Declare param only, no change
        mixin_alias__ALIAS1 = "alias1"
        mixin_alias__ALIAS2 = "alias2"
        mixin_alias__ALIAS3 = "alias3"

        # When STRICT=True
        # Example User Attributes, must be declared into class
        ATTR1 = "default"
        ATTR2 = "default"
        ATTR3 = "default"

        BUILT_CONFIG = None

    # Must always reference existing mixin attributes, sent in __init__ mixin_conf
    mixin_conf = {
        "mixin_enabled": False,
        "mixin_key": "MyKey",
        # "mixin_key_FAIL": "MyKey",
        # Conf override
        "mixin_param__ATTR2": "attr2_new",  # Change remap for ATTR2
        "mixin_alias__ALIAS2": "alias2_new",
    }

    # Allow new param creation/remap, sent via __init__ kwargs
    runtime_params = {
        "attr1": "INIT override value1",
        "attr2_new": "INIT override value2_new",
        "ATTR3": "user default param",
        # "alias1": "INIT alias1",
        # "alias2_new": "INIT alias2_new",
    }

    # # Test load
    tobj1 = Node()
    tobj2 = MixinCls(tobj1.__node__)
    tloader = MixinConfigLoader(tobj2)

    # aliases = tloader.build(mixin_conf=mixin_conf, kwargs=runtime_params, strict=False)
    aliases = tloader.build(mixin_conf=mixin_conf, kwargs=runtime_params, strict=True)

    pprint(tobj2.__dict__)

    # Check dynconf
    assert tobj2.mixin_enabled == False
    assert tobj2.mixin_key == "MyKey"

    # Check __init__ param overrides
    assert tobj2.ATTR1 == "INIT override value1"
    assert tobj2.ATTR2 == "INIT override value2_new"
    assert tobj2.ATTR3 == "user default param"

    pprint(aliases)

    # assert aliases == {'ALIAS1': 'alias1', 'ALIAS2': 'alias2_new', 'ALIAS3': 'alias3'}

    # assert False, "WIPP"
