"""
Cafram Root Classes
"""

import logging
import inspect

from pprint import pprint


class CaframObj:
    "An empty root class to determine a cafram object or not"

    # Name part
    name = None

    def get_name(self):
        "Retrieve node Name"
        return self.name or self.__class__.__name__

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
    _obj_impersonate = True

    _obj_logger_level = None

    # Do yo want native logger to be impersonated as well, None to use defaults
    _obj_logger_impersonate = False

    # Prefix of the impersonated object, string or None to be ignored
    _obj_logger_impersonate_prefix = None

    # Class attr
    _obj = None
    _log = None

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

        if self._obj_impersonate:
            # prefix = f'YOOOOOOOOOOOOOOOOOO{self.get_obj_fqn()}[{self.get_prefix()}.{self.get_name()}]'
            prefix = f"{self.get_obj_fqn()}[{self.get_prefix()}]"
            return prefix
        return super().get_fqn()

    def __repr__(self):
        "Mixin representation"
        return self.get_ident()

    # Logger management
    # --------------------

    def get_logger_name(self, impersonate=None):
        "Get logger internal name"

        if impersonate is True:

            if self._obj_logger_impersonate_prefix:
                logger_name = f"{self.get_obj_fqn()}.{self._obj_logger_impersonate_prefix}.{self.get_name()}"
            else:
                logger_name = (
                    f"{self.get_obj_fqn()}.{self.get_prefix()}.{self.get_name()}"
                )
        else:
            logger_name = self.get_fqn()

        return logger_name

    def _init_logger(self, level=None, impersonate=None):
        "Init internal cafram logger"

        impersonate = (
            impersonate
            if isinstance(impersonate, bool)
            else self._obj_logger_impersonate
        )

        logger_name = self.get_logger_name(impersonate=impersonate)
        # impersonated = self._obj_logger_impersonate or self._obj_impersonate
        impersonated = "impersonated" if impersonate else "generic"

        # print ("NEW LOGGER", logger_name, impersonate)

        self._log = logging.getLogger(logger_name)

        level = level or self._obj_logger_level
        if level is not None:
            self._log.setLevel(level)
        self._log.debug(f"Get {impersonated} Cafram logger for {self}: {logger_name}")


class CaframCtrl(CaframInternalsGroup):
    "Cafram Controller Type"

    _obj_attr = "_node"
    _obj_logger_impersonate_prefix = "cafram"

    # OVERRIDES
    def get_ident(self):
        "Return the class Fully Qualified Name of any object"

        if self._obj_impersonate:
            # BROKEN: prefix = f"{self.get_obj_fqn()}[{self._obj_attr}]({self.get_prefix()})" # Missing name in last part
            # BROKEN: prefix = f"{self.get_obj_fqn()}[{self._obj_attr}]({self.get_name()})"  # Missing prefix in last part
            prefix = f"{self.get_obj_fqn()}[{self._obj_attr}]({self._obj_logger_impersonate_prefix}.{self.get_name()})"  # Missing prefix in last part
            return prefix
        return super().get_fqn()


class CaframMixin(CaframInternalsGroup):
    "Cafram Mixin Type"

    # _obj_logger_prefix =  "MIXIN"
    node_ctrl = None

    _obj_logger_impersonate_prefix = "cafram.Mixin"

    def get_ctrl(self):
        "Return current Node controller"
        return self.node_ctrl

    def get_obj(self):
        "Return current object"
        return self.get_ctrl().get_obj()

    # OVERRIDES
    def get_ident(self):
        "Return the class Fully Qualified Name of any object"

        if self._obj_impersonate:
            # BROKEN: prefix = f"{self.get_obj_fqn()}[{self.mixin_key}]({self.get_prefix()})" # Missing name
            # prefix = f"{self.get_obj_fqn()}[{self.mixin_key}]({self.get_prefix()}.{self.get_name()})"  # Long form
            prefix = f"{self.get_obj_fqn()}[{self.mixin_key}]({self.get_name()})"  # Short form
            return prefix
        return super().get_fqn()
