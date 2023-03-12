"""
Tree mixins
"""


# Imports
################################################################

import inspect
from typing import MutableSequence, MutableSet, MutableMapping

from pprint import pprint, pformat


from .. import errors
from ..lib.utils import to_json, from_json, to_yaml, from_yaml, import_from_str

from ..nodes2 import Node
from ..common import CaframNode

from .base import PayloadMixin, NodePayload
from .hier import HierParentMixin, HierChildrenMixin
from .path import PathMixin


from . import LoadingOrder


# Parent exceptions
class ConfMixinException(errors.CaframMixinException):
    """Mixin Exceptions"""


# Child exceptions
class InvalidConfig(ConfMixinException):
    """When the provided configuration is invalid"""


class ExpectedList(ConfMixinException):
    """A list was expected"""


class ExpectedDict(ConfMixinException):
    """A dict was expected"""


class ExpectedListOrDict(ConfMixinException):
    """A list or a dict was expected"""


# Conf mixins (Composed classes)
################################################################


class ConfMixinGroup(PayloadMixin, HierParentMixin):
    "Conf mixin that group all ConfMixins"

    mixin_order = LoadingOrder.NORMAL


class ConfMixin(ConfMixinGroup):
    "Conf mixin that manage a basic serializable value"

    # name = "conf"
    # key = "conf"
    mixin_key = "conf"

    index = None
    _param_index = "index"

    # pylint: disable=line-too-long
    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: ConfMixin",
        "description": "ConfMixin Configuration",
        "default": {},
        "properties": {
            "index": {
                "title": "Index",
                "description": "Name of the index key",
                "default": index,
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

    # @mixin_init
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # self._super__init__(super(), *args, **kwargs)

        # Value check
        value = self.get_value()
        valid = (str, bool, dict, list, int, float, type(None))
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


# Simple value wrappers
################################################################


class ConfPathMixin(ConfMixin, PathMixin):
    "Conf mixin that manage a basic serializable value"

    _param_raw = "payload"

    # def __init__(self, *args, **kwargs):
    #     # super().__init__(*args, **kwargs)

    #     self._super__init__(super(), *args, **kwargs)

    # print ("____> ConfigPath")
    # pprint (kwargs)
    # pprint (self.__dict__)


# Containers
################################################################


class _ConfContainerMixin(HierChildrenMixin, ConfMixin):
    "Conf mixin that manage a nested serializable values"

    children = True

    # Because they create children
    mixin_order = LoadingOrder.POST

    # pylint: disable=line-too-long
    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: PayloadContainerMixin",
        "description": "PayloadContainer Configuration",
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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._log.warning(f"HELLO WORLD LIST, {self}, {self.get_logger_name()}")
    #     print(f"HELLO WORLD LIST, {self}, {self.get_logger_name()}")

    def set_default(self, payload):
        "Update defaults"

        payload = payload or []
        if not isinstance(payload, list):
            msg = (
                f"Invalid children config for {self}. "
                "Expected a List, got "
                f"{type(payload).__name__}: {payload}"
            )
            raise ExpectedList(msg)

        default = list(self.default)
        if not isinstance(default, list):
            # pprint(self.__dict__)
            msg = (
                f"Invalid default config for {self}. "
                "Expected a List, got "
                f"{type(payload).__name__}: {payload}"
            )
            raise ExpectedList(msg)

        # ret = default
        # ret.update(payload)

        return payload or default

    def _parse_children(self):

        # Get data
        value = self.get_value()
        # self._children = []
        children_conf = self.children

        if children_conf is False:
            pass
        elif children_conf is None:
            self._log.debug("Children configs is None")
            for child_key, child_value in enumerate(value):
                self.add_child(child_value)
                self._log.info(
                    f"Child '{child_key}' config is native {type(child_value)}"
                )

        elif children_conf:

            default_cls = children_conf if inspect.isclass(children_conf) else None

            self._log.debug("Children configs is automatic")
            for child_key, child_value in enumerate(value):

                if default_cls is None:
                    child_cls = map_node_class(child_value)
                else:
                    child_cls = default_cls

                if child_cls is None:
                    child = child_value
                else:
                    child_args = {
                        # self._param_ident_prefix: self.get_ident(),
                        # self._param_ident: f"{child_key}",
                        self._param_index: child_key,
                        self._param__payload: child_value,
                        self._param__parent: self,
                    }
                    msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                    self._log.info(msg)
                    # print ("CREATE LIST CHILD", child_args)

                    assert issubclass(child_cls, CaframNode)
                    child = child_cls(self, **child_args)

                self.add_child(child)
                # self.add_child(child_value)
                self._log.debug(f"Child '{child_key}' config is {child_cls}")
        else:
            msg = (
                f"Invalid children config for {self}. "
                "Expected one of bool,None,str,MixinClass , got "
                f"{type(children_conf).__name__}: {children_conf}"
            )

            raise InvalidConfig(msg)


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
            msg = (
                f"Invalid payload config for {self}. "
                "Expected a Dict, got "
                f"{type(payload).__name__}: {payload}"
            )
            msg = f"Expected a dict for '{self.get_ident()}', got {type(payload)}: {payload}"
            raise ExpectedDict(msg)

        # Fetch default value
        default = dict(self.default) or {}
        if not isinstance(default, dict):
            msg = (
                f"Invalid default config for {self}. "
                "Expected a Dict, got "
                f"{type(default).__name__}: {default}"
            )
            # msg = f"Expected a dict for '{self.get_ident()}', got {type(default)}: {default}"
            raise ExpectedDict(msg)

        # Update from default dict
        ret = default
        ret.update(payload)

        return ret

    def _parse_children_config(self, children_conf, value):
        "Only simple configs are allowed here"

        # Value based config
        children_list = []

        default_conf = {
            "key": None,
            "cls": None,
            "order": None,
        }

        if children_conf is False:
            pass

        elif children_conf is True:
            self._log.debug("Children configs is automatic")

            child_order = 0
            for child_key, child_value in value.items():
                child_order += 1
                child_cls = map_node_class(child_value)

                conf = dict(default_conf)
                conf["order"] = child_order * 10
                conf["key"] = child_key
                conf["cls"] = child_cls
                conf = {
                    "order": child_order * 10,
                    "key": child_key,
                    "cls": child_cls,
                }
                children_list.append(conf)

                self._log.debug(f"Child '{child_key}' config is {child_cls}")

        elif children_conf is None:
            self._log.debug("Children configs is None")

            for idx, child_key in enumerate(value.keys(), start=1):
                conf = {
                    "order": idx * 10,
                    "key": child_key,
                    "cls": None,
                }
                children_list.append(conf)

                self._log.debug(f"Child '{child_key}' config is native/forwarded")

        else:

            if isinstance(children_conf, str):
                children_conf = import_from_str(children_conf)

            if inspect.isclass(children_conf) and issubclass(children_conf, Node):
                self._log.debug(f"Children configs is {children_conf}")

                for idx, child_key in enumerate(value.keys(), start=1):
                    conf = {
                        "order": idx * 10,
                        "key": child_key,
                        "cls": children_conf,
                    }
                    children_list.append(conf)

                    self._log.debug(
                        f"Child '{child_key}' config is default mapped to {children_conf}"
                    )

            else:
                print("YOOOOO", str(self.get_ctrl()))
                msg = (
                    f"Invalid children config for {self}, "
                    "expected one of bool,None,str,MixinClass, got "
                    f"{type(children_conf).__name__}: {children_conf}"
                )
                raise InvalidConfig(msg)

        return children_list

    def _parse_children(self):

        # Get data
        value = self.get_value() or {}
        # Parse children
        children_list = self._parse_children_config(self.children, value)

        # Get load order
        load_order = sorted(children_list, key=lambda item: item["order"])

        # Instanciate children
        for child_def in load_order:

            child_key = child_def["key"]
            child_cls = child_def["cls"]

            child_value = value.get(child_key)
            if child_cls is None:
                _type = type(child_value).__name__
                self._log.info(
                    f"Create native child '{child_key}': {_type}({child_value})"
                )
                child = child_value

            else:
                child_args = {
                    # self._param_ident_prefix: self.get_ident(),
                    # self._param_ident: f"{child_key}",
                    self._param_index: child_key,
                    self._param__payload: child_value,
                    self._param__parent: self,
                }

                self._log.info(f"Create Node child '{child_key}': {child_cls.__name__}")
                assert issubclass(child_cls, CaframNode)
                child = child_cls(self, **child_args)

            self.add_child(child, index=child_key, alias=True)


class ConfOrderedMixin(ConfDictMixin):
    "Conf mixin that manage a serializable and ordered dict of values"

    default = {}

    def _parse_children_config(self, children_conf, value):
        "Parse complex config"

        children_list = []
        if isinstance(children_conf, dict):
            child_index = 0

            for child_index, child_key in enumerate(children_conf, start=1):

                child_def = children_conf[child_key]
                index = child_index * 10
                conf = {
                    "key": child_key,
                    "cls": None,
                    "order": index,
                }

                if isinstance(child_def, dict):
                    child_def.pop("key", None)
                    conf.update(child_def)
                elif isinstance(child_def, str):
                    conf["cls"] = import_from_str(child_def)
                else:
                    conf["cls"] = child_def

                children_list.append(conf)

        elif isinstance(children_conf, list):
            for child_index, child_def in enumerate(children_conf, start=1):

                index = child_index * 10
                conf = {
                    "key": None,
                    "cls": None,
                    "order": index,
                }

                if isinstance(child_def, dict):
                    child_def.pop("order", None)
                    conf.update(child_def)
                elif isinstance(child_def, str):
                    conf["cls"] = import_from_str(child_def)
                else:
                    conf["cls"] = child_def

                children_list.append(conf)

        else:
            msg = (
                f"Invalid children config for {self}. "
                "You may want to use 'ConfDictMixin' instead. "
                "Expected a List or Dict, got: "
                f"{type(children_conf).__name__}: {children_conf}"
            )

            raise ExpectedListOrDict(msg)

        return children_list


# Nodes helpers
################################################################


class NodeConf(NodePayload):
    "NodeConf"

    _node_conf = [{"mixin": ConfMixin}]


class NodeConfDict(NodeConf):
    "NodeConfDict"

    _node_conf = [{"mixin": ConfDictMixin}]


class NodeConfList(NodeConf):
    "NodeConfList"

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
