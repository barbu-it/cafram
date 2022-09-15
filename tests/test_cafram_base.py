
import sys
import unittest
from pprint import pprint 
import pytest
import logging 

from cafram.base import MissingIdent
from cafram.nodes import *
#from cafram.nodes_conf import *

log = logging.getLogger()


# Testing bases
# =====================================

class Test01_ConfVal(unittest.TestCase):
    "Test base objects"


    def test_ident_is_correctly_set(self):
        """
        Test class with ident
        """

        node = Base(ident="My App")
        self.assertEqual(node.ident, "My App")


    def test_fail_without_ident_arg(self):
        """
        Test if class fails if not named with ident
        """

        try:
            node = Base()
        except MissingIdent:
            pass
        except:
            self.assertFalse(True)

    def test_parents(self):
        """
        Ensure the _node_parent relationship work as expected
        """

        node = NodeMap(ident="TestInstance")
        self.assertEqual(node._node_parent, node._node_root)
        self.assertNotEqual(node._node_parent, None)
        self.assertNotEqual(node._node_root, None)

        node = NodeMap(ident="TestInstance", parent=None)
        self.assertEqual(node._node_parent, node._node_root)
        self.assertNotEqual(node._node_parent, None)
        self.assertNotEqual(node._node_root, None)

        # Todo: Test with inheritance
        # node = CustomConfigAttrIdent(parent="MyParent")
        # pprint (node.__dict__)
        # self.assertEqual(node._node_parent, node._node_root)
        # self.assertEqual(node._node_parent, None)


    def test_dump_method(self):
        """
        Ensure the dump method works correctly
        """

        node = NodeMap(ident="TestInstance")
        node.dump2()







# ConfMixed Testing
# ================================

payload_keydict = {
        "subkey2": "val2",
        "subkey3": 1234,
        "subkey4": None,
    }
payload_keylist = ["item1", "item2"]
payload_value = "MyValue"
payload = {
    "keyVal": payload_value,
    "keyDict": payload_keydict,
    "keyList": payload_keylist,
}


@pytest.fixture(scope="function")
def config_class(request):

    # Prepare class according payload
    params = request.param
    payload = request.param
    cls = map_all_class(payload)
    if isinstance(params, tuple):
        payload = params[0]
        cls = params[1] if len(params) > 1 else map_all_class(payload)
        
    print ("Create new obj:", cls, payload)
    class MyConfig(cls):
        ident="ConfigTest"

    # Create instance
    inst = MyConfig(ident=f"TestInstance-{cls}", payload=payload)
    return inst




# Simple tests
# ------------------------

@pytest.mark.parametrize("config_class", [
        (payload_keydict),
        (payload_keylist),
        (payload_value),
        (payload),
        ],
        indirect=["config_class"])
def test_is_root_method(config_class):
    "All instances should be root"
    assert config_class.is_root() == True


@pytest.mark.parametrize("config_class", [
        (payload_keydict),
        (payload_keylist),
        (payload_value),
        (payload),
        ],
        indirect=["config_class"])
def test_get_parent_method(config_class):
    "Parent should be self"
    assert config_class.get_parent() == config_class


@pytest.mark.parametrize("config_class", [
        (payload_keydict),
        (payload_keylist),
        (payload_value),
        (payload),
        ],
        indirect=["config_class"])
def test_get_parent_root_method(config_class):
    "Should return empty things"
    assert config_class.get_parent_root() == config_class


@pytest.mark.parametrize("config_class", [
        (payload_keydict),
        (payload_keylist),
        (payload_value),
        (payload),
        ],
        indirect=["config_class"])
def test_get_parents_method(config_class):
    "Should return empty things"

    assert config_class.get_parents() == []


# Data tests
# ------------------------

@pytest.mark.parametrize("config_class,result", [
        (payload_keydict, payload_keydict),
        (payload_keylist, payload_keylist),
        (payload_value, payload_value),
        ((payload, NodeDict), payload),
        ],
        indirect=["config_class"])
def test_node_get_value_method(config_class, result):
    assert config_class.get_value() == result


@pytest.mark.parametrize("config_class,result", [
        (payload_keydict, {}),
        (payload_keylist, []),
        (payload_value, None),

        ((payload, NodeDict), {}),
        ],
        indirect=["config_class"])
def test_get_children_method(config_class, result):
    "Should return empty things"
    assert config_class.get_children() == result


@pytest.mark.parametrize("config_class,result", [
        (payload_keydict, payload_keydict),
        (payload_keylist, payload_keylist),
        (payload_value, payload_value),
        (payload, payload),
        ],
        indirect=["config_class"])
def test_get_value_method(config_class, result):
    assert config_class.get_value() == result


@pytest.mark.parametrize("config_class,result", [
        (payload_keydict, payload_keydict),
        (payload_keylist, payload_keylist),
        (payload_value, payload_value),
        (payload, payload),
        ],
        indirect=["config_class"])
def test_is_root_method(config_class, result):
    assert config_class.serialize() == result


@pytest.mark.parametrize("config_class,result", [
        (payload_keydict, payload_keydict),
        (payload_keylist, payload_keylist),
        (payload_value, payload_value),
        (payload, payload),
        ],
        indirect=["config_class"])
def test_deserialize_method(config_class, result):
    config_class.deserialize(result)
    assert config_class.serialize() == result


@pytest.mark.parametrize("config_class,result", [
        (payload_keydict, payload_keydict),
        (payload_keylist, payload_keylist),
        (payload_value, payload_value),
        (payload, payload),
        ],
        indirect=["config_class"])
def test_serialize_method(config_class, result):
    assert config_class.serialize() == result


if __name__ == '__main__':
    unittest.main()