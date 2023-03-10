"""
Tree mixins
"""

# Imports
################################################################

import inspect
import json
from typing import MutableSequence, MutableSet, MutableMapping

from pprint import pprint, pformat


from .. import errors
from ..utils import to_json, from_json, to_yaml, from_yaml
#from ..nodes import Node
from ..nodes2 import Node
from ..common import CaframMixin, CaframNode

from .base import PayloadMixin, NodePayload, MapAttrMixin
from .hier import HierParentMixin, HierChildrenMixin



# Conf mixins (Composed classes)
################################################################


class ConfMixinGroup(PayloadMixin, HierParentMixin):
    "Conf mixin that group all ConfMixins"


class ConfMixin(ConfMixinGroup):
    "Conf mixin that manage a basic serializable value"

    #name = "conf"
    #key = "conf"
    mixin_key = "conf"

    index = None
    _param_index = "index"

    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: PayloadMixin",
        "description": "PayloadMixin Configuration",
        "default": {},
        "properties": {
            "mixin_key": {
                "title": "Mixin key",
                "description": "Name of the mixin. Does not keep alias if key is set to `None` or starting with a `.` (dot)",
                "default": mixin_key,
                "oneOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
        },
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Value check
        value = self.get_value()
        valid = (str, bool, dict, list, type(None))
        if not isinstance(value, valid):
            assert False, f"TYPE ERROR, got: {type(value)}"

    # Converter methods
    # -----------------
    def to_json(self):
        "Export value from json string"
        return to_json(self.get_value())

    def from_json(self, payload):
        "Import value from json string"
        self.set_value(from_json(payload))

    def to_yaml(self):
        "Export value from yaml string"
        return to_yaml(self.get_value())

    def from_yaml(self, payload):
        "Import value from yaml string"
        self.set_value(from_yaml(payload))

    # Additional methods
    # -----------------

    def is_mutable(self):
        "Check if value is mutable or not"
        payload = self._payload
        return issubclass(type(payload), (MutableSequence, MutableSet, MutableMapping))
    
    def get_index(self):
        "Check if value is mutable or not"
        return self.index


# Containers
################################################################


class _ConfContainerMixin(HierChildrenMixin, ConfMixin):
    "Conf mixin that manage a nested serializable values"

    children = True

    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: PayloadMixin",
        "description": "PayloadMixin Configuration",
        "default": {},
        "properties": {
            "children": {
                "title": "Children configuration",
                "description": "`False` does not generate children, `null` does generate 1 level children, `True` generate recursively all children. A `dict` can also be provided in `ConfDictMixin` case",
                "default": children,
                "oneOf": [
                    {
                        "description": "Generate recursively children containers if set to `True`, does not generate children otherwise",
                        "type": "boolean",
                    },
                    {
                        "description": "Generate only first children level from types",
                        "type": "null",
                    },
                    {
                        "description": "Generate types on attribute (ConfDictMixin only)",
                        "type": "dict",
                    },
                ],
            },
        },
    }

    # def get_name(self):
    #     return self.index or super().get_name()


# Dict Containers
################################################################


