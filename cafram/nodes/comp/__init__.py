"""
Base Mixin Class definition
"""

import inspect
import json
import textwrap
from enum import IntEnum
from pprint import pformat, pprint
from typing import List, Optional, Union

from ... import errors
from ...common import CaframCtrl, CaframMixin, CaframObj
from ...lib.sprint import SPrint
from ...lib.utils import truncate, update_classattr_from_dict

# Helpers
################################################################

# def _list_parameters_from_argsV2(self, obj, kwargs, prefix="mixin_param__"):

# def update_classattr_from_dict(obj, kwargs, prefix="mixin_param__"):
#     """List args/kwargs parameters

#     Loop over each key/value of kwargs,

#     Scan a given object `obj`, find all its attributes starting with `prefix`,
#     and update all matched attributes from kwargs
#     """

#     # Params, left part is constant !
#     # mixin_param__<SOURCE> = <EXPECTED_NAME>

#     ret = {}
#     for key, val in kwargs.items():

#         attr_name = f"{prefix}{key}"
#         print ("YOOOO", hasattr(obj, attr_name), key, attr_name)
#         if not hasattr(obj, attr_name):
#             continue

#         # Fetch new name from config
#         new_name = getattr(obj, attr_name)
#         ret[new_name] = val

#     return ret


# Base mixins
################################################################


class LoadingOrder(IntEnum):
    "Helper class to determine mixin loading order"

    FIRST = 10
    PRE = 30
    NORMAL = 50
    POST = 70
    LAST = 90


