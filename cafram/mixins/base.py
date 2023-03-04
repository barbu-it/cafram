"""
Base mixins
"""

import types
import logging
from pprint import pprint

from ..nodes import Node
from . import BaseMixin


log = logging.getLogger(__name__)


# Core Mixins
################################################################


class PayloadMixin(BaseMixin):

    name = "payload"
    name_param = "payload"
    value_alias = "value"

    payload_schema = False
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
            "name_param": {
                "title": "Mixin name parameter",
                "description": "Name of the parameter to load name from",
                "default": name_param,
            },
            "value_alias": {
                "title": "Value alias name",
                "description": "Name of the alias to retrieve value. Absent if set to None",
                "default": value_alias,
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

    def _init(self, **kwargs):

        super()._init(**kwargs)

        self._value = None
        self._payload = kwargs.get(self.name_param, None)
        self.set_value(self._payload)
        self._register_alias()

    def _register_alias(self):
        if self.value_alias:
            self.node_ctrl.alias_register(self.value_alias, self.value)

    # Generic value handler
    # ---------------------
    @property
    def value(self):
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
        conf = self.transform(value)
        conf = self.validate(conf)
        self._value = conf
        return self._value

    # Transformers/Validators
    # ---------------------

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

    _node_conf = [{"mixin": PayloadMixin}]


# Utils Mixins
################################################################


class MapAttrMixin(BaseMixin):

    # Mapping rules
    mixin_map = {}

    # Allow mixin map overrides
    attr_override = False

    # Set your static mapping here
    attr_map = {
        # "conf": None,
        # "log": "log2",
    }

    # Set a function to forward unknown attr, can be Tue/False or a function
    attr_forward = True

    def _init(self, *args, **kwargs):

        attr_map = self.attr_map

        # Init manual mapping
        for name, key in attr_map.items():
            key = key or name
            value = self.node_ctrl.mixin_get(key)

            if not value:
                raise errors.MissingMixin(f"Missing mixin: {key}")

            self.node_ctrl.mixin_set(value, name=name)

        # Add hooks
        this = self

        def func(name):
            "Hook gettattr"
            if name in this.mixin_map:
                return True, this.mixin_map[name]
            return False, None

        self.node_ctrl.mixin_hooks("__getattr__", func)

        # Patch object __getattr__
        if self.attr_forward is True:

            def func2(self, name):
                "Hook gettattr for top object"
                return getattr(this.node_ctrl, name)

            self.node_ctrl._obj.__class__.__getattr__ = types.MethodType(
                func2, self.node_ctrl._obj.__class__
            )


class LoggerMixin(BaseMixin):

    key = "logger"
    conf_logger = None

    default_conf = {
        # Set True to map to known mixins
        "logger_key": "log",
        # Define the logger name, class name if not used
        "logger_name": None,
        # Define the logger name prefix, None for internal use
        "logger_prefix": None,
        # Define if this config is inherited by children
        "logger_propagate": True,
        # Define logging format
        "logger_sformat": "default",
        # Define time format
        "logger_tformat": "default",
    }

    # Log and time formats
    sformats = {
        "default": "%(levelname)8s: %(message)s",
        "struct": "%(name)-40s%(levelname)8s: %(message)s",
        "time": "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s",
        "precise": (
            "%(asctime)s.%(msecs)03d"
            + " (%(process)d/%(thread)d) "
            + "%(pathname)s:%(lineno)d:%(funcName)s"
            + ": "
            + "%(levelname)s: %(message)s"
        ),
    }
    tformats = {
        "default": "%H:%M:%S",
        "precise": "%Y-%m-%d %H:%M:%S",
    }

    def _init(self, *args, **kwargs):

        logger_key = self.conf["logger_key"]
        self.set_logger()

        # Register logger into node_ctrl
        self.node_ctrl.mixin_set(self.log, name=logger_key, shortcut=True)

    def set_format(self, sformat=None, tformat=None):

        sformat = sformat or self.conf["logger_sformat"]
        tformat = tformat or self.conf["logger_tformat"]

        _sformat = self.sformats.get(sformat, sformat)
        _tformat = self.sformats.get(tformat, tformat)

        ch = logging.StreamHandler()
        formatter = logging.Formatter(_sformat)
        ch.setFormatter(formatter)
        # ch.setLevel(logging.DEBUG)

        self.log.addHandler(ch)

    def set_logger(self, conf_logger=None, attribute_name="log"):
        """Set instance logger name or instance"""

        logger_name = self.conf["logger_name"]
        logger_prefix = self.conf["logger_prefix"]
        if not logger_name:
            logger_name = self.node_ctrl._obj.__class__.__name__
            logger_name = self.ident
        if not logger_prefix:
            logger_prefix = __name__

        logger_fqdn = f"{logger_prefix}.{logger_name}"

        self.logger_name = logger_name
        self.logger_prefix = logger_prefix
        self.logger_fqdn = logger_fqdn

        # Get logger
        self.log = logging.getLogger(logger_fqdn)

        # Set level
        self.log.setLevel(logging.DEBUG)

        self.set_format()
