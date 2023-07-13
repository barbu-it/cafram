"""
Tree mixins
"""


# Imports
################################################################

import inspect
from pprint import pformat, pprint
from typing import MutableMapping, MutableSequence, MutableSet

from ... import errors
from ...common import CaframNode
from ...lib.utils import (
    from_json,
    from_yaml,
    import_module,
    read_file,
    to_json,
    to_yaml,
)
from . import BaseMixin, LoadingOrder
from .base import PayloadMixin
from .hier import HierChildrenMixin, HierParentMixin
from .path import FilePathMixin, PathFinderMixin, PathMixin


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


class ExpectedNodeClass(ConfMixinException):
    """Expected a Node Class"""


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

    # Index management
    index = None
    mixin_param__index = "index"
    _index_enable = True

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
                "default": None,
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

        child_node_cls = self.node_ctrl._obj.__class__

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

                child_args = {}
                if default_cls is None:
                    # child_cls = map_node_class(child_value)

                    child_cls = child_node_cls
                    child_args = map_node_class_full2(child_value, self.mixin_key)

                else:
                    child_cls = default_cls

                if child_cls is None:
                    child = child_value
                else:
                    child_args.update(
                        {
                            # self.mixin_param__ident_prefix: self.get_ident(),
                            # self.mixin_param__ident: f"{child_key}",
                            # self.mixin_param__index: child_key,
                            # "mixin_index": child_key,
                            self.mixin_param___payload: child_value,
                            self.mixin_param___parent: self,
                            # Forward config
                            # print ("LEVEL CAHNGE", self._obj_logger_indent, "=>", self._obj_logger_indent +1)
                            # "node_logger_indent": self._obj_logger_indent +1,
                        }
                    )

                    if self._index_enable == True:
                        child_args[self.mixin_param__index] = child_key

                    msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                    self._log.info(msg)
                    # print ("CREATE LIST CHILD", child_args)

                    # Unecessary??? TODO: assert issubclass(child_cls, CaframNode)
                    child = child_cls(self, **child_args)

                self.add_child(child)
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
    """Conf mixin that manage a unknown serializable dict of values

    :Usecases:

        - For Dicts only
        - Unknown children of same types: Number of children is unknown, but with similar type.
        - Homogneous children:
            - For keyed dicts (Ie: dict[$NAME] = {conf1, conf2})
        - Heterogenous children: AUTO/NATIVE
            - For mixed dicts (Ie: dict("config1": True, "path": "/", value=123) )
        - Poor children configuration
            - Children processing order can't be modified

    :Explanations:

        children_config:
            - False/"NONE": No children at all
            - None/"AUTO": Create Node children for list and dicts (default). Skip all others!
            - True/"NATIVE": Create Native children for all items. Accept any type!
            - Node based class (cls/str): Apply a Node based class on the item, via payload arg.

            New (Future settings example):
            - none                  : No children
            - containers_only       : Create children for list and dicts (default)
            - leaf_only             : Create children for anything but list and dicts
            - all                   : Create children for all
            - cls_name (str)        : Create children from class cls()
            - cls(Node)             : Create children from class cls()
            - func(str)             : Custom function that execute object method
            - func(dictconf)        : Custom function that accept item info and return a value


    :Examples:

        To statically configure the func method:

        >>> @newNode()
        >>> @addMixin("DictConfMixin", "conf",
            # children = lambda (dict): return Node()
            # children = "self._node_mixin__conf_children"
            )
        >>> class MyClass():
        >>>
        >>> @staticmethod
        >>>    def _node_mixin__conf_children(dictconf):
        >>>        return Node()
    """

    default = {}
    _children: dict = {}

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
        prefix = self.node_ctrl._obj_attr
        child_node_cls = self.node_ctrl._obj.__class__
        default_conf = {
            "key": None,
            "cls": None,
            "order": None,
        }

        if children_conf is False or children_conf == "NONE":
            pass

        elif children_conf is True or children_conf == "AUTO":
            self._log.debug("Children configs is automatic")

            child_order = 0
            for child_key, child_value in value.items():
                child_order += 1

                child_cls = child_node_cls
                params = map_node_class_full2(child_value, self.mixin_key)

                conf = dict(default_conf)
                conf = {
                    "order": child_order * 10,
                    "key": child_key,
                    "cls": child_cls,
                    "params": params,
                }

                children_list.append(conf)

                self._log.debug(f"Child '{child_key}' config is {child_cls}")

        elif children_conf is None or children_conf == "NATIVE":
            self._log.debug("Children configs is None")

            for idx, child_key in enumerate(value.keys(), start=1):
                conf = {
                    "order": idx * 10,
                    "key": child_key,
                    "cls": None,
                }
                children_list.append(conf)

                self._log.debug(f"Child '{child_key}' config is native/forwarded")

        else:  # Or: children_conf == cls

            if isinstance(children_conf, str):
                children_conf = import_module(children_conf)

            if inspect.isclass(children_conf):

                children_params = {}
                if issubclass(children_conf, BaseMixin):
                    children_params = {
                        "obj_mixins": {
                            self.mixin_key: {
                                "mixin": children_conf,
                            },
                        }
                    }
                    children_conf = child_node_cls

                if not hasattr(children_conf, prefix):
                    msg = (
                        f"Invalid children config for {self}, "
                        "expected to be a children of CaframNode of BaseMixin Class, got: "
                        f"{children_conf} => {type(children_conf).__name__}: {children_conf.__mro__}"
                    )
                    raise InvalidConfig(msg)

                self._log.debug(f"Children configs is {children_conf}")

                for idx, child_key in enumerate(value.keys(), start=1):
                    conf = {
                        "order": idx * 10,
                        "key": child_key,
                        "cls": children_conf,
                        "params": children_params,
                    }
                    children_list.append(conf)

                    self._log.debug(
                        f"Child '{child_key}' config is default mapped to {children_conf}"
                    )

            else:

                msg = (
                    f"Invalid children config for {self}, "
                    "expected one of bool,None,str,CaframNode, got "
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

        # print ("CHILDREN LIST")
        # pprint (children_list)

        # Instanciate children
        for child_def in load_order:

            child_key = child_def["key"]
            child_cls = child_def["cls"]
            child_params = dict(child_def.get("params", {}))

            child_value = value.get(child_key)
            if child_cls is None:
                _type = type(child_value).__name__
                self._log.info(
                    f"Create native child '{child_key}': {_type}({child_value})"
                )
                child = child_value

            else:
                prefix = self.node_ctrl._obj_attr

                child_args = child_params
                child_args.update(
                    {
                        self.mixin_param___payload: child_value,
                        self.mixin_param___parent: self,
                        "name": child_key,
                    }
                )
                if self._index_enable == True:
                    child_args[self.mixin_param__index] = child_key

                self._log.info(
                    f"Create Node child '{child_key}': {child_cls.__name__} => {child_args}"
                )

                if not issubclass(child_cls, (CaframNode)) and not hasattr(
                    child_cls, prefix
                ):
                    msg = (
                        f"Invalid children config for {self}. "
                        "Expected a Node Class, got: "
                        f"{child_cls.__name__}: {child_cls}"
                    )
                    raise ExpectedNodeClass(msg)
                child = child_cls(self, **child_args)

            self.add_child(child, index=child_key, alias=True)


class ConfOrderedMixin(ConfDictMixin):
    """Conf mixin that manage a serializable and ordered dict of values

    :raises ExpectedListOrDict: _description_

    :return: ConfOrderedMixin instance
    :rtype: ConfOrderedMixin

    :Explanations:

    :Usecases:

        * For Dicts only
        * Known children of different types: All children are explicitely defined
        * To represent complex objects that have to process things in a certain order
            * Ie: Your top app will want to read top level concept and deep done to smaller components,
            * later componants may depends on top level items.
        * Advanced children configuration
            * Children processing order can be defined in 2 ways/format


    :Examples:

        Code Format as list of dicts

        >>> children = [
            {
                "key": "KEY2",
                "cls": Node,
            },
            {
                "key": "KEY1",
                "cls": Node,
            },
        ]

        Code Format as dict

        >>> children = {
            "KEY2": {
                "cls": Node,
                "order": 20,
            },
            "KEY1": {
                "cls": Node,
                "order": 50,
            },
        }

    """

    default = {}
    # _index_enable = False

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
                    conf["cls"] = import_module(child_def)
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
                    conf["cls"] = import_module(child_def)
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


# Simple value wrappers
################################################################


class ConfPathMixin(PathMixin, ConfMixin):
    "Conf mixin that manage a basic serializable value"

    # OLD: mixin_param__raw = "payload"
    mixin_param__payload = "raw"


class ConfFileMixin(PathFinderMixin, ConfDictMixin):
    "Conf mixin that manage a basic serializable value"

    # OLD: mixin_param__raw = "payload"
    mixin_param__payload = "raw"

    conf_format = None

    mapping_parser = {
        ".yaml": from_yaml,
        ".yml": from_yaml,
        ".json": from_json,
        # toml
        # ini
    }

    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)

        PathFinderMixin.__init__(self, *args, **kwargs)

        # print("INIT CONF FILEMIXIN")
        fpath = self.get_path()
        # pprint (fpath)
        content = read_file(fpath)

        # print (content)
        conf_format = self.conf_format or self.get_ext()
        # print ("FORMAT", conf_format)

        if conf_format not in self.mapping_parser:
            msg = "Missing format support"
            raise Exception(msg)

        conv = self.mapping_parser[conf_format]

        ret = conv(content)
        # print (to_json(dict(ret)))
        # print (to_yaml(ret))

        # self._payload = ret
        # self.set_value(self._payload)
        # kwargs["payload"] = ret
        kwargs[self.mixin_param___payload] = dict(ret)
        # kwargs[self.mixin_param___children] = self.children
        # print("PARENT CALL")
        # pprint(kwargs)

        # print("INSERT CONFIG INTO PAYLOAD")
        ConfDictMixin.__init__(self, *args, **kwargs)


