#!/usr/bin/env pytest
# -*- coding: utf-8 -*-


import logging
import os
import traceback
from pprint import pprint  # noqa: F401

import pytest

import cafram.errors as errors
from cafram.nodes import Node
from cafram.nodes.comp import BaseMixin
from cafram.nodes.comp.base import LoggerMixin, MapAttrMixin, PayloadMixin
from cafram.nodes.comp.hier import HierChildrenMixin, HierMixin, HierParentMixin
from cafram.nodes.comp.tree import (
    ConfDictMixin,
    ConfListMixin,
    ConfMixin,
    # NodeConf,
    # NodeConfDict,
    # NodeConfList,
    # NodePayload,
)

# from cafram.tools import NodeConfigLoader, MixinConfigLoader
from cafram.nodes.ctrl import NodeCtrl


# ConfigLoader
# ------------------------


def test_node_config_parser():
    class MyApp(Node):

        # 1. Inheritable attributes
        # =========================

        # Simple inherited param config
        __node___param_opt_inherit__ = True

        # Simple inherited mixin OVERRIDE config
        __node___param_obj_mixins__ = {
            "log": {
                "mixin_key": "Blihh",
                # "mixin": "Blihh",
                "mixin_many": "YEAH",
                "override": "ATTR DICT MIXIN",
            }
        }

        # Simple inherited mixin config
        __node___mixin__log__mixin__ = LoggerMixin
        __node___mixin__log__mixin_key__ = "logger"
        __node___mixin__log__mixin_one__ = "YEAH"
        __node___mixin__log__override = "SINGLE ATTR"

        # 2. Decorator attributes
        # =========================
        __node___params__ = {
            "param1": "Yeahhh",
            "obj_mixins": {
                "mixin1": {
                    "mixin": ConfListMixin,
                    "override": "params",
                    "params": "params",
                },
                # "mixin2": {
                #     "mixin": ConfDictMixin
                # },
            },
        }
        __node___mixins__ = {
            "mixin1": {
                "mixin": ConfMixin,
                "override": "deco",
                "mixins": "mixins",
            },
            # "mixin3": {
            #     "mixin": ConfListMixin
            # },
        }

    # TODO: TEst with kwargs !!!

    app = MyApp()

    pprint(app.__node__.__dict__)

    expected_config = {
        "_obj_mixins": {
            "log": {
                "mixin": LoggerMixin,
                "mixin_key": "Blihh",
                "mixin_many": "YEAH",
                "mixin_one": "YEAH",
                "mixin_order": 30,
                "override": "ATTR DICT MIXIN",
            },
            "mixin1": {
                "mixin": ConfMixin,
                "mixin_key": "mixin1",
                "mixin_order": 50,
                "mixins": "mixins",
                "override": "deco",
                "params": "params",
            },
        },
    }

    assert expected_config.get("_obj_mixins") == app.__node__._obj_mixins


# from cafram.decorators import newNode, addMixin

# ConfigLoader
# ------------------------


# def test_configloader_nodectrl_NEW():
#     "Test good functionning of NodeConfigLoader"

#     class NodeCls(Node):

#         # Config load order, last wins:
#         # - generic class attribute
#         # - decorator config
#         # - __init__ config

#         # Node: Config via class (inherited) attributes
#         # ----------------------------------------
#         # Note:
#         #   - Support Native Python inheritance
#         # Usage:
#         #   _node__<KEY> = <VALUE>                      : Configure NodeCtrl
#         #   _node_mixin__<MIXIN>__<KEY> = <VALUE>       : Configure Mixin Configuration

#         _node__KEY1 = True
#         _node__KEY2 = True
#         _node__KEY3 = True

#         _node_mixin__mixin1__mixin_enabled = False
#         _node_mixin__mixin1__aconf = "VALUE"

#         _node_mixin__mixin9__mixin_enabled = False
#         _node_mixin__mixin9__aconf = "VALUE"

#         # Node: Config via decorator attrs
#         # ----------------------------------------
#         # Note:
#         #   - Support Native Python inheritance (ONLY when inherit=True)
#         # Usage:
#         #   @newNode()
#         #   @addMixin("MIXIN_CLS" [, "MIXIN_KEY"] [, **mixin_conf])
#         # Note:
#         #  When you use decorators, it works with 2 class attributes: __node_params__ and __node_mixins__
#         #  If you enable inheritance, then all attributes are added to class (see above)

#         __node_params__ = {"KEY1": "OVERRIDED by Decorator"}
#         __node_mixins__ = {
#             "mixin1": {
#                 "mixin_key": "NEWKEY",
#             },
#             "mixin2": {
#                 "mixin_key": "NEWKEY",
#             },
#             "mixin8": {
#                 "mixin_key": "NEWKEY",
#             },
#         }

#     # Node: Config via mixin_conf from __init__()
#     # ----------------------------------------
#     # Note:
#     #   - Does NOT Support Native Python inheritance
#     #   - Recommended for generic live object, such as nested children
#     # Usage:
#     #   mixin = MixinClass(mixin_conf={})

