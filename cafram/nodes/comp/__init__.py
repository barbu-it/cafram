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
from ...lib.utils import truncate

# Helpers
################################################################


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

        # Update local conf
        creates = False
        for key, val in mixin_conf.items():
            if not creates:
                if not hasattr(self, key):
                    if creates is None:
                        continue

            val = self._prepare_conf(val)

            setattr(self, key, val)

        # Build remap config and assign kwargs to attr
        remap_conf = self.build_remap("mixin_param__")
        # print ("REMAPPPP")
        # print (remap_conf, kwargs)
        self.remap_kwargs(remap_conf, kwargs)

        # Assign aliases
        self.mixin_conf = mixin_conf
        self._mixin_alias_map = self._list_aliases()

        self.mixin_init_kwargs = kwargs

        # print ("\n\n================= NEW MIXIN", self)
        # pprint (self.__dict__)
        # print ("=" * 6 + "v" * 10)

    def build_remap(self, prefix):
        "Build param list"

        ret = {}
        for key in dir(self):

            if not key.startswith(prefix):
                continue

            target = key.replace(prefix, "")
            if not target:
                continue

            param = getattr(self, key)
            ret[target] = param

        return ret

    def remap_kwargs(self, remap, kwargs):
        for attr_name, param_name in remap.items():

            if not param_name in kwargs:
                continue

            param_value = kwargs[param_name]
            # print ("REMAP", self, attr_name, param_value)
            setattr(self, attr_name, param_value)

    def _prepare_conf(self, value):
        "Transform some specific parameters"

        # Rewrap/rewrite callables !
        # Look for functions or bound methods
        if inspect.isfunction(value) or (
            callable(value) and hasattr(value, "__self__")
        ):

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
                    # print("Rewrap function to mixin", value)

                    def _wrapper(*args, **kwargs):

                        try:
                            return _func(self, *args, **kwargs)
                        except TypeError as err:
                            msg = f"{err}, Please ensure {_func} have the folowing signature: def {_func.__name__}(self, mixin, *args, **kwargs)"
                            raise errors.BadArguments(msg) from err
                            assert False

                    value = _wrapper

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

    def _register_alias(self, name, value, undeclared=False, override=False):
        "Method for mixins to register alias into NodeCtrl"
        # alias_map = self.alias_map

        if self.mixin_aliases:
            if not undeclared:
                assert (
                    name in self._mixin_alias_map
                ), f"Missing undeclared alias for {self}: {name}"
            name = self._mixin_alias_map.get(name, name)
            if name:
                self.node_ctrl.alias_register(name, value, override=override)

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