class ConfDictMixin(_ConfContainerMixin):
    "Conf mixin that manage a serializable dict of values"

    default = {}
    _children = {}

    def set_default(self, payload):
        "Update defaults"

        # Validate payload type
        payload = payload or {}
        if not isinstance(payload, dict):
            msg = f"Expected a dict, got {type(payload)}: {payload}"
            raise errors.DictExpected(msg)

        # Fetch default value
        default = dict(self.default) or {}
        if not isinstance(default, dict):
            msg = f"Expected a dict, got {type(default)}: {default}"
            raise errors.DictExpected(msg)

        # Update from default dict
        ret = default
        ret.update(payload)

        return ret



    def _parse_children(self):

        # Get data
        value = self.get_value() or {}

        # Parse children
        children_conf = self.children
        children_map = {}
        if children_conf is False:
            pass
        elif children_conf is True:
            self._log.info(f"Children configs is automatic")
            for child_key, child_value in value.items():
                child_cls = map_node_class(child_value)
                children_map[child_key] = child_cls
                self._log.info(f"Child '{child_key}' config is {child_cls}")
        elif children_conf is None:
            self._log.info(f"Children configs is None")
            for child_key, child_value in value.items():
                children_map[child_key] = None
                self._log.info(f"Child '{child_key}' config is native {type(child_value)}")
        elif isinstance(children_conf, dict):
            self._log.info(f"Children configs is Dict")
            for child_key, child_cls in children_conf.items():
                children_map[child_key] = child_cls
                self._log.info(f"Child '{child_key}' config is mapped to {child_cls}")
        elif issubclass(children_conf, Node):
            self._log.info(f"Children configs is {children_conf}")
            for child_key, child_cls in value.items():
                children_map[child_key] = children_conf
                self._log.info(f"Child '{child_key}' config is default mapped to {child_cls}")
        else:
            msg = f"Invalid configuration for Dict children: {children_conf}"
            raise errors.CaframException(msg)

        # Instanciate children
        for child_key, child_cls in children_map.items():

            child_value = value.get(child_key)
            if child_cls is None:
                self._log.info(f"Create native child '{child_key}': {type(child_value).__name__}({child_value})")
                child = child_value
            else:
                child_args = {
                    self._param_ident_prefix: self.get_ident(),
                    self._param_ident: f"{child_key}",

                    self._param_index: child_key,
                    self._param__payload: child_value,
                    self._param__parent: self,
                }

                self._log.info(f"Create Node child '{child_key}': {child_cls.__name__}")
                assert issubclass(child_cls, CaframNode)
                child = child_cls(self, **child_args)

            self.add_child(child, index=child_key, alias=True)


# List Container
################################################################


class ConfListMixin(_ConfContainerMixin):
    """Conf mixin that manage a serializable list of values

    Usage:
      ConfListMixin(node_ctrl, mixin_conf=None)
      ConfListMixin(node_ctrl, mixin_conf=[ConfDictMixin])

    """

    default = []
    _children = []

    def set_default(self, payload):
        "Update defaults"

        payload = payload or []
        if not isinstance(payload, list):
            msg = f"Got {type(payload)} instead: {payload}"
            raise errors.ListExpected(msg)

        default = list(self.default)
        if not isinstance(default, list):
            pprint (self.__dict__)
            msg = f"Got {type(default)} instead: {default}"
            raise errors.ListExpected(msg)

        # ret = default
        # ret.update(payload)

        return payload or default


    def _parse_children(self):

        # Get data
        value = self.get_value()
        #self._children = []
        children_conf = self.children
        
        if children_conf is False:
            pass
        elif children_conf is None:
            self._log.info(f"Children configs is None")
            for child_key, child_value in enumerate(value):
                self.add_child(child_value)
                self._log.info(f"Child '{child_key}' config is native {type(child_value)}")

        elif children_conf:

            # param_payload = 
            # param_parent = 
            # param_ident = self._param_ident
            # param_ident_prefix = self._param_ident_prefix
            # #param_ident_suffix = self._param_ident_suffix
            # param_index = self._param_index

            default_cls = children_conf if inspect.isclass(children_conf) else None

            self._log.info(f"Children configs is automatic")
            for child_key, child_value in enumerate(value):
                
                if default_cls is None:
                    child_cls = map_node_class(child_value)
                else:
                    child_cls = default_cls
                    
                if child_cls is None:
                    child = child_value
                else:
                    child_args = {
                        self._param_ident_prefix: self.get_ident(),
                        self._param_ident: f"{child_key}",

                        self._param_index: child_key,

                        self._param__payload: child_value,
                        self._param__parent: self,
                    }
                    msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                    self._log.info(msg)
                    #print ("CREATE LIST CHILD", child_args)

                    assert issubclass(child_cls, CaframNode)
                    child = child_cls(self, **child_args)

                self.add_child(child_value)
                self._log.info(f"Child '{child_key}' config is {child_cls}")
        else:            
            msg = f"Invalid configuration for children: {children_conf}"
            raise errors.CaframException(msg)


# Nodes helpers
################################################################


class NodeConf(NodePayload):

    _node_conf = [{"mixin": ConfMixin}]


class NodeConfDict(NodeConf):

    _node_conf = [{"mixin": ConfDictMixin}]


class NodeConfList(NodeConf):

    _node_conf = [{"mixin": ConfListMixin}]


# Function helpers
################################################################


def map_node_class_full(payload):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        return NodeConfDict
    if isinstance(payload, list):
        # return NodeConf
        # TEMPORARY
        return NodeConfList

    return NodeConf


def map_node_class(payload):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        return NodeConfDict
    if isinstance(payload, list):
        # return None
        return NodeConfList

    return None
