import traceback
import logging
from pprint import pprint
import pytest

from cafram.mixins.base import LoggerMixin, IdentMixin, PayloadMixin

from cafram.mixins.base import LoggerMixin
from cafram.mixins.tree import (
    ConfDictMixin,
    ConfListMixin,
    NodeConfDict,
    NodeConfList,
    ConfMixin,
)
from cafram.nodes2 import Node
from cafram.ctrl2 import NodeCtrl


print("Run test suite !")


# Test mixin: Ident
# ===============================================


def get_mixin_ident_conf():

    test_ident1 = "CustomIdent"
    test_prefix1 = "CustomPrefix"

    test_ident2 = "Node"
    test_prefix2 = "cafram.nodes2"

    conf = [
        # Test without object
        {
            "key": "basic",
            "obj": None,
            "kwargs": {},
            "result_ident": IdentMixin.__module__ + "." + IdentMixin.__name__,
            "result_ident_name": IdentMixin.__name__,
            "result_ident_prefix": IdentMixin.__module__,
        },
        {
            "key": "basic_name",
            "obj": None,
            "kwargs": {
                "ident": test_ident1,
            },
            "result_ident": IdentMixin.__module__ + "." + test_ident1,
            "result_ident_name": test_ident1,
            "result_ident_prefix": IdentMixin.__module__,
        },
        {
            "key": "basic_prefix",
            "obj": None,
            "kwargs": {
                "ident_prefix": test_prefix1,
            },
            "result_ident": test_prefix1 + "." + IdentMixin.__name__,
            "result_ident_name": IdentMixin.__name__,
            "result_ident_prefix": test_prefix1,
        },
        {
            "key": "basic_all",
            "obj": None,
            "kwargs": {
                "ident": test_ident1,
                "ident_prefix": test_prefix1,
            },
            "result_ident": test_prefix1 + "." + test_ident1,
            "result_ident_name": test_ident1,
            "result_ident_prefix": test_prefix1,
        },
        # Test with object
        {
            "key": "obj_basic",
            "obj": Node(),
            "kwargs": {},
            "result_ident": test_prefix2 + "." + test_ident2,
            "result_ident_name": test_ident2,
            "result_ident_prefix": test_prefix2,
        },
        {
            "key": "obj_basic_name",
            "obj": Node(),
            "kwargs": {
                "ident": test_ident1,
            },
            "result_ident": test_prefix2 + "." + test_ident1,
            "result_ident_name": test_ident1,
            "result_ident_prefix": test_prefix2,
        },
        {
            "key": "obj_basic_prefix",
            "obj": Node(),
            "kwargs": {
                "ident_prefix": test_prefix1,
            },
            "result_ident": test_prefix1 + "." + test_ident2,
            "result_ident_name": test_ident2,
            "result_ident_prefix": test_prefix1,
        },
        {
            "key": "obj_basic_all",
            "obj": Node(),
            "kwargs": {
                "ident": test_ident1,
                "ident_prefix": test_prefix1,
            },
            "result_ident": test_prefix1 + "." + test_ident1,
            "result_ident_name": test_ident1,
            "result_ident_prefix": test_prefix1,
        },
    ]
    return conf


@pytest.mark.parametrize("mixin_config", get_mixin_ident_conf())
def test_mixin_ident(mixin_config):

    # print ("")
    # print ("run parametrized test", mixin_config)

    # Extract data
    test_name = mixin_config.get("key")
    obj = mixin_config.get("obj")
    kwargs = mixin_config.get("kwargs")

    # Init mixin
    node_ctrl = NodeCtrl(node_obj=obj)
    mixin_inst = IdentMixin(node_ctrl, **kwargs)

    # Test methods
    ret = mixin_inst.get_ident_name()
    expected = mixin_config["result_ident_name"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"

    ret = mixin_inst.get_ident_prefix()
    expected = mixin_config["result_ident_prefix"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"

    ret = mixin_inst.get_ident()
    expected = mixin_config["result_ident"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"


# Test mixin: Payload
# ===============================================


def get_mixin_payload_conf():

    payload1 = "SimpleValue"
    payload2 = 123
    payload3 = True

    payload_dict1 = {"my_key": "SimpleValue dict1", "other_bool": True}
    payload_dict2 = {
        "my_other_key": "UPDATED DICT2",
        "nested_list": [456, "nettest_list2"],
    }
    payload_list1 = [123, True, "a string 1"]
    payload_list2 = ["a list2", {"netsted_key": "nexted_dict"}]

    return [
        {
            "desc": "basic payload",
            # "obj": Node(),
            "kwargs": {
                "payload": payload1,
            },
            "result_get_value": payload1,
            "arg_new_val": payload2,
            "result_new_val": payload2,
        },
        {
            "desc": "dict payload",
            # "obj": Node(),
            "kwargs": {
                "payload": payload_dict1,
            },
            "result_get_value": payload_dict1,
            "arg_new_val": payload_dict2,
            "result_new_val": payload_dict2,
        },
    ]


@pytest.mark.parametrize("mixin_config", get_mixin_payload_conf())
def test_mixin_payload(mixin_config):

    # print ("")
    # print ("run parametrized test", mixin_config)

    # Extract data

    # Extract data
    test_name = mixin_config.get("desc")
    obj = mixin_config.get("obj")
    kwargs = mixin_config.get("kwargs")

    # Init mixin
    mock_node_ctrl = NodeCtrl(node_obj=obj)
    mixin_inst = PayloadMixin(mock_node_ctrl, **kwargs)

    # pprint (mixin_inst.__dict__)

    # mixin_inst.doc(details=True)

    # Get value
    ret = mixin_inst.get_value()
    expected = mixin_config["result_get_value"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"

    # Update value and check
    mixin_inst.set_value(mixin_config["arg_new_val"])
    ret = mixin_inst.get_value()
    expected = mixin_config["result_new_val"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"

    # Check value setter and getter
    mixin_inst.value = mixin_config["arg_new_val"]
    ret = mixin_inst.value
    expected = mixin_config["result_new_val"]
    assert ret == expected, f"[{test_name}] Expected: {expected}, got: {ret}"


# PARAMS
# default: None
# ident: CustomIdent
# ident_prefix: None
# ident_suffix: None

# mixin_conf: {}
# mixin_key: payload
# mixin_order: 50

# name: None
# name_from_obj: False
# name_prefix: None
# value: None
# value_alias: value
