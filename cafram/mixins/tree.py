"""
Tree mixins
"""

# Imports
################################################################

import json
import logging
from typing import MutableSequence, MutableSet, MutableMapping

from pprint import pprint, pformat


from .. import errors
from ..utils import to_json, from_json, to_yaml, from_yaml
from ..nodes import Node
from ..common import CaframMixin, CaframNode

from .base import PayloadMixin, NodePayload, MapAttrMixin
from .hier import HierParentMixin, HierChildrenMixin

log = logging.getLogger(__name__)


# Conf mixins (Composed classes)
################################################################


class ConfMixinGroup(PayloadMixin, HierParentMixin):
    "Conf mixin that group all ConfMixins"


class ConfMixin(ConfMixinGroup):
    "Conf mixin that manage a basic serializable value"

    name = "conf"

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
            "name": {
                "title": "Mixin name",
                "description": "Name of the mixin. Does not keep alias if name is set to `None` or starting with a `.` (dot)",
                "default": name,
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

    def _init(self, **kwargs):

        super()._init(**kwargs)

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


# Dict Containers
################################################################


class ConfDictMixin(_ConfContainerMixin):
    "Conf mixin that manage a serializable dict of values"

    def _parse_children(self):

        # Get data
        value = self.get_value() or {}
        self._children = {}

        # Sanity checks
        assert isinstance(value, dict), f"Got: {value}"

        # Parse children
        children_conf = self.children
        children_map = {}
        if children_conf is True:
            log.info(f"Children configs is automatic")
            for child_key, child_value in value.items():
                child_cls = map_node_class(child_value)
                children_map[child_key] = child_cls
                log.info(f"Child '{child_key}' config is {child_cls}")
        elif children_conf is None:
            log.info(f"Children configs is None")
            for child_key, child_value in value.items():
                children_map[child_key] = None
                log.info(f"Child '{child_key}' config is native {type(child_value)}")
        elif children_conf is False:
            pass
        else:
            msg = f"Invalid configuration for children: {children_conf}"
            raise errors.CaframException(msg)

        # Instanciate children
        name_param = self.name_param
        parent_param = self.parent_param
        for child_key, child_cls in children_map.items():

            child_value = value.get(child_key)
            if child_cls is None:
                child = child_value
                msg = f"Create child '{child_key}': {type(child_value).__name__}({child_value})"
                log.info(msg)
                # print (msg)
            else:
                child_args = {
                    name_param: child_value,
                    parent_param: self,
                }
                msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                log.info(msg)
                # print (msg)

                assert issubclass(child_cls, CaframNode)
                child = child_cls(self, **child_args)
                # child = self.create_child(child_cls, child_value, child_key=child_key, **child_args)

            self.add_child(child, index=child_key, alias=True)


# List Container
################################################################


class ConfListMixin(_ConfContainerMixin):
    """Conf mixin that manage a serializable list of values

    Usage:
      ConfListMixin(node_ctrl, mixin_conf=None)
      ConfListMixin(node_ctrl, mixin_conf=[ConfDictMixin])

    """

    def _parse_children(self):

        # Get data
        value = self.get_value() or []
        self._children = []

        # Sanity checks
        assert isinstance(value, list), f"Got: {value}"

        children_conf = self.children
        if children_conf is True:

            name_param = self.name_param
            parent_param = self.parent_param

            log.info(f"Children configs is automatic")
            for child_key, child_value in enumerate(value):
                child_cls = map_node_class(child_value)
                if child_cls is None:
                    child = child_value
                else:
                    child_args = {
                        name_param: child_value,
                        parent_param: self,
                    }
                    msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                    log.info(msg)
                    # print (msg)

                    assert issubclass(child_cls, CaframNode)
                    child = child_cls(self, **child_args)

                self.add_child(child_value)
                log.info(f"Child '{child_key}' config is {child_cls}")
        elif children_conf is None:
            log.info(f"Children configs is None")
            for child_key, child_value in enumerate(value):
                # children_map[child_key] = None
                self.add_child(child_value)
                log.info(f"Child '{child_key}' config is native {type(child_value)}")
        elif children_conf is False:
            pass
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
