#!/usr/bin/env pytest
# -*- coding: utf-8 -*-


import os
from pprint import pprint  # noqa: F401
import logging

import pytest

from cafram2.ctrl import NodeCtrl
from cafram2.nodes import Node, Node2

from cafram2.mixins.base import LoggerMixin, MapAttrMixin
from cafram2.mixins.tree import ValueMixin, DictConfMixin, ListConfMixin, SimpleConfMixin #, HierMixin



# Test stacks vars scenarios
# ------------------------


def generate_base(mixin_confs=None):
    
    class Tester():
        def __init__(self, *args, **kwargs):
            #NodeCtrl(obj=self, attr="_node", mixin_confs=mixin_confs, *args, **kwargs)
            NodeCtrl(obj=self, mixin_confs=mixin_confs, *args, **kwargs)

    return Tester


# Test mixins Base
# ------------------------


def test_logger_mixin(tester=None):

    # Test setup
    if not tester:
        mixin_confs = [
            {
                    "mixin": LoggerMixin,
                    "logger_key": "log2",
                },
            ]
        TestApp = generate_base(mixin_confs=mixin_confs)
        tester = TestApp()


    # Tests
    tester._node.logger.log.warning("TEST - warning 1")
    #pprint (tester._node.__dict__)
    tester._node.log2.warning("TEST - warning 2")








def lib_tests_remap_1(tester=None, attr_map=False, attr_forward=False):

    # Test setup
    if not tester:

        attr_map = {
            "conf3": "store",
            "conf4": "conf2",
        }
        
        mixin_confs = [
            {
                "mixin": ValueMixin,
                "key": "store",
            },
            {
                "mixin": ValueMixin,
                "key": "conf2",
            },
            # Should always be last
            {
                "mixin": MapAttrMixin,
                "attr_map": attr_map,
                "attr_forward": attr_forward,
            },
        ]

        TestApp = generate_base(mixin_confs=mixin_confs)
        tester = TestApp()

    # Test with store
    #test_store(tester)

    

    if attr_forward:
        #pprint (attr_map)

        # Tests alias base
        tester._node.conf4.value("value10")
        ret = tester._node.conf2.value()
        assert ret == "value10", ret
        
        tester.conf3.value("value6")
        ret = tester.conf3.value()
        assert ret == "value6", ret

        # Tests alias xssing
        tester._node.conf3.value("value5")
        ret = tester._node.conf3.value()
        assert ret == "value5", ret


    else:
        # Ensure args are not propagated
        try:
            ret = tester.conf3.value()
            assert False, f"This should have failed, got: {ret}"
        except AttributeError:
            pass
        


def test_remap_all(tester=None):
    
    lib_tests_remap_1(attr_forward=False)
    lib_tests_remap_1(attr_forward=False)
    lib_tests_remap_1(attr_forward=True)

    # attr_map = "__AUTO__"
    # lib_tests_remap_1(attr_map=attr_map)



# Test mixins Values
# ------------------------

# from cafram2.mixins.tree import ValueMixin, DictConfMixin, ListConfMixin, SimpleConfMixin #, HierMixin


def test_value_mixin(tester=None):

    # Test setup
    if not tester:
        mixin_confs = [
                {
                    "mixin": ValueMixin,
                    "key": "store",
                },
                {
                    "mixin": ValueMixin,
                    "key": "conf2",
                },
            ]
        TestApp = generate_base(mixin_confs=mixin_confs)
        tester = TestApp()


    # Tests default
    # pprint (tester._node.__dict__)
    # pprint (tester._node.store.__dict__)
    ret = tester._node.store.value()
    assert ret is None, f"Got: {ret}"

    tester._node.store.value("value1")
    ret = tester._node.store.value()
    assert ret == "value1"

    tester._node.store.value(None)
    ret = tester._node.store.value()
    assert ret == None

    tester._node.store.value(["value1", "value2"])
    ret = tester._node.store.value()
    assert ret == ["value1", "value2"]

    tester._node.store.value({"key1": "value2"})
    ret = tester._node.store.value()
    assert ret == {"key1": "value2"}

    # Tests second instance
    ret = tester._node.conf2.value()
    assert ret is None

    tester._node.conf2.value("value1")
    ret = tester._node.conf2.value()
    assert ret == "value1"

    # Test dict access via dunder
    ret = tester._node["conf2"].value()
    assert ret == "value1"

    tester._node.conf2.value(None)
    ret = tester._node.conf2.value()
    assert ret == None