# Nodes helpers
################################################################


# class NodeConf(NodePayload):
#     "NodeConf"

#     # _node_conf = [{"mixin": ConfMixin}]
#     # __node__mixins__ = [{"mixin": ConfMixin}]
#     # _obj_mixins = [{"mixin": ConfMixin}]
#     #__node__obj_mixins = [{"mixin": ConfMixin}]
#     #__node___mixins__ = [{"mixin": ConfMixin}]
#     __node___mixins__ = [{"mixin": ConfMixin}]
#     # NEW: {prefix}_mixins__  , prefix =__node__

# class NodeConfDict(NodeConf):
#     "NodeConfDict"

#     # _node_conf = [{"mixin": ConfDictMixin}]
#     __node___mixins__ = [{"mixin": ConfDictMixin}]


# class NodeConfList(NodeConf):
#     "NodeConfList"

#     # _node_conf = [{"mixin": ConfListMixin}]
#     __node___mixins__ = [{"mixin": ConfListMixin}]


# Function helpers
################################################################


def map_node_class_full2(payload, mixin_key):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        mixin_cls = ConfDictMixin
    elif isinstance(payload, list):
        mixin_cls = ConfListMixin
    else:
        mixin_cls = ConfMixin

    params = {
        "obj_mixins": {
            mixin_key: {
                "mixin": mixin_cls,
            },
        }
    }

    return params


def map_node_class2(payload, mixin_key):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        mixin_cls = ConfDictMixin
    elif isinstance(payload, list):
        mixin_cls = ConfListMixin
    else:
        mixin_cls = None

    params = {
        "obj_mixins": {
            mixin_key: {
                "mixin": mixin_cls,
            },
        }
    }

    return params
