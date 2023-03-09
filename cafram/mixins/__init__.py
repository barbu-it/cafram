"""
Base Mixin Class definition
"""

import textwrap
import inspect
from enum import IntEnum

from pprint import pprint, pformat

from .. import errors
from ..lib.utils import truncate
from ..common import CaframObj, CaframMixin, CaframCtrl
from ..utils import SPrint


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
    #key = None
    mixin_order = LoadingOrder.NORMAL
    mixin_key = None

    name_from_obj = False

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

    def __init__(self, node_ctrl, mixin_conf=None, **kwargs):

        # super().__init__(**kwargs)

        self.node_ctrl = node_ctrl
        self.mixin = self.mixin or type(self) # TODO: Is it relevant ????
        self._init_logger(prefix=self.node_ctrl._obj_logger_prefix)


        # # Update name
        # self.name_prefix = None
        # if self.name_from_obj:
        #     obj = self.node_ctrl._obj
        #     if issubclass(type(obj), CaframObj):
        #         self.name_prefix = obj.get_fqn()




        # Update mixin requested config 
        mixin_conf = mixin_conf or {}
        for key, value in mixin_conf.items():

            # Check for bound methods
            if callable(value) and hasattr(value, '__self__'):
                cls = value.__self__.__class__

                # If not a CaframMixin class, add mixin as second param
                if not issubclass(cls, CaframMixin):
                    func = value
                    def wrapper(*args, **kwargs):
                        return func(self, *args, **kwargs)
                    self._log.info (f"Overriden method is now available '{key}': {value}")
                    value =  wrapper

            if hasattr(self, key):
                self._log.debug(f"Update mixin from config '{key}' with: {truncate(value)}")
                setattr(self, key, value)

        # Save arguments in instance
        self.mixin_conf = mixin_conf

        # Fetch kwargs parameters for live parameters (_param_)
        for attr in dir(self):
            
            if not attr.startswith("_param_"):
                continue
            
            attr_name = attr.replace("_param_", "")
            attr_param = getattr(self, attr)
            #print ("SCAN ", attr_param)
            if attr_param and attr_param in kwargs:
                attr_value = kwargs.get(attr_param)
                self._log.debug(f"Update mixin from param '{attr_name}' with: {truncate(attr_value)}")
                setattr(self, attr_name, attr_value)


        # # TEMP, deprecation process
        # if hasattr(self, "_init"):
        #     mro = self.get_mro()
        #     cls = None
        #     for cls in mro:
        #         if hasattr(cls, '_init'):
        #             break
        #     assert False, f"_init is deprecated on: {self.get_fqn()}, problematic classes: cls"


    # Override CaframObj methods
    # -------------------

    # def _get_name_target(self):
    #     "Try to catch CaframObj reference for naming, fall back on current class"

    #     target = self

    #     obj = self.node_ctrl._obj
    #     if issubclass(type(obj), CaframObj):    
    #         target = obj

    #     return target

    # def get_name(self):
    #     "Get name from CaframObj first or get back to class name"
    #     target = self._get_name_target()        

    #     name = target.name or target.__class__.__name__
    #     inst = target.name_inst
    #     if inst:
    #         name += str(inst)
    #     return name



    # def get_fqn(self):
    #     "Get FQN from CaframObj first or get back to class name"

    #     # TODO: Transform into 
    #     name_prefix = self.name_prefix

    #     if name_prefix:
    #         obj = self.node_ctrl._obj
    #         if issubclass(type(obj), CaframObj):
    #             print ("FQN FROM OBJ")  
    #             return obj.get_fqn()

    #     print ("FQN FROM MIXIN")
    #     return super().get_fqn()


    # def get_fqn__2(self):
    #     "Get FQN from CaframObj first or get back to class name"

    #     target = self._get_name_target()

    #     log_name = self.get_name()
    #     log_prefix = self.name_prefix

    #     if not log_name or not log_prefix:

    #         if self.node_ctrl._obj:
    #             target = self.node_ctrl._obj
    #         else:
    #             target = self
    #         target = type(target)

    #         if not log_prefix:
    #             log_prefix = target.__module__ + "."

    #         if not log_name:
    #             log_name = target.__name__

    #     return f"{log_prefix}{log_name}"




    # Generic
    # -------------------




    # v1
    # def __getattribute__(self, name):
        
    #     attr = super().__getattribute__(name)

    #     if callable(attr):
    #         try:
    #             cls = attr.__self__.__class__
    #         except AttributeError:
    #             cls = None

    #         if cls and not issubclass(cls, CaframMixin):
    #             #print ("====> CATCH ALL", name, cls)
    #             #pprint (attr)
    #             def wrapper(*args, **kwargs):
    #                 return attr(self, *args, **kwargs)
    #             return wrapper
    #     #else:
    #     return attr

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
            elif attr_name.startswith("_"):

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

                except:
                    other[key] = val
                    continue
                if type(val).__name__ not in ["method"]:
                    other[key] = val
                    continue

                print(f"    {key}{sign}:")
                head_doc = textwrap.indent(val.__doc__ or "<Missing>", "      ")
                print(head_doc)

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
        #bases = inspect.getmro(self.__class__)
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
