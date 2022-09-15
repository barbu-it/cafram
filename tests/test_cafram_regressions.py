
import sys
import unittest
from pprint import pprint 
import pytest
import logging 

from cafram.nodes import *

log = logging.getLogger()




# Testing regressions
# =====================================


payload_regression = {
    # Simple nodeval
    "_0_values": {
        "_0_key_str": "string",
        "_0_key_bool": True,
        "_0_key_int": 1234,
        "_0_key_null": None,
    },

    # Dict
    "_1_dict_empty": {},
    "_2_dict_nested": {
        "_0_dict": { "str": "string_value1" },
        "_1_dict": { "str": "string_value2" },
        "_2_dict": { "str": "string_value3" },
        "_3_dict": { "str": "string_value4" },
        "_4_dict_empty": {},
    },
    "_3_dict_mixed": {
        "_0_key_str": "string",
        "_1_key_bool": True,
        "_2_key_int": 1234,
        "_3_key_null": None,

        "_4_key_dict_empty": {},
        "_5_key_dict_misc": {
            "_0_key_str": "string",
            "_1_key_bool": True,
            "_2_key_int": 1234,
            "_3_key_null": None,
            "_4_key_dict_nested": {
                "_4_key_dict_nested": {
                    "_4_key_dict_nested": {
                        "nest_key": "nested_value"
                    }
                }
            }
        }
    },

    # List
    "_4_list_mixed": [
        "string1",
        1234,
        False,
        None,
    ],
    "_5_list_dict": [
        {
            "key": "value1",
        },
        {
            "key": "value2",
        },
        {
            "key": "value3",
        },
    ],
    "_6_list_list": [
        ["value1"],
        ["value2"],
        [1234],
    ],
    "_7_list_empty": [],
    "_8_list_mixed": [
        "value",
        12,
        True,
        {
            "key": "val",
            "dict": {
                "subkey": 1234
            }
        }
        
    ],
}


def test_autoconf_levels_get_values():

    node = NodeAuto(ident="AutoConf-1", payload=payload_regression, autoconf=-1)
    assert node.get_value() == {}

    node = NodeAuto(ident="AutoConf0", payload=payload_regression, autoconf=0)
    assert node.get_value() == payload_regression
    
    node = NodeAuto(ident="AutoConf1", payload=payload_regression, autoconf=1)
    assert node.get_value() == payload_regression

    node = NodeAuto(ident="AutoConf2", payload=payload_regression, autoconf=2)
    assert node.get_value() == {}

    node = NodeAuto(ident="AutoConf3", payload=payload_regression, autoconf=3)
    assert node.get_value() == {}




def test_autoconf_get_values_regressions(data_regression):

    node = NodeAuto(ident="AutoConf2", payload=payload_regression, autoconf=2)

    result = {}
    for name, i in node.get_children().items():
        out = i.get_value(lvl=-1)
        result[name] = out
    
    data_regression.check(result)

def test_autoconf_get_children_regressions(data_regression):

    node = NodeAuto(ident="AutoConf2", payload=payload_regression, autoconf=4)

    node.dump(all=True)

    result = {}
    for name, i in node.get_children().items():
        out = len(i.get_children())
        result[name] = out
    
    data_regression.check(result)





if __name__ == '__main__':
    unittest.main()