class BaseMixin(CaframMixin):
    """Parent class of Cafram Mixins

    Usage:
      BaseMixin(node_ctrl, mixin_conf=None)
      BaseMixin(node_ctrl, mixin_conf=[BaseMixin])

    """

    # If key is None, register as ephemeral mixin, if string as persistant.
    mixin = None
    # key = None
    mixin_order = LoadingOrder.NORMAL
    mixin_key: Optional[str] = None
    mixin_aliases = True
    _mixin_alias_map = None

    mixin_logger_impersonate = None
    mixin_logger_level = None

    # name_from_obj = False

    # pylint: disable=line-too-long
    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: BaseMixin",
        "description": "PayloadMixin Configuration",
        "default": {},
        "properties": {
            "mixin_key": {
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
            "mixin": {
                "title": "Mixin class",
                "description": "Mixin class to use",
                "default": mixin,
            },
        },
    }

    # def __repr__(self):
    #     "Mixin representation"
    #     prefix = self.get_fqn()
    #     suffix = f"[{self.mixin_key}]{type(self).__name__}"
    #     return f"<{prefix}{suffix}>"

    def __init__(self, node_ctrl, mixin_conf=None, **kwargs):

        # Call generic init for cafram objects
        super().__init__(node_ctrl)

        # Fetch mixin params and __init__ kwargs
        mixin_conf = mixin_conf or {}
        param_conf = update_classattr_from_dict(self, kwargs, prefix="mixin_param__")

        # Update mixin with gathered configs
        # self._update_attrs_conf(mixin_conf, creates=False) # TODO: What to do of unparsed items ???
        self._update_attrs_conf(mixin_conf, creates=None)
        self._update_attrs_conf(param_conf, creates=True)

        # Assign aliases
        self.mixin_conf = mixin_conf
        self._mixin_alias_map = self._list_aliases()

    def _update_attrs_conf(self, mixin_conf, creates=False):
        """Update object attributes from a dict. Fail if key does not already exists when create=False

        If creates is None, then it skip all not already created attributes.
        """

        for key, value in mixin_conf.items():

            value = self._prepare_conf(value)

            if not creates:
                if not hasattr(self, key):
                    if creates is None:
                        continue
                    assert False, f"Unknown config option '{key}={value}' for {self}"

            setattr(self, key, value)

    def _prepare_conf(self, value):
        "Transform some specific parameters"

        # Check for bound methods
        # if callable(value) and hasattr(value, "__self__"):
        # if callable(value):

        # print ("PREPARSE VALUE", value, inspect.isfunction(value), hasattr(value, "__self__"))

        # Rewrap/rewrite callables !
        # Look for functions or bound methods
        if inspect.isfunction(value) or (
            callable(value) and hasattr(value, "__self__")
        ):
            # print ("PREPARSE FUNC ", value)

            MODE = "rebind"
            MODE = "wrap"

            if MODE == "rebind":

                # Rebound method if linked to anything
                if hasattr(value, "__get__"):
                    # print ("Remap function to method", value)
                    value = value.__get__(self)
                    # assert False, value

            else:
                # Wrap method for NodeCtrl view
                if hasattr(value, "__get__"):
                    _func = value
                    print("Rewrap function to mixin", value)

                    def _wrapper(*args, **kwargs):

                        try:
                            return _func(self, *args, **kwargs)
                        except TypeError as err:
                            # print (err)
                            msg = f"{err}, Please ensure {_func} have the folowing signature: def {_func.__name__}(self, mixin, *args, **kwargs)"

                            raise errors.BadArguments(msg) from err
                            assert False

                    value = _wrapper

                # else:
                #     print ("DO NOT CHANGE FUNCTION", value)
                #     # DEPRECATED: self._log.debug(f"Overriden method is now available '{key}': {value}")
                #     # value = _wrapper

                # # If not a CaframMixin class, add mixin as second param
                # # pylint: disable=cell-var-from-loop
                # if not issubclass(cls, CaframMixin):
                #     _func = value

                #     def wrapper(*args, **kwargs):
                #         return _func(self, *args, **kwargs)

                #     # DEPRECATED: self._log.debug(f"Overriden method is now available '{key}': {value}")
                #     value = wrapper

            # assert False, "WIP"
        # elif inspect.isfunction(value):
        #     assert False, value

        return value

    def _list_aliases(self):
        "List internal aliases"

        # Config, left part is constant !
        # mixin_alias__<SOURCE> = <ACCESS_KEY>

        aliases = {}
        for attr in dir(self):

            if not attr.startswith("mixin_alias__"):
                continue

            attr_name = attr.replace("mixin_alias__", "")
            attr_param = getattr(self, attr)
            self._log.debug(
                f"Configure alias for '{self.node_ctrl._obj.__class__.__name__}': 'o.{attr_param}' => 'o.__node__.{self.mixin_key}.{attr_name}'"
            )
            aliases[attr_param] = attr_name

        return aliases

    def _register_alias(self, name, value):
        "Method for mixins to register alias into NodeCtrl"
        # alias_map = self.alias_map

        if self.mixin_aliases:
            assert (
                name in self._mixin_alias_map
            ), f"Missing undeclared alias for {self}: {name}"
            name = self._mixin_alias_map.get(name, name)
            if name:
                self.node_ctrl.alias_register(name, value)

    # Troubleshooting
    # -------------------

    def dump(self, stdout=True, details=False, ignore=None):
        "Dump mixin for debugging purpose"

        sprint = SPrint()
        sprint(f"Dump of mixin: {self.__class__.__name__}:{hex(id(self))}")

        attr = self._dump_attr(details=details, ignore=ignore)
        for section in ["params", "methods", "private_var", "private_fn"]:
            value = attr.get(section, None)
            if value:
                value_ = textwrap.indent(pformat(value), "      ")
                sprint(f"  {section}:\n{value_}")

        ret = sprint.render(stdout=stdout)
        return ret

    def _dump_attr(self, details=False, ignore=None):

        ignore = ignore or []
        out = {
            "private_var": {},
            "private_fn": {},
            "params": {},
            "methods": {},
        }

        for attr_name in dir(self):

            if attr_name in ignore:
                continue

            if attr_name.startswith("__"):
                continue

            if attr_name.startswith("_"):

                value = getattr(self, attr_name)
                target = out["private_fn"]
                if isinstance(
                    value, (type(None), bool, int, str, list, dict, set, tuple)
                ):
                    target = out["private_var"]

                target[attr_name] = getattr(self, attr_name)
            else:
                value = getattr(self, attr_name)

                if isinstance(
                    value, (type(None), bool, int, str, list, dict, set, tuple)
                ):
                    out["params"][attr_name] = value
                else:
                    out["methods"][attr_name] = value

        if not details:
            del out["methods"]
            del out["private_fn"]

        return out

    # Documentation
    # -------------------

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def doc(self, details=False):
        "Show mixin internal documentation"

        fqdn = f"{self.__class__.__module__}.{self.__class__.__name__}"
        print(f"Documentation for: {fqdn}")

        print("  Usage:")
        # print ("TESTSSS", self.__doc__, "SEP" , self.__class__.__doc__)
        head_doc = self.__doc__ or self.__class__.__doc__ or "<Missing>"
        head_doc = textwrap.indent(head_doc, "    ")
        print(head_doc)

        other = {}
        ignore = ["payload_schema", "mixin", "_schema"]
        data = self._dump_attr(details=True, ignore=ignore)

        bases = inspect.getmro(self.__class__)
        print("  Mixins inheritance:")
        for cls in reversed(bases):
            print(f"    - {cls.__module__}.{cls.__name__}")

        # pprint(data)
        if "params" in data:
            sec = data["params"]
            print("\n  Parameters:")
            for key, val in sec.items():
                print(f"    {key}: {val}")

        if "methods" in data:
            sec = data["methods"]
            print("\n  Methods:")
            for key, val in sec.items():
                sign = type(val)
                try:
                    sign = inspect.signature(val)

                except Exception as err:
                    other[key] = val
                    assert False, f"Please fix this wide exception: {err}"
                    continue
                if type(val).__name__ not in ["method"]:
                    other[key] = val
                    continue

                print(f"    {key}{sign}:")
                head_doc = textwrap.indent(val.__doc__ or "<Missing>", "      ")
                print(head_doc)

        if "private_var" in data:
            # TODO: Show up _param vars
            sec = data["private_var"]
            print("\n  Private vars:")
            for key, val in sec.items():
                print(f"    {key}: {val}")

        if len(other) > 0:
            sec = other
            print("\n  Other:")
            for key, val in sec.items():
                sign = type(val).__name__
                print(f"    {key}({sign}): {val}")
                # head_doc = textwrap.indent(val.__class__.__doc__ or "N", "      ")
                # print(head_doc)

        if self._schema:
            schema = self._doc_jsonschema_get()
            if details:
                print("\n  JSON Schema:")
                # data = pformat(self.payload_schema)

                data = json.dumps(schema, indent=4)
                head_doc = textwrap.indent(data, "      ")
                print(head_doc)
            else:

                print("\n  JSON Doc:")
                props = schema.get("properties")
                for key, val in props.items():

                    title = val.get("title", None)
                    default = val.get("default", None)
                    print(f"    {key}({default}): {title}")

                    desc = val.get("description", "")
                    head_doc = "\n".join(textwrap.wrap(desc, width=50))
                    head_doc = textwrap.indent(head_doc, "      ")
                    print(head_doc + "\n")

    def _doc_jsonschema_get(self):
        "Build json schema from python mro"

        # Fetch schema from parent classes
        bases = self.get_mro()
        # bases = inspect.getmro(self.__class__)
        props = {}
        for base in reversed(bases):
            schema = getattr(base, "_schema", None)
            if schema:
                schema_props = schema.get("properties", {})
                for key, val in schema_props.items():
                    props[key] = val

        # Overrides parent properties in final schema
        out = dict(self._schema)
        out["properties"] = props
        return out
