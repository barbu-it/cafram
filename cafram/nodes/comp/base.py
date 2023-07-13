"""
Base mixins
"""

import copy
import logging
import traceback
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

from ...common import CaframObj

# from ..nodes import Node
# from ...lib import logger
from ...nodes import Node
from .. import errors
from . import BaseMixin, LoadingOrder

# log = logging.getLogger(__name__)


# def add_positional_arg(func):
#     def wrapper(*args, **kwargs):
#         args = list(args)
#         args.insert(1, 'extra_arg')
#         return func(*args, **kwargs)
#     return wrapper


# Core Mixins
################################################################


# Can't work, because we can't live patch instance dunder
# class ObjForwardMixin(BaseMixin):
#     "Object forwarder Mixin"

#     # key = "ident"
#     mixin_key = None

#     # Config
#     forward_attr = True
#     forward_item = True

#     forward_len = True
#     forward_iter = True

#     forward_call = True


#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         obj = self.get_obj()


class IdentMixin(BaseMixin):
    "Ident Mixin"

    # key = "ident"
    mixin_key = "ident"

    # Config
    ident = None
    ident_suffix = None
    ident_prefix = None

    # Parameters
    mixin_param__ident = "ident"
    mixin_param__ident_suffix = "ident_suffix"
    mixin_param__ident_prefix = "ident_prefix"

    def _get_name_target(self):
        "Try to catch CaframObj reference for naming, fall back on current class"

        target = self

        # obj = self.node_ctrl._obj
        obj = self.get_obj()
        if issubclass(type(obj), CaframObj):
            target = obj

        return target

    def get_ident_name(self):
        "Return the last part of the ident, including suffix"

        ident = self.ident
        if not ident:
            target = self._get_name_target()
            ident = target.get_name()

        suffix = self.ident_suffix
        if suffix:
            ident += str(suffix)
        return ident

    def get_ident_prefix(self):
        "Return the first part of the ident"

        prefix = self.ident_prefix
        if not prefix:
            target = self._get_name_target()
            prefix = target.get_prefix()
        return prefix

    def get_ident(self):
        "Return the full ident"
        return ".".join([self.get_ident_prefix(), self.get_ident_name()])


# class PayloadMixin(IdentMixin):
class PayloadMixin(BaseMixin):
    "Payload Mixin"

    mixin_key = "payload"

    _payload: Any = None
    mixin_param___payload = "payload"

    mixin_alias__value = "value"

    default: Any = None
    payload_schema = False

    # pylint: disable=line-too-long
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
            # "name_param": {
            #     "title": "Mixin name parameter",
            #     "description": "Name of the parameter to load name from",
            #     "default": name_param,
            # },
            "value_alias": {
                "title": "Value alias name",
                "description": "Name of the alias to retrieve value. Absent if set to None",
                "default": mixin_alias__value,
                "oneOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
            "payload_schema": {
                "title": "Payload schema",
                "description": "Json schema that must validate payload",
                "default": payload_schema,
                "oneOf": [
                    {
                        "title": "JSONschema definition",
                        "type": "dict",
                    },
                    {
                        "title": "Disabled",
                        "type": "null",
                    },
                ],
            },
        },
    }

    # def __repr__(self):
    #     if hasattr(self, "_value"):
    #         return self.get_value()
    #     return str(self)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._super__init__(super(), *args, **kwargs)

        # print("PayloadMixin INIT payload", self._payload)
        # print("PayloadMixin INIT params", args, kwargs)
        self._value = None
        self.set_value(self._payload)
        # self._register_alias()

        # self._aliases = {
        #     ""
        # }

        self._register_alias("value", self.get_value())

    # def _register_alias(self):
    #     if self.value_alias:
    #         self.node_ctrl.alias_register()

    # Generic value handler
    # ---------------------
    @property
    def value(self):
        "Manage payload value"
        return self.get_value()

    @value.setter
    def value(self, value):
        self.set_value(value)

    @value.deleter
    def value(self):
        self.set_value(None)

    def get_value(self):
        "Get a value"
        return self._value

    def set_value(self, value):
        "Set a value"

        conf = self.preparse(value)
        conf = self.set_default(conf)
        conf = self.validate(conf)
        conf = self.transform(conf)
        self._value = conf
        return self._value

    # def __repr__(self):

    #     prefix = self.get_ident()
    #     suffix = f"[{self.mixin_key}]{type(self).__name__}"
    #     return f"<{prefix}{suffix}>"

    # Transformers/Validators
    # ---------------------

    def set_default(self, payload):
        "Set default if value is null"

        # TODO: This does not allow to determine in advance the state of default
        return payload or copy.copy(self.default)

    def preparse(self, payload):
        "Pre parse payload before schema validation"
        return payload

    def transform(self, payload):
        "Transform payload before"
        return payload

    def validate(self, payload):
        "Validate config against json schema"

        schema = self.payload_schema
        if isinstance(schema, dict):
            valid = True
            if not valid:
                raise errors.CaframException(f"Can't validate: {payload}")

        return payload

    def schema(self):
        "Return json schema for payload"
        return self.payload_schema


