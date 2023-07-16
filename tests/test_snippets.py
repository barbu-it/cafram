#!/usr/bin/env pytest
# -*- coding: utf-8 -*-


import logging
import os
import traceback
from pprint import pprint  # noqa: F401

import pytest

import cafram.errors as errors
from cafram.nodes import Node, NodeWrapper, addMixin, newNode
from cafram.nodes.comp import BaseMixin
from cafram.nodes.comp.base import LoggerMixin, MapAttrMixin, PayloadMixin
from cafram.nodes.comp.hier import HierChildrenMixin, HierMixin, HierParentMixin
from cafram.nodes.comp.tree import (  # NodeConf,; NodeConfDict,; NodeConfList,; NodePayload,
    ConfDictMixin,
    ConfListMixin,
    ConfMixin,
)
from cafram.nodes.ctrl import NodeCtrl


def test_app1_post_init():
    "Test that show how to use __post_init__"

    # node = NodeWrapper(
    #     prefix="__node__",
    #     override=False,
    #     name="Node",
    # )

    # Sample Data
    # @node.newNode()
    @newNode()
    class MyApp:

        my_option = "DEFAULT"

        def __post_init__(self, *args, **kwargs):
            "Default __post_init__ class with no argument matching"
            print(f"I'm initing myself '{self}'")
            print(f"My args: {args}")
            print(f"My kwargs: {kwargs}")
            self.my_option = kwargs.get("my_option", "UNSET")

            self.TEST_INITED = True
            self.TEST_EXECUTED = False
            self.TEST_ARGS = args
            self.TEST_KWARGS = kwargs

        def demo(self):
            "Example method"
            print(f"I'm '{self}' and my attribute 'my_option' is: {self.my_option}")

            self.TEST_EXECUTED = True

    pprint(MyApp)

    # Test all different accesses
    app1 = MyApp()
    print("+++ DEBUG +++")
    pprint(app1.__class__.__mro__)
    pprint(MyApp.__dict__)
    pprint(app1)
    pprint(app1.__dict__)
    print("+++ DEBUG +++")

    assert app1.TEST_INITED is True
    assert app1.TEST_EXECUTED is False
    assert app1.my_option == "UNSET"
    app1.demo()

    app2 = MyApp(
        "first_param",
        "second_param",
        random_opt1=False,
        random_opt2=True,
        my_option="SUCCESS",
    )
    assert app2.TEST_INITED is True
    assert app2.TEST_EXECUTED is False
    assert app2.my_option == "SUCCESS"
    app2.demo()

    # Advanced tests

    assert app1.TEST_INITED is True
    assert app1.TEST_EXECUTED is True
    assert app1.TEST_ARGS == ()
    assert app1.TEST_KWARGS == {}

    assert app2.TEST_INITED is True
    assert app2.TEST_EXECUTED is True
    assert app2.TEST_ARGS == ("first_param", "second_param")
    assert app2.TEST_KWARGS == dict(
        random_opt1=False, random_opt2=True, my_option="SUCCESS"
    )


def test_app2_post_init_args():
    "Test that show how to use args and kwargs with __post_init__"

    # Sample Data
    @newNode()
    class MyApp:

        my_option = "DEFAULT"

        def __post_init__(self, my_arg, *args, my_option="UNSET", **kwargs):
            "Default __post_init__ class with params and options"

            print(f"I'm initing myself '{self}'")
            print(f"param: my_arg: {my_arg}")
            print(f"param: my_opt: {my_option}")
            print(f"My args: {args}")
            print(f"My kwargs: {kwargs}")

            self.my_option = my_option
            self.my_arg = my_arg

            self.TEST_INITED = True
            self.TEST_EXECUTED = False
            self.TEST_ARGS = args
            self.TEST_KWARGS = kwargs

        def demo(self):
            print(f"I'm '{self}' and my attribute 'my_option' is: {self.my_option}")

            self.TEST_EXECUTED = True

    # Test all different accesses
    app1 = MyApp("RUNTIME_PARAM", my_option="RUNTIME_SETTING", extra_param="unknown")
    assert app1.TEST_INITED is True
    assert app1.TEST_EXECUTED is False
    assert app1.my_arg == "RUNTIME_PARAM"
    assert app1.my_option == "RUNTIME_SETTING"
    assert app1.TEST_KWARGS == dict(extra_param="unknown")
    assert app1.TEST_ARGS == ()
    app1.demo()

    # Should throuh BadArguments exception if passed with no parameter
    try:
        app2 = MyApp()
    except errors.BadArguments as err:
        pass

    # On its shortest form
    app1 = MyApp("RUNTIME_PARAM")
    assert app1.TEST_INITED is True
    assert app1.TEST_EXECUTED is False
    assert app1.my_arg == "RUNTIME_PARAM"
    assert app1.my_option == "UNSET"
    assert app1.TEST_KWARGS == dict()
    assert app1.TEST_ARGS == ()
    app1.demo()


