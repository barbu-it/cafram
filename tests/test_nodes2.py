#!/usr/bin/env pytest
# -*- coding: utf-8 -*-


import os
from pprint import pprint  # noqa: F401
import logging

import pytest


import cafram2.errors as errors
from cafram2.ctrl import NodeCtrl

from cafram2.mixins import BaseMixin
from cafram2.mixins.base import LoggerMixin, MapAttrMixin
# from cafram2.mixins.tree import PayloadMixin, DictConfMixin, ListConfMixin, SimpleConfMixin #, HierMixin


#from cafram2.mixins.tree import  _ContainerMixin

from cafram2.nodes import Node, Node
from cafram2.mixins.tree import NodePayload, NodeConf, NodeConfDict, NodeConfList

from cafram2.mixins.tree import HierMixin, HierParentMixin, HierChildrenMixin
from cafram2.mixins.tree import PayloadMixin, ConfMixin, ConfDictMixin, ConfListMixin


# Test payloads
# ------------------------


EX_PAYLOAD1 = {
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



# Test Bases/Units
# ------------------------


def test_node_empty(tester=None):

    tester = tester or Node()

    assert isinstance(tester._node._mixin_dict, dict)
    assert isinstance(tester._node._mixin_hooks, dict)
    assert isinstance(tester._node._mixin_shortcuts, dict)
    assert isinstance(tester._node._obj_attr, str)
    assert isinstance(tester._node._obj_conf, list)
    assert isinstance(tester._node._obj_has_attr, bool)



# Test Payload
# ------------------------


def run_payload_base(tester, payload):
    # Test parameters
    assert tester._node.payload._payload == payload

    # Test mixin methods
    ret = tester._node.payload.get_value()
    assert ret == payload
    
    # Test mixin methods
    ret = tester._node.payload.set_value("123")
    assert ret == "123"
    ret = tester._node.payload.get_value()
    assert ret == "123"

    # Restore previous state
    tester._node.payload.set_value(payload)


def test_node_payload(tester=None, payload=None):

    payload=payload or EX_PAYLOAD1
    node_conf = [
        {
            "mixin": PayloadMixin,
        }
    ]
    tester = tester or Node(node_conf=node_conf, payload=payload)

    # Run new tests
    # --------------

    # Run previous tests
    test_node_empty(tester=tester)

    # Run partial tests
    run_payload_base(tester, payload)

    # Test alias access
    assert tester._node.value == payload


# def test_node_container(tester=None):

#     payload=EX_PAYLOAD1
#     node_conf = [
#         {
#             "mixin": _ContainerMixin,
#         },
        
#     ]
#     tester = tester or Node(node_conf=node_conf, payload=payload)

#     # Test alias access
#     assert tester._node.value == payload



# Test ConfMixin
# ------------------------


def test_node_conf(tester=None):

    payload=EX_PAYLOAD1
    node_conf = [
        {
            "mixin": ConfMixin,
        },
        
    ]
    tester = tester or Node(node_conf=node_conf, payload=payload)

    # This should fail as we removed "name"="payload" in conf
    try:
        run_payload_base(tester, payload)
        assert False
    except errors.AttributeError:
        pass

    # pprint (tester._node.__dict__)

    # Test json deserializer/serializer
    val1 = tester._node.conf.get_value()
    ret = tester._node.conf.to_json()
    assert isinstance(ret, str)
    ret = tester._node.conf.from_json(ret)
    val2 = tester._node.conf.get_value()
    assert val1 == val2




# Test NodeDict Children
# ------------------------



def test_node_dict_children_false(tester=None):
    "Test when children=False, disable aliases and disable containers"

    # When children = True
    payload=EX_PAYLOAD1
    node_conf = [
        {
            "mixin": ConfDictMixin,
            "children": False,
        },
    ]
    tester = tester or NodeConf(node_conf=node_conf, payload=payload)

    # tester.dump()
    # pprint (None)
    # print ("UUUUUUUUUUUUUU")
    # tester.ex_dict.dump()

    # Generic mixin API works    
    assert tester.conf.value == payload
    assert tester.value == payload

    # Generic aliases works
    #pprint (tester._node.__dict__)
    #assert tester.ex_dict == payload["ex_dict"]

    # Mixins/aliases are not filled with dict keys
    ret = tester._node.mixin_list(mixin=True, shortcuts=True)
    assert set(ret) == set(["conf", "value"]) 

    try:
        ret = tester.ex_dict.value
        assert False
    except errors.AttributeError:
        pass
    try:
        ret = tester.ex_dict.ex_key1
        assert False
    except errors.AttributeError:
        pass

    # Test children count
    assert len(tester.conf.get_children()) == 0
   

def test_node_dict_children_none(tester=None):
    "Test when children=None, enable alias, disable containers"

    # When children = None
    payload=EX_PAYLOAD1
    node_conf = [
        {
            "mixin": ConfDictMixin,
            "children": None,
        },
    ]
    tester = tester or NodeConf(node_conf=node_conf, payload=payload)

    # Generic mixin API works
    assert tester.conf.value == payload
    assert tester.value == payload

    # Generic aliases works
    assert tester.ex_dict == payload["ex_dict"]

    # Ensure children=True atttribute fails
    try:
        ret = tester.ex_dict.value
        assert False
    except AttributeError:
        pass
    try:
        ret = tester.ex_dict.ex_key1
        assert False
    except AttributeError:
        pass

    # Test children count
    assert len(tester.conf.get_children()) == 2


def test_node_dict_children_true(tester=None):
    "Test when children=True, enable alias, enable containers and children"

    # When children = True
    payload=EX_PAYLOAD1
    node_conf = [
        {
            "mixin": ConfDictMixin,
            "children": True,
        },
    ]
    tester = tester or NodeConf(node_conf=node_conf, payload=payload)

    # tester.dump()
    # pprint (None)
    # print ("UUUUUUUUUUUUUU")
    # tester.ex_dict.dump()

    # Generic mixin API works    
    assert tester.conf.value == payload
    assert tester.value == payload

    # Test children count
    assert len(tester.conf.get_children()) == 2

    # Generic aliases works
    assert tester.ex_dict.value == payload["ex_dict"]
    assert tester.ex_dict.ex_key1 == payload["ex_dict"]["ex_key1"]

    # Dict and lists are now containers
   # assert tester.ex_dict.ex_list1 == payload["ex_dict"]["ex_list1"], "To be fixed when conflist is implemetned"
    
    assert tester.ex_dict.ex_list1 != payload["ex_dict"]["ex_list1"]
    assert tester.ex_dict.ex_list1.value == payload["ex_dict"]["ex_list1"]
    
    assert tester.ex_dict.ex_dict1 != payload["ex_dict"]["ex_dict1"]
    assert tester.ex_dict.ex_dict1.value == payload["ex_dict"]["ex_dict1"]

    


def test_node_dict_get_parents(tester=None):
    "Test when children=True, enable alias, enable containers and children"

    # When children = True
    payload=EX_PAYLOAD1
    node_conf = [
        {
            "mixin": ConfDictMixin,
            "children": True,
        },
    ]
    tester = tester or NodeConf(node_conf=node_conf, payload=payload)

    # Test get_parent and get_parents
    ret1 = tester.ex_dict.ex_dict1.conf.get_parents(1)[0]
    ret2 = tester.ex_dict.ex_dict1.conf.get_parents()
    ret3 = tester.ex_dict.ex_dict1.conf.get_parents(1)[-1]

    # Ensure relationships
    assert ret1 == tester.ex_dict.ex_dict1.conf.get_parent(), "Ensure first element of get_parents is get_parent"
    assert ret1 == ret2[0], "Ensure first element is the element returned by get_parent()"
    assert tester._node == ret2[-1], f"Ensure last element is root node"
    assert tester.ex_dict._node == ret2[-2], f"Ensure last element is root node"
    assert len(ret2) == 2, "Ensure there are 2 parents for this node"

    assert ret3 == ret2[-1], "Ensure get_root_parent return the top parent only"
    assert tester.ex_dict.ex_dict1._node != ret1, "Ensure the current node is not included in result"
    assert not tester.ex_dict.ex_dict1._node in ret2, "Ensure the current node is not included in results"
    
    # Ensure parents returns correct number of args
    assert len(tester.ex_dict.ex_dict1.conf.get_parents()) == 2
    assert len(tester.ex_dict.ex_dict1.conf.get_parents(level=0)) == 0
    assert len(tester.ex_dict.ex_dict1.conf.get_parents(level=1)) == 1
    assert len(tester.ex_dict.ex_dict1.conf.get_parents(level=2)) == 2
    assert len(tester.ex_dict.ex_dict1.conf.get_parents(level=3)) == 2
    assert len(tester.ex_dict.ex_dict1.conf.get_parents(level=50)) == 2
    


def test_node_dict_get_children(tester=None):
    "Test when children=True, enable alias, enable containers and children"

    # When children = True
    payload=EX_PAYLOAD1
    node_conf = [
        {
            "mixin": ConfDictMixin,
            "children": True,
        },
    ]
    tester = tester or NodeConf(node_conf=node_conf, payload=payload)

    assert tester.conf.get_children() == tester.conf.get_children(level=0), "Ensure optional param works as expected"
    
    ret = tester.conf.get_children(level=-1)
    assert ret == payload, "Ensure the whole payload can be retrieved on infinite recursion"
    assert isinstance(ret["ex_dict"]["ex_dict1"], dict)

    ret = tester.conf.get_children(level=1)
    assert isinstance(ret["ex_dict"]["ex_dict1"], Node)



def test_node_conf_variants(tester=None):
    "Test various forms of node_confs"

    # When children = True
    payload=EX_PAYLOAD1
    node_confs = [
        [
            {
                "mixin": ConfDictMixin,
            }
        ],
        [
            ConfDictMixin,
        ],
        {
            "conf": ConfDictMixin,
        },
        {
            "conf": {
                "mixin": ConfDictMixin,
            }
        }
    ]

    for node_conf in node_confs:
        tester = Node(node_conf=node_conf, payload=payload)
        tester.dump(stdout=False)




# ########### OOOLDDD D??




# class CollectionTester():

#     def __init__(self, tester):
#         self.node = tester

#     def test_value(self, expected):
#         assert self.node._node.conf.value == expected

#     def test_payload(self, expected):
#         assert self.node._node.conf._payload == expected


#     def get_mixin(self, name):
#         return getattr(self.node._node, name, None)
        

#     def get_mixin_tester(self, name):
#         cls = self.__class__
#         return cls(self.get_mixin(name))

#     def get_children(self, children):
#         inst = self
#         for child in children:
#             inst = inst.get_mixin(name)

#         return inst

# def test_node_dict_mapping_auto(tester=None):

#     payload=EX_PAYLOAD1
#     node_conf = [
#         {
#             "mixin": ConfDictMixin,
#             "children": True,
#             # Create mapping automatic children
#         },
#     ]
#     tester = tester or NodeConf(node_conf=node_conf, payload=payload)

#     # Test basics    
#     ret = tester._node.conf._payload
#     assert ret == payload

#     ret = tester._node.conf.value
#     assert ret == payload

#     # Features: None , mixins and shortcuts list should be simple type
#     ret = tester._node.ex_dict._node.conf.value
#     assert ret == payload["ex_dict"]

#     # pprint ("WIPP")
#     # pprint (tester._node.__dict__)

#     ret = tester._node.ex_val
#     assert ret == payload["ex_val"]


#     # Features: None, mixins and shortcuts list should be empty
#     ret = tester._node.mixin_list(mixin=True, shortcuts=False)
#     assert ret == ["conf"] 
#     ret = tester._node.mixin_list(mixin=False, shortcuts=True)
#     assert set(ret) == set(["ex_val", "ex_dict"])
#     assert tester._node.conf.value == payload

#     # Class tester
#     tester_ = CollectionTester(tester)
#     tester_.test_value(payload)
#     tester_.test_payload(payload)
    
#     ex_dict_ = tester_.get_mixin_tester("ex_dict")
#     ex_dict_.test_value(payload["ex_dict"])
#     ex_dict_.test_payload(payload["ex_dict"])
#     assert payload["ex_dict"] == ex_dict_.get_mixin("conf").value

#     ret = tester_.get_mixin("ex_val")
#     assert ret == payload["ex_val"]








######## VERY OLD













    # ret = tester._node.payload
    # print (ret)


# {
#             "mixin": MapAttrMixin,
#         },


# def test_cont_payload(tester=None, payload=None):


#     payload = payload or EX_PAYLOAD1
#     # Test setup
#     if not tester:
#         mixin_confs = [
#                 {
#                     "mixin": PayloadMixin,
#                 }
#             ]
#         tester = Node(node_mixins=mixin_confs, payload=payload)



#     # Tests low level APIs
#     ret = tester._node.conf.value()
#     assert ret == payload, f"Got: {ret}"

#     ret = tester._node.conf.children["ex_val"]._node.conf.value()
#     assert ret == "Hello World!", f"Got: {ret}"

#     ret = tester._node.conf.children["ex_dict"]._node.conf.value()
#     assert ret == payload["ex_dict"], f"Got: {ret}"

#     ret = tester._node.conf.children["ex_dict"]._node.conf.value()["ex_key1"]
#     assert ret == payload["ex_dict"]["ex_key1"], f"Got: {ret}"