def test_container_mixin1(tester=None, payload=None):

    payload = payload or {
        "ex_val": "Hello World!",
        "ex_dict": {
            "ex_key1": "This is a string",
            "ex_list1": [
                "ex_bool1=True",
            ],
            "ex_dict1": {
                "ex_bool2": True,
            },       
        }
    }

    # Test setup
    if not tester:
        mixin_confs = [
                {
                    "mixin": DictConfMixin,
                }
            ]
        tester = Node2(node_mixins=mixin_confs, payload=payload)

    # Tests low level APIs
    ret = tester._node.conf.value()
    assert ret == payload, f"Got: {ret}"

    ret = tester._node.conf.children["ex_val"]._node.conf.value()
    assert ret == "Hello World!", f"Got: {ret}"

    ret = tester._node.conf.children["ex_dict"]._node.conf.value()
    assert ret == payload["ex_dict"], f"Got: {ret}"

    ret = tester._node.conf.children["ex_dict"]._node.conf.value()["ex_key1"]
    assert ret == payload["ex_dict"]["ex_key1"], f"Got: {ret}"




def test_container_mixin2(tester=None, payload=None):

    payload = payload or {
        "ex_val": "Hello World!",
        "ex_dict": {
            "ex_key1": "This is a string",
            "ex_list1": [
                "ex_bool1=True",
            ],
            "ex_dict1": {
                "ex_bool2": "PROBLEMATIC VALUE",
            },       
        }
    }

    # Test setup
    if not tester:
        mixin_confs = [
                {
                    "mixin": DictConfMixin,
                    "children": ValueMixin,
                    #"children": True,
                    #"children": False,
                },
                {
                    "mixin": MapAttrMixin,
                    #"key": "debug"

                    #"attr_map": attr_map,
                    #"attr_forward": attr_forward,
                },
            ]
        tester = Node2(node_mixins=mixin_confs, payload=payload)


    pprint(tester.__dict__)
    pprint(tester._node.__dict__)

    tester._node.dump(mixins=True)

    ret = tester.value
    assert ret == payload

    ret = tester.conf.value["ex_val"]
    assert ret == payload["ex_val"]

    ret = tester.conf.value["ex_dict"]
    assert ret == payload["ex_dict"]

    ret = tester.conf.value["ex_dict"]["ex_key1"]
    assert ret == payload["ex_dict"]["ex_key1"]

    ret = tester.conf.value["ex_dict"]["ex_dict1"]
    assert ret == payload["ex_dict"]["ex_dict1"]

    tester._node.dump(mixins=True)



# def test_container_mixin3(tester=None, payload=None):

#     payload = payload or {
#         "ex_val": "Hello World!",
#         "ex_dict": {
#             "ex_key1": "This is a string",
#             "ex_list1": [
#                 "ex_bool1=True",
#             ],
#             "ex_dict1": {
#                 "ex_bool2": "PROBLEMATIC VALUE",
#             },       
#         }
#     }

#     # Test setup
#     if not tester:
#         mixin_confs = [
#                 {
#                     "mixin": DictConfMixin,
#                     "children": ValueMixin,
#                     #"children": True,
#                     #"children": False,
#                 },
#                 {
#                     "mixin": MapAttrMixin,
#                     #"key": "debug"

#                     #"attr_map": attr_map,
#                     #"attr_forward": attr_forward,
#                 },
#             ]
#         tester = Node2(node_mixins=mixin_confs, payload=payload)




# Test user stories
# ------------------------

def test_user_story(tester=None):

    # Test setup
    if not tester:
        mixin_confs = [
        {
            "mixin": LoggerMixin,
            #"logger_key": "log2",
        },
        {
            "mixin": SimpleConfMixin,
        },
        {
            "mixin": MapAttrMixin,
            "attr_forward": True,
        },
    ]
        TestApp = generate_base(mixin_confs=mixin_confs)
        tester = TestApp()

    # Quick usage for logs
    tester.log.debug("LOGGING: Init easy app")

    # Quick usage for conf
    tester.conf.value("value_123")
    ret = tester.conf.value()
    assert ret == "value_123", ret






# EXAMPLES
# =================================
# import importlib
# common = importlib.import_module("common_lib")


# def test_cli_info_without_project(caplog):

#     caplog.set_level(logging.INFO, logger="paasify.cli")
#     pass

# def test_stacks_vars(caplog, data_regression) -> None:
#     "Ensure name, app path and direct string config works correctly"

#     caplog.set_level(logging.INFO, logger="paasify.cli")

#     # Load project
#     root_prj = cwd + "/tests/examples/var_merge"
#     app_conf = {
#         "config": {
#             "root_hint": root_prj,
#         }
#     }
#     psf = PaasifyApp(payload=app_conf)

#     prj = psf.load_project()
#     prj.stacks.cmd_stack_assemble()

#     # Check results
#     common.recursive_replace(root_prj, root_prj, os.path.relpath(root_prj))
#     results = common.load_yaml_file_hierarchy(root_prj)
#     data_regression.check(results)