# ==============================================
# Possible Instanciation Tests
# ==============================================


class MyAppExample:

    TEST_ATTR = "DEFAULT"
    TEST_INIT_NEW = False
    TEST_POST_INIT_NEW = False

    def __init__(self, *args, my_opts=None, **kwargs):
        print("EXEC POST INIT")
        self.TEST_INIT_NEW = True

        super().__init__(*args, **kwargs)

    def __post_init__(self, *args, my_opts=None, **kwargs):
        print("EXEC POST INIT")
        self.TEST_POST_INIT_NEW = True
        self.TEST_ATTR = my_opts

    def demo(self):
        return "SUCCESS"


def test_integration1_deco_override():
    """Test that show how to use new node,

    some methods are protected such as __init__, __getattr__ and so ...

    """

    # Sample Data
    @newNode(
        override=True,
        # node_attr = "__node__",
    )
    class MyApp1(MyAppExample):
        "Simple placeholder"

    app1 = MyApp1()
    assert app1.demo() == "SUCCESS"

    pprint(app1.__dict__)
    pprint(dir(MyApp1))
    assert app1.TEST_INIT_NEW is False
    assert app1.TEST_POST_INIT_NEW is True


def test_integration1_deco_loose():
    "Test that show how to use loose inheritance, with override=false"

    # Sample Data
    @newNode(override=False)
    class MyApp1(MyAppExample):
        "Simple placeholder"

    app1 = MyApp1()
    assert app1.demo() == "SUCCESS"

    pprint(app1.__dict__)
    pprint(dir(MyApp1))
    assert app1.TEST_INIT_NEW is True
    assert app1.TEST_POST_INIT_NEW is False


def test_integration2_inheritance():
    """Test that show how to use without decorators

    But ther is no way to customize nodectrl instanciation
    """

    # Sample Data
    class MyApp1(Node, MyAppExample):
        "Simple placeholder"

    # Test all different accesses
    app1 = MyApp1()

    pprint(app1.__dict__)
    pprint(dir(MyApp1))
    assert app1.TEST_INIT_NEW is False
    assert app1.TEST_POST_INIT_NEW is True


def test_integration2_inheritance_configured():
    """Test that show how to use without decorators

    But ther is no way to customize nodectrl instanciation
    """

    # Sample Data
    class MyApp1(Node, MyAppExample):
        "Simple placeholder"

        # __node__ : Where the node lies, minimum !
        # _node__prefix = "__node__" : Where the node lies, minimum !

        # Inheritable node configuration
        _node__alias = True
        _node__debug = False
        _node__obj_config = {  # Local config, not inherited
            "conf": {
                "debug": True,
                "opt": 7894,
            }
        }

        # Or _node__obj_config can be expanded with. Inheritance works !
        _node_mixin__conf__config = {}
        _node_mixin__conf__children = "DictConf"
        _node_mixin__conf__debug = False
        _node_mixin__conf__opt = 1234

        # Then all of this is tranformed in: NodeCtrl params !

    # Example with mixin:
    # class MixinExample(BaseMixin):
    #     "Flat config for mixins ..."

    #     # BaseClass:
    #     mixin = cls # Mixin class to use , None to disable ...
    #     mixin_key = "my_mod"  # Mixin key to use, none if None
    #     mixin_aliases = bool # Enable alias creation
    #     mixin_logger_impersonate = None   # Show in target program logs (unhide)
    #     mixin_logger_level = None         # Mixin log level
    #     mixin_enabled = True          # Temporary enable/disable mixin

    #     # Other helpers
    #     mixin_param__<ATTR> = <name_in_params>
    #     mixin_alias__<ATTR> = <alias_name>

    #     <ATTR> = # Parametrizable attribute via config (via mixin_conf)
    #     _<ATTR> = # Internal attributes

    # Test all different accesses
    app1 = MyApp1()

    pprint(app1.__dict__)
    pprint(dir(MyApp1))
    assert app1.TEST_INIT_NEW is False
    assert app1.TEST_POST_INIT_NEW is True


