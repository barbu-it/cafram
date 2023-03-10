"""
Base mixins
"""

import types
import logging
import copy
import traceback
from pprint import pprint

# from ..nodes import Node
from ..lib import log_colors

from ..nodes2 import Node
from ..common import CaframObj
from .. import errors
from . import BaseMixin, LoadingOrder


#log = logging.getLogger(__name__)


# def add_positional_arg(func):
#     def wrapper(*args, **kwargs):
#         args = list(args)
#         args.insert(1, 'extra_arg')
#         return func(*args, **kwargs)
#     return wrapper




# Core Mixins
################################################################

class IdentMixin(BaseMixin):

    #key = "ident"
    mixin_key = "ident"

    # Config
    ident = None
    ident_suffix = None
    ident_prefix = None

    # Parameters
    _param_ident = "ident"
    _param_ident_suffix = "ident_suffix"
    _param_ident_prefix = "ident_prefix"

    def _get_name_target(self):
        "Try to catch CaframObj reference for naming, fall back on current class"

        target = self

        obj = self.node_ctrl._obj
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
        



class PayloadMixin(IdentMixin):

    mixin_key = "payload"

    _payload = None
    _param__payload = "payload"

    value_alias = "value"

    default = None
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
            "key": {
                "title": "Mixin key",
                "description": "Name of the mixin. Does not keep alias if name is set to `None` or starting with a `.` (dot)",
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
            # "name_param": {
            #     "title": "Mixin name parameter",
            #     "description": "Name of the parameter to load name from",
            #     "default": name_param,
            # },
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


    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._value = None
        self.set_value(self._payload)
        self._register_alias()

    def _register_alias(self):
        if self.value_alias:
            self.node_ctrl.alias_register(self.value_alias, self.get_value())

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
        conf = self.set_default(conf)
        conf = self.validate(conf)
        self._value = conf
        return self._value


    # Transformers/Validators
    # ---------------------

    def set_default(self, payload):
        "Update defaults"
        return payload or copy.copy(self.default)


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


class LoggerMixin(IdentMixin):

    #name = "logger"
    #key = "logger"

    mixin_order = LoadingOrder.PRE
    mixin_key = "logger"

    _logger = None
    _param__logger = "logger"

    # Logger instance
    log = None

    # Logger config
    log_alias = "log"

    # Logger level: Logging level, can be object, string or number
    log_level = None

    # Logger name, if none, set to the Node Class name
    log_name = None

    # Prefix to use, if None, set to the module name
    log_prefix = None

    # FQDN of logger, generated from log_name and log_prefix
    log_fqdn = None

    # # If true, logging 
    # log_node = True
    log_colors = True

    # Define logging format
    log_sformat = "default"
    # Define time format
    log_tformat = "default"

    # Log and time formats db
    log_sformats = {
        "default": "%(levelname)8s: %(message)s",
        "struct": "%(name)-20s%(levelname)8s: %(message)s",
        "time": "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s",
        "precise": (
            "%(asctime)s.%(msecs)03d"
            + " (%(process)d/%(thread)d) "
            + "%(pathname)s:%(lineno)d:%(funcName)s"
            + ": "
            + "%(levelname)s: %(message)s"
        ),
    }
    log_tformats = {
        "default": "%H:%M:%S",
        "precise": "%Y-%m-%d %H:%M:%S",
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 

        # Init logger if not provided in params
        if not self._logger:
            self.set_logger()
        else:
            self.log = self._logger

        # Customize Logger
        self.set_format()
        self.set_level()

        # Register logger into node_ctrl
        self.node_ctrl.alias_register(self.log_alias, self.log)

    def set_logger(self):
        """Set instance logger name or instance"""

        name = self.get_logger_fqdn()
        self.log = logging.getLogger(name)

        # Disable log propagation
        self.log.propagate = False

    def get_logger_fqdn(self, name=None, prefix=None):
        "Return the logger FQDN"

        return self.get_ident()


    def set_level(self, level=None):
        "Set logger level"

        log_level = level or self.log_level
        if isinstance(log_level, str):
            log_level = logging.getLevelName(log_level)

        if log_level:
            self.log.setLevel(log_level)

    def set_format(self, sformat=None, tformat=None):
        "Change logger format"  

        sformat = sformat or self.log_sformat
        tformat = tformat or self.log_tformat

        _sformat = self.log_sformats[sformat]
        _tformat = self.log_sformats[tformat]



        formatter = logging.Formatter(_sformat)
        if self.log_colors:
            formatter = log_colors.ColorizedArgsFormatter(_sformat)

        # Get current handle
        if len(self.log.handlers) > 0:
            #pprint (self.log.__dict__)
            ch = self.log.handlers[0]
            self.log.removeHandler(ch)
        else:
            ch = logging.StreamHandler()

        ch.setFormatter(formatter)
        # ch.setLevel(logging.DEBUG)

        #self.log.handlers[0] = ch
        #self.log.handlers.insert(0, ch)
        self.log.addHandler(ch)

    def traceback(self):
        "Print traceback to stdout"
        traceback.print_stack()

        

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

    #def _init(self, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        # The methods has changed !
        self.node_ctrl.mixin_hooks("__getattr__", func)

        # Patch object __getattr__
        if self.attr_forward is True:

            def func2(self, name):
                "Hook gettattr for top object"
                return getattr(this.node_ctrl, name)

            self.node_ctrl._obj.__class__.__getattr__ = types.MethodType(
                func2, self.node_ctrl._obj.__class__
            )