#     mixin_conf = {
#         "mixin1": {
#             "mixin_enabled": True,
#         },
#         "mixin2": {
#             "mixin_enabled": True,
#             "mixin_key": "NEWKEY2",
#         },
#         "mixin3": {
#             "mixin_enabled": True,
#         },
#         "mixin7": {
#             "mixin_enabled": True,
#         },
#     }

#     # Direct __init__ param override
#     kwargs = {
#         "KEY2": "OVERRIDEDN BY KWARGS",
#         "obj_attr": "__node__",
#     }

#     tobj1 = NodeCls()

#     # Live patch for stict mode, as example are pretty bad
#     STRICT = True
#     if STRICT:
#         setattr(tobj1.__node__, "KEY1", "test_only")
#         setattr(tobj1.__node__, "KEY2", "test_only")
#         setattr(tobj1.__node__, "KEY3", "test_only")
#         setattr(tobj1.__node__, "obj_attr", "test_only")
#         setattr(tobj1.__node__, "obj_conf", "test_only")

#     # Generate the loader object
#     tloader = NodeConfigLoader(tobj1.__node__, obj_src=tobj1)
#     mixin_conf = tloader.build(kwargs_mixins=mixin_conf, kwargs=kwargs, strict=STRICT)

#     # DEbug
#     print("DEBUG")
#     pprint(tobj1.__dict__)
#     pprint(tobj1.__node__.__dict__)
#     pprint(mixin_conf)
#     print("EOOOFFF")

#     # Test nodectrl configuration
#     assert tobj1.__node__.KEY1 == "OVERRIDED by Decorator"
#     assert tobj1.__node__.KEY2 == "OVERRIDEDN BY KWARGS"
#     assert tobj1.__node__.KEY3 == True

#     # Test mixin configuration
#     assert mixin_conf == {
#         "KEY1": "OVERRIDED by Decorator",
#         "KEY2": "OVERRIDEDN BY KWARGS",
#         "KEY3": True,
#         "obj_attr": "__node__",
#         "obj_conf": {
#             "mixin1": {"aconf": "VALUE", "mixin_enabled": True, "mixin_key": "NEWKEY"},
#             "mixin2": {"mixin_enabled": True, "mixin_key": "NEWKEY2"},
#             "mixin3": {"mixin_enabled": True},
#             "mixin7": {"mixin_enabled": True},
#             "mixin8": {"mixin_key": "NEWKEY"},
#             "mixin9": {"aconf": "VALUE", "mixin_enabled": False},
#         },
#     }


# def test_configloader_mixins():
#     "Test good functionning of MixinConfigLoader"

#     # Mock mixin
#     class MixinCls(BaseMixin):
#         mixin_enabled = True
#         mixin_cls = None
#         mixin_key = "MyKey"
#         mixin_param__ATTR1 = "attr1"  # Declare param and remap
#         mixin_param__ATTR2 = "attr2"  # Declare param and remap
#         mixin_param__ATTR3 = None  # Declare param only, no change
#         mixin_alias__ALIAS1 = "alias1"
#         mixin_alias__ALIAS2 = "alias2"
#         mixin_alias__ALIAS3 = "alias3"

#         # When STRICT=True
#         # Example User Attributes, must be declared into class
#         ATTR1 = "default"
#         ATTR2 = "default"
#         ATTR3 = "default"

#         BUILT_CONFIG = None

#     # Must always reference existing mixin attributes, sent in __init__ mixin_conf
#     mixin_conf = {
#         "mixin_enabled": False,
#         "mixin_key": "MyKey",
#         # "mixin_key_FAIL": "MyKey",
#         # Conf override
#         "mixin_param__ATTR2": "attr2_new",  # Change remap for ATTR2
#         "mixin_alias__ALIAS2": "alias2_new",
#     }

#     # Allow new param creation/remap, sent via __init__ kwargs
#     runtime_params = {
#         "attr1": "INIT override value1",
#         "attr2_new": "INIT override value2_new",
#         "ATTR3": "user default param",
#         # "alias1": "INIT alias1",
#         # "alias2_new": "INIT alias2_new",
#     }

#     # # Test load
#     tobj1 = Node()
#     tobj2 = MixinCls(tobj1.__node__)
#     tloader = MixinConfigLoader(tobj2)

#     # aliases = tloader.build(mixin_conf=mixin_conf, kwargs=runtime_params, strict=False)
#     aliases = tloader.build(mixin_conf=mixin_conf, kwargs=runtime_params, strict=True)

#     pprint(tobj2.__dict__)

#     # Check dynconf
#     assert tobj2.mixin_enabled == False
#     assert tobj2.mixin_key == "MyKey"

#     # Check __init__ param overrides
#     assert tobj2.ATTR1 == "INIT override value1"
#     assert tobj2.ATTR2 == "INIT override value2_new"
#     assert tobj2.ATTR3 == "user default param"

#     pprint(aliases)

#     # assert aliases == {'ALIAS1': 'alias1', 'ALIAS2': 'alias2_new', 'ALIAS3': 'alias3'}

#     # assert False, "WIPP"