# ==============================================
# Decorators Tests
# ==============================================


class MyAppDeco:

    my_option = "DEFAULT"

    def __post_init__(self, *args, **kwargs):
        print("EXEC POST INIT")
        self.TEST_INIT_NEW = True

    def demo(self):
        return "SUCCESS"


def test_deco1_override_true():
    "Test that show how to use override (enabled by default)"

    # Sample Data
    @newNode(override=True)
    class MyApp(MyAppDeco):
        "Simple placeholder"

        def __init__(self):
            print("EXEC REGULAR INIT, NEVER CALLED HERE")
            self.TEST_INIT_REGULAR = True

            # Required in this case to call Node __init__
            super().__init__()
            # If not called, Node Object can't be initialized

    # Test all different accesses
    app1 = MyApp()
    assert app1.TEST_INIT_NEW is True
    assert app1.demo() == "SUCCESS"

    # Ensure __init__ method never executed
    assert not hasattr(app1, "TEST_INIT_REGULAR")


def test_deco2_override_false():
    "Test that shows when override is disabled"

    # Sample Data
    @newNode(override=False)
    class MyApp(MyAppDeco):
        "Simple placeholder"

        custom_attr = True

        def __init__(self):
            print("EXEC REGULAR INIT")
            self.TEST_INIT_REGULAR = True

            # Required in this case to call Node __init__
            super().__init__()
            # If not called, Node Object can't be initialized

    # Test all different accesses
    app1 = MyApp()
    # pprint (MyApp.__dict__)
    # pprint (MyApp.__mro__)
    # pprint (app1.__dict__)
    # print ("YOOO ",app1.TEST_INIT_REGULAR)

    assert app1.TEST_INIT_REGULAR is True
    assert app1.demo() == "SUCCESS"

    pprint(app1.__dict__)

    # Ensure __init__ method never executed
    assert not hasattr(app1, "TEST_INIT_NEW")


def test_deco3_override_bad():
    "Test that shows when override is disabled and init not inherited"

    # Sample Data
    @newNode(override=False)
    class MyApp(MyAppDeco):
        "Simple placeholder"

        custom_attr = True

        def __init__(self):
            print("EXEC REGULAR INIT")
            self.TEST_INIT_REGULAR = True

            # Required in this case to call Node __init__
            # super().__init__()
            # If not called, Node Object can't be initialized

    # Test all different accesses
    app1 = MyApp()
    assert app1.TEST_INIT_REGULAR is True
    assert app1.demo() == "SUCCESS"

    # Ensure __init__ method never executed because not super().__init__()
    assert not hasattr(app1, "TEST_INIT_NEW")


def test_deco4_inherit():
    "Test that shows decorator inheritance"

    # Sample Data
    @newNode()
    class MyAppParent(MyAppDeco):
        "Simple placeholder"

        custom_attr = True

        def __post_init__(self, *args, **kwargs):
            print("EXEC POST INIT NEVER CALLED")
            self.TEST_INIT_NEW = "ERROR"

    # Sample Data
    @newNode()
    class MyApp(MyAppParent):
        "Simple placeholder"

        def __post_init__(self, *args, **kwargs):
            print("EXEC POST INIT")
            self.TEST_INIT_NEW = "OVERRIDE"

    # Test all different accesses
    app1 = MyApp()
    assert app1.TEST_INIT_NEW == "OVERRIDE"
    assert app1.demo() == "SUCCESS"

    # Ensure __init__ method never executed because not super().__init__()
    # assert not hasattr(app1, "TEST_INIT_NEW")


