
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
from cafram.ctrl2 import NodeCtrl

from cafram.mixins import BaseMixin
from cafram.mixins.base import LoggerMixin, MapAttrMixin

# from cafram.mixins.tree import PayloadMixin, DictConfMixin, ListConfMixin, SimpleConfMixin #, HierMixin


# from cafram.mixins.tree import  _ContainerMixin

from cafram.nodes2 import Node, Node
from cafram.mixins.base import PayloadMixin
from cafram.mixins.hier import HierMixin, HierParentMixin, HierChildrenMixin
from cafram.mixins.tree import NodePayload, NodeConf, NodeConfDict, NodeConfList
from cafram.mixins.tree import ConfMixin, ConfDictMixin, ConfListMixin



from cafram.decorators import newNode, addMixin

# Examples 1
# ------------------------


@newNode()
@addMixin("cafram.mixins.base:LoggerMixin")
class MyApp1():
    "This is my main app"

    # _node_config1 = True
    # _node_config2 = True
    # _node__KEY__OPT = True
    # _node__KEY__OPT2 = True

    # _ZZZZZZZZZZZZZZz = True

    def __post_init__(self, *args, my_opt=True, **kwargs):
        print(f"LOCAL __INIT__ !: {my_opt}, {args}, {kwargs}")


    def _init(self, **kwargs):

        self.log.info("App initialization complete!")


    # def __getitem__(self, name):
    #     print ("OVERRIDED GET ITEM METHOD")
    #     return "WEEEEEEEEEEEEEE"

    def log_demo(self):

        pprint (self.__dict__)
        pprint (self.__node__.__dict__)

        self.log.debug("TEST_DEBUG_Messages")
        self.log.info("TEST_INFO_Messages")
        self.log.warning("TEST_WARNING_Messages")
        self.log.error("TEST_ERROR_Messages")


def test_app1():

    # Test all different accesses

    tapp = MyApp1()

    # Test decorator params
    assert hasattr(tapp, "__node__params__")
    assert isinstance(tapp.__node__params__, dict)

    # Test internal object access
    assert hasattr(tapp, "__node__")

    # Test logger mixin
    assert hasattr(tapp, "log")
    assert hasattr(tapp, "logger")

    nctl = tapp.__node__

    # Assert internal components
    assert nctl._obj == tapp
    assert nctl._obj_attr == "__node__"

    tapp.log_demo()
    tapp.__node__.dump()

    # Debug mode
    if False:
        print (type(tapp))
        pprint (tapp.__dict__)
        pprint (nctl.__dict__)

        assert False, "WIPPP"



    # print("===")
    # print (app.config.conf.to_yaml())
    # print("===")
    # print (app.config["conf"].to_yaml())

    # print("===")
    # print (app.config.__node__.conf.to_yaml())
    # print("===")
    # print (app.config.__node__["conf"].to_yaml())
    # print("===")
    # print (app.config.__node__._mixin_dict["conf"].to_yaml())
    # print("===")

    # print (app.config.conf.doc())




# Examples 1
# ------------------------


@newNode()
class MyApp2():
    "This is my main app"


    def __post_init__(self, *args, my_opt=True, **kwargs):
        print(f"LOCAL __INIT__ !: {my_opt}, {args}, {kwargs}")

        self.my_option = my_opt

    def log_demo(self):

        pprint (self.__dict__)
        pprint (self.__node__.__dict__)

        # self.log.debug("TEST_DEBUG_Messages")
        # self.log.info("TEST_INFO_Messages")
        # self.log.warning("TEST_WARNING_Messages")
        # self.log.error("TEST_ERROR_Messages")


def test_app2():

    # Test all different accesses

    tapp = MyApp2()

    # Test decorator params
    assert hasattr(tapp, "__node__params__")
    assert isinstance(tapp.__node__params__, dict)

    # Test internal object access
    assert hasattr(tapp, "__node__")

    # Test logger mixin
    # assert hasattr(tapp, "log")
    # assert hasattr(tapp, "logger")

    nctl = tapp.__node__

    # Assert internal components
    assert nctl._obj == tapp
    assert nctl._obj_attr == "__node__"

    tapp.log_demo()
    nctl.dump()

    # Debug mode
    if False:
        print (type(tapp))
        pprint (tapp.__dict__)
        pprint (nctl.__dict__)

        assert False, "WIPPP"