class NodePayload(Node):
    "Payload Node"

    # _node_conf = [{"mixin": PayloadMixin}]
    __node___mixins__ = [{"mixin": PayloadMixin}]


# Utils Mixins
################################################################


class LoggerMixin(BaseMixin):
    "Logger Mixin"

    # name = "logger"
    # key = "logger"

    mixin_order = LoadingOrder.PRE
    mixin_key = "logger"

    index = None
    mixin_param__index = "index"

    _logger = None
    mixin_param___logger = "logger"

    # Logger instance
    log = None

    # Logger config
    # log_alias = "log"
    # _alias_log = "log"
    mixin_alias__log = "log"

    # Logger level: Logging level, can be object, string or number
    log_level = None
    mixin_param__log_level = "logger_level"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init logger if not provided in params
        self.set_logger(logger=self._logger)
        self.set_level()
        self._register_alias("log", self.log)

    # This break logger things ....
    def get_logger_inst_name(self):
        "Override default method name, we use obj fqn here"

        index = getattr(self, "index", None)
        if index is not None:
            index = f".{index}"
        else:
            index = ""

        return f"{self.get_obj_fqn()}{index}"
        # return f"{self.get_obj_prefix()}{index}"
        # return f"{self.get_obj_fqn()}{index}"

    def set_logger(self, logger=None):
        """Set instance logger name or instance"""

        if not logger:
            # name = self.get_ident()
            name = self.get_logger_inst_name()
            logger = logging.getLogger(name)

        self.log = logger

    def set_level(self, level=None):
        "Set logger level"

        log_level = level or self.log_level
        if isinstance(log_level, str):
            log_level = logging.getLevelName(log_level)

        if log_level:
            self.log.setLevel(log_level)

    def traceback(self):
        "Print traceback to stdout"
        traceback.print_stack()


class MapAttrMixin(BaseMixin):
    "MapAttrMixin"

    # # Mapping rules
    # mixin_map = {}

    # # Allow mixin map overrides
    # attr_override = False

    # # Set your static mapping here
    # attr_map = {
    #     # "conf": None,
    #     # "log": "log2",
    # }

    # # Set a function to forward unknown attr, can be Tue/False or a function
    # attr_forward = True

    # # def _init(self, *args, **kwargs):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     attr_map = self.attr_map

    #     # Init manual mapping
    #     for name, key in attr_map.items():
    #         key = key or name
    #         value = self.node_ctrl.mixin_get(key)

    #         if not value:
    #             raise errors.MissingMixin(f"Missing mixin: {key}")

    #         self.node_ctrl.mixin_set(value, name=name)

    #     # Add hooks
    #     this = self

    #     def func(name):
    #         "Hook gettattr"
    #         if name in this.mixin_map:
    #             return True, this.mixin_map[name]
    #         return False, None

    #     # The methods has changed !
    #     self.node_ctrl.mixin_hooks("__getattr__", func)

    #     # Patch object __getattr__
    #     if self.attr_forward is True:

    #         def func2(self, name):
    #             "Hook gettattr for top object"
    #             return getattr(this.node_ctrl, name)

    #         self.node_ctrl._obj.__class__.__getattr__ = types.MethodType(
    #             func2, self.node_ctrl._obj.__class__
    #         )