# ==============================================
# Mixins Tests
# ==============================================


# Logger
# ---------------------

from cafram.nodes.comp.base import LoggerMixin


def test_mixin_logger1():
    "Test that show how to use the logger"

    @newNode()
    @addMixin("cafram.nodes.comp.base:LoggerMixin")
    class MyApp1:
        def __post_init__(self, *args, **kwargs):
            # self.log.debug("DEBUG_Messages: INIT")
            print("DEBUG_Messages: INIT")

        def demo(self):
            self.log.debug("DEBUG_Messages")
            self.log.info("INFO_Messages")
            self.log.warning("WARNING_Messages")
            self.log.error("ERROR_Messages")

    print("DEBUUUGG 1")
    pprint(MyApp1.__dict__)

    app = MyApp1()

    print("DEBUUUGG 2")
    pprint(app.__dict__)
    pprint(app.__node__.__dict__)

    app.demo()

    pprint(app.__node__.__dict__)
    pprint(LoggerMixin.__dict__)
    assert hasattr(app, LoggerMixin.mixin_alias__log)
    # OLDassert hasattr(app, LoggerMixin.mixin_key)
    assert app(LoggerMixin.mixin_key)


# Config
# ---------------------

from cafram.nodes.comp.tree import (  # NodeConf,; map_node_class,; map_node_class_full,
    ConfDictMixin,
)

app_config = {
    "config": {
        "enabled": True,
        "desc": "This is a description",
        "remote": "http://gitlab.com/",
        "branches": ["main"],
        "var_files": [
            "first.env",
            "second.env",
        ],
    },
    "repos": [
        {
            "name": "my_repo1.git",
            "nested1": {
                "nested2": {
                    "nested3": {},
                },
            },
        },
        {
            "name": "my_repo2.git",
            "branches": ["main", "develop"],
            "enabled": False,
        },
    ],
}


def test_mixin_confdict1_children_true():
    "Test to show how to not create children with True (DEFAULT BEHAVIOR)"

    # Example Class
    @newNode()
    @addMixin("cafram.nodes.comp.tree:ConfDictMixin", children=True)  # "titi",
    class MyApp:
        "This is my main app"

        def __post_init__(self, my_opt=True, *args, **kwargs):
            print(f"LOCAL __INIT__ !: {my_opt}, {args}, {kwargs}")

        def demo(self):

            self.log.warning("WARNING_Messages")

    # Launch with config in init
    app = MyApp(payload=app_config)

    print("YOOO")
    pprint(app.__class__.__mro__)
    pprint(app.__node__.__dict__)
    # Test for aliases
    for attr in ["config", "repos", "value"]:
        assert hasattr(app, attr)
    # Test for aliases
    for attr in ["conf"]:
        assert app(attr)

    # Assert config is OK
    assert app["conf"].value == app_config

    # Launch without init config and load after
    app2 = MyApp()

    assert app2("conf").get_value() == {}
    app2("conf").set_value(app_config)
    # Then it should be equal
    assert app2("conf").value == app_config

    app2("conf").set_value({})
    assert app2.value == {}

    # Test other form of config access via value attribute alias
    app2.value = app_config
    assert app2.value == app_config

    # Test config json/yaml methods
    _yaml_conf = app2("conf").to_yaml()
    _json_conf = app2("conf").to_json()

    assert isinstance(_yaml_conf, str)
    assert isinstance(_json_conf, str)

    app2("conf").from_yaml(_yaml_conf)
    app2("conf").from_json(_json_conf)


