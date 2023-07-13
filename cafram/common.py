"""
Cafram Root Classes
"""

import inspect
import logging
from pprint import pprint
from typing import Optional, Union

from python_log_indenter import IndentedLoggerAdapter


class CaframObj:
    "An empty root class to determine a cafram object or not"

    # Name part
    # name = None
    __cafram_name__ = None

    def get_name(self):
        "Retrieve node Name"
        return self.__cafram_name__ or self.__class__.__name__

    def get_prefix(self):
        "Return name prefix"
        return self.__class__.__module__

    def get_fqn(self):
        "Return the class Fully Qualified Name of any object"
        prefix = self.get_prefix()
        name = self.get_name()
        if prefix and name:
            return ".".join([prefix, name])
        return name

    def get_mro(self):
        "Return the class MRO of any object"
        cls = type(self)
        return inspect.getmro(cls)


class CaframNode(CaframObj):
    "An empty root class to determine a cafram object or not"


class CaframInternalsGroup(CaframObj):
    "Cafram Internals"

    # Does the Cafram object are impersonated to obj
    _obj_debug = False

    _obj_logger_level = None

    _obj_logger_indent = 0

    # Do yo want native logger to be impersonated as well, None to use defaults
    # _obj_logger_impersonate = False

    # Prefix of the impersonated object, string or None to be ignored
    _obj_logger_impersonate_prefix: Optional[str] = None

    # Class attr
    _obj = None
    _log = None

    # Init method
    # --------------------
    def __init__(self, debug=None, impersonate=None, log_level=None):
        "Create new mixin. Ensure nodectrl is always registered and logger ready to be used"

        # Configure base mixin logger
        if isinstance(debug, bool):
            self._obj_debug = debug
        if impersonate:
            assert isinstance(
                impersonate, str
            ), "impersonate must be a string, got: {impersonate}"
            self._obj_logger_impersonate_prefix = impersonate
        if log_level:
            self._obj_logger_level = log_level

        self._init_logger(level=log_level)

    # Object management
    # --------------------

    def get_obj(self):
        "Return current object"
        return self._obj

    def get_obj_name(self):
        "Get object name"
        obj = self.get_obj()
        if isinstance(obj, CaframObj):
            return obj.get_name()
        return type(self).__name__

    def get_obj_prefix(self):
        "Get object prefix"
        obj = self.get_obj()
        if isinstance(obj, CaframObj):
            return obj.get_prefix()
        else:
            return type(self).__module__

    def get_obj_fqn(self):
        "Return the class Fully Qualified Name of any object"
        prefix = self.get_obj_prefix()
        name = self.get_obj_name()
        if name and prefix:
            return f"{prefix}.{name}"
        return name or prefix

    # Ident Object management
    # --------------------

    def get_ident(self):
        "Return the class Fully Qualified Name of any object"

        if self._obj_debug:
            # prefix = f'YOOOOOOOOOOOOOOOOOO{self.get_obj_fqn()}[{self.get_prefix()}.{self.get_name()}]'
            # prefix = f"{self.get_obj_fqn()}[{self.get_prefix()}]"
            ident = f"{self.get_obj_fqn()}[{self.get_name()}]"
            return ident
        return super().get_fqn()

    def __repr__(self):
        "Mixin representation"
        return self.get_ident()

    def get_ctrl(self):
        "Return current Node controller"
        return self

    # Logger management
    # --------------------

    def is_impersonated(self):
        "Return if object is impersonated or not"
        return self._obj_debug

    def get_logger_name(self):  # , impersonate=None):
        "Get logger internal name"

        if self.is_impersonated() is True:

            if self._obj_logger_impersonate_prefix:
                prefix = self._obj_logger_impersonate_prefix
            else:
                prefix = self.get_prefix()

            if self.get_obj_fqn() != f"{prefix}.{self.get_name()}":
                logger_name = f"{self.get_obj_fqn()}.{prefix}.{self.get_name()}"
            else:
                logger_name = f"{self.get_obj_fqn()}"
        else:
            # logger_name = str(self.__class__)
            logger_name = self.get_fqn()
            # logger_name = self.get_name()

        return logger_name

    def _init_logger(self, level=None, impersonate=None):
        "Init internal cafram logger"

        logger_name = self.get_logger_name()
        impersonated = "impersonated" if self.is_impersonated() else "generic"

        if False and self._obj_logger_indent:
            # NOT WORKING AT THIS STAGE
            _log = IndentedLoggerAdapter(logging.getLogger(logger_name))
            _log.add(self._obj_logger_indent)
        else:
            _log = logging.getLogger(logger_name)

        # level = level or self.get_ctrl()._obj_logger_level
        level = level or self._obj_logger_level
        if level is not None:
            # print ("SET LEVEL", level)
            _log.setLevel(level)
        _log.info(
            f"Get {impersonated} Cafram logger for {self}: {logger_name} {self.__class__} ({self.is_impersonated()})"
        )

        self._log = _log


class CaframCtrl(CaframInternalsGroup):
    "Cafram Controller Type"

    _obj_attr = "__node__"
    _obj_logger_impersonate_prefix = "cafram"

    # OVERRIDES
    def get_ident(self):
        "Return the class Fully Qualified Name of any object"

        key = self.get_name()
        if self._obj_debug:
            key = self._obj_attr
        ident = f"{self.get_obj_fqn()}[{key}]({self.get_name()})"
        return ident
        # return super().get_fqn()


class CaframMixin(CaframInternalsGroup):
    "Cafram Mixin Type"

    # _obj_logger_prefix =  "MIXIN"
    node_ctrl = None
    _obj_logger_impersonate_prefix = "caframMixin"

    def get_ctrl(self):
        "Return current Node controller"
        return self.node_ctrl

    def get_obj(self):
        "Return current object"
        return self.get_ctrl().get_obj()

    def __init__(self, node_ctrl, debug=None, impersonate=None, log_level=None):
        "Create new mixin. Ensure nodectrl is always registered and logger ready to be used"

        # Ensure node_ctrl is added
        assert issubclass(
            type(node_ctrl), CaframCtrl
        ), f"Got: {node_ctrl} ({type(node_ctrl)})"
        self.node_ctrl = node_ctrl

        # Call parent methods
        super().__init__(debug=debug, impersonate=impersonate, log_level=log_level)

    # OVERRIDES
    def get_ident(self):
        "Return the class Fully Qualified Name of any object"

        key = self.get_name()
        if self.node_ctrl._obj_debug:
            key = self.mixin_key

        # TODO: Bug below !!!
        ident = f"{self.get_obj_fqn()}[{key}]({self.get_name()})"
        return ident
        # return super().get_fqn()
