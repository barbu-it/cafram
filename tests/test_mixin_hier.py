import traceback
import logging
from pprint import pprint
import pytest

# from cafram.mixins.base import LoggerMixin, IdentMixin, PayloadMixin

from cafram.mixins.hier import HierParentMixin, HierChildrenMixin
from cafram.nodes2 import Node
from cafram.ctrl2 import NodeCtrl


print("Run test suite !")


# Test mixin: HierParentMixin
# ===============================================


def get_mixin_hierparent_conf():

    # payload1 = "SimpleValue"
    # payload2 = 123
    # payload3 = True

    # payload_dict1 = {"my_key": "SimpleValue dict1", "other_bool": True}
    # payload_dict2 = {"my_other_key": "UPDATED DICT2", "nested_list": [456, "nettest_list2"]}
    # payload_list1 = [123, True, "a string 1"]
    # payload_list2 = ["a list2", {"netsted_key": "nexted_dict" }]

    return [
        {
            "desc": "basic payload",
            # "obj": Node(),
            "kwargs": {
                #    "payload": payload1,
            },
            "result_get_parents": [],
            "result_get_child_level": 0,
        },
    ]


@pytest.mark.parametrize("mixin_config", get_mixin_hierparent_conf())
def test_mixin_hierparent(mixin_config):

    # print ("")
    # print ("run parametrized test", mixin_config)

    # Extract data

    # Extract data
    test_name = mixin_config.get("desc")
    obj = mixin_config.get("obj")
    kwargs = mixin_config.get("kwargs")

    # Init mixin
    mock_node_ctrl = NodeCtrl(node_obj=obj)
    mixin_inst = HierParentMixin(mock_node_ctrl, **kwargs)

    pprint(mixin_inst.__dict__)

    # Test methods
    ret = mixin_inst.get_parents()
    expected = mixin_config["result_get_parents"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"

    ret = mixin_inst.get_child_level()
    expected = mixin_config["result_get_child_level"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"


# Test mixin: HierChildrenMixin
# ===============================================


def get_mixin_hierchildren_conf():

    # payload1 = "SimpleValue"
    # payload2 = 123
    # payload3 = True

    # payload_dict1 = {"my_key": "SimpleValue dict1", "other_bool": True}
    # payload_dict2 = {"my_other_key": "UPDATED DICT2", "nested_list": [456, "nettest_list2"]}
    # payload_list1 = [123, True, "a string 1"]
    # payload_list2 = ["a list2", {"netsted_key": "nexted_dict" }]

    return [
        {
            "desc": "basic payload",
            # "obj": Node(),
            "kwargs": {
                #    "payload": payload1,
            },
            "result_get_children": [],
            # "result_get_child_level": 0,
        },
    ]


@pytest.mark.parametrize("mixin_config", get_mixin_hierchildren_conf())
def test_mixin_hierparent(mixin_config):

    # print ("")
    # print ("run parametrized test", mixin_config)

    # Extract data

    # Extract data
    test_name = mixin_config.get("desc")
    obj = mixin_config.get("obj")
    kwargs = mixin_config.get("kwargs")

    # Init mixin
    mock_node_ctrl = NodeCtrl(node_obj=obj)
    mixin_inst = HierChildrenMixin(mock_node_ctrl, **kwargs)

    # pprint (mixin_inst.__dict__)

    # Test methods
    ret = mixin_inst.get_children()
    expected = mixin_config["result_get_children"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"

    # ret = mixin_inst.get_child_level()
    # expected = mixin_config["result_get_child_level"]
    # assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"