def test_mixin_confdict2_children_false():
    "Test to show how to not create children with False"

    # Example Class
    @newNode()
    @addMixin("cafram.nodes.comp.tree:ConfDictMixin", children=False)  # "titi",
    class MyApp:
        "This is my main app"

        def demo(self):

            self.log.warning("WARNING_Messages")

    # Launch with config in init
    app = MyApp(payload=app_config)

    # Check aliases
    for attr in ["config", "repos", "value"]:
        assert hasattr(app, attr)

    # Check mixin
    for attr in ["conf"]:
        assert app(attr)

    # Assert config is OK
    assert app["conf"].value == app_config


def test_mixin_confdict3_children_none():
    "Test to show how to use children with None"

    # Example Class
    @newNode()
    @addMixin("cafram.nodes.comp.tree:ConfDictMixin", children=None)  # "titi",
    class MyApp:
        "This is my main app"

        def demo(self):

            self.log.warning("WARNING_Messages")

    # Launch with config in init
    app = MyApp(payload=app_config)

    # Check aliases
    for attr in ["config", "repos", "value"]:
        assert hasattr(app, attr)

    # Check mixin
    for attr in ["conf"]:
        assert app(attr)

    # Assert config is OK
    assert app["conf"].value == app_config


def test_mixin_confdict4_children_nodeconf_cls():
    "Test to show how to use children with class"

    # Example Class
    @newNode()
    # @addMixin("cafram.nodes.comp.tree:ConfDictMixin", children=NodeConf)  # "titi",
    @addMixin("cafram.nodes.comp.tree:ConfDictMixin", children=ConfMixin)  # "titi",
    class MyApp:
        "This is my main app"

        def demo(self):

            self.log.warning("WARNING_Messages")

    pprint(MyApp.__dict__)
    # Launch with config in init
    app = MyApp(payload=app_config)

    # Check aliases
    for attr in ["config", "repos", "value"]:
        assert hasattr(app, attr)

    # Check mixin
    for attr in ["conf"]:
        assert app(attr)

    # Assert config is OK
    assert app["conf"].value == app_config


def test_mixin_confdict5_children_nodeconf_str():
    "Test to show how to use children with string (class)"

    # Example Class
    @newNode()
    @addMixin(
        "cafram.nodes.comp.tree:ConfDictMixin",  # "titi",
        children="cafram.nodes.comp.tree:ConfMixin",
    )
    class MyApp:
        "This is my main app"

        def demo(self):

            self.log.warning("WARNING_Messages")

    # Launch with config in init
    app = MyApp(payload=app_config)

    # Check aliases
    for attr in ["config", "repos", "value"]:
        assert hasattr(app, attr)

    # Check mixin
    for attr in ["conf"]:
        assert app(attr)

    # Assert config is OK
    assert app["conf"].value == app_config

    # pprint (app.config.__dict__)
    # pprint (app.config.__node__.__dict__)
    # print ("HEHEEHEH")
    # pprint (app.config)
    # pprint (app.config.__node__.__dict__)

    # pprint (app.config.value)

    # # pprint (app.repos.__dict__)
    # # pprint (app.repos.__node__.__dict__)

    # assert False, "WIPPP"

    # assert app.config.value == app_config["config"]
    # assert app.repos.value == app_config["repos"]


# def test_mixin_confdict6_children_custom_cls():
#     "Test to show how to use children with string (class)"


#     @newNode()
#     @addMixin("cafram.nodes.comp.tree:ConfMixin", # "titi",
#         #children=False
#     )
#     class ItemConf():
#         "This is a config item"

#         def demo_conf(self):
#             self.log.warning("WARNING_Messages")
#             return self.conf.to_yaml()


#     # Example Class
#     @newNode()
#     @addMixin("cafram.nodes.comp.tree:ConfDictMixin", # "titi",
#         children=ItemConf
#     )

#     class MyApp():
#         "This is my main app"

#         def demo(self):
#             self.log.warning("WARNING_Messages")


#     # Launch with config in init
#     app = MyApp(payload=app_config)

#     assert app.config.value == app_config["config"]
#     assert app.repos.value == app_config["repos"]

#     assert False
