


import logging
import textwrap
from inspect import signature

from pprint import pprint, pformat
from cafram2.common import CaframMixin, CaframCtrl
import cafram2.errors as errors
import inspect

log = logging.getLogger(__name__)



# from cafram2.nodes import Node2
# from cafram2.mixins import BaseMixin


# class MixinLoader():

#     def __init__(self, mixin):

#         self._mixin_src = mixin or BaseMixin
#         self._start()

#     def _start(self):
#         self._mixin = Node2(node_conf=[self._mixin_src])

#     def dump(self, **kwargs):
#         self._mixin.dump(**kwargs)

#     def doc(self, **kwargs):
#         self._mixin._doc(**kwargs)


class BaseMixin(CaframMixin):
    """Parent class of Cafram Mixins
    
    Usage:
      BaseMixin(node_ctrl, mixin_conf=None)
      BaseMixin(node_ctrl, mixin_conf=[BaseMixin])

    """

    # If key is None, register as ephemeral mixin, if string as persistant.
    mixin = None
    name = None

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
            "mixin": {
                "title": "Mixin class",
                "description": "Mixin class to use",
                "default": mixin,
            },
        },
    }
    
    def __init__(self, node_ctrl, mixin_conf=None, **kwargs):

        # Update config from params
        #assert False, ""
        mixin_conf = mixin_conf or {}
        for key, value in mixin_conf.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Save arguments in instance
        self.mixin = self.mixin or type(self)
        self.node_ctrl = node_ctrl
        self.mixin_conf = mixin_conf

        # Mixin initialization
        self._init(**kwargs)

    def _init(self, **kwargs):
        pass

    # def __repr__(self):
    #     return f"Mixin: <{self.__class__.__name__}:{hex(id(self))}>[{self.name}] of {self.node_ctrl}"
    #     # return f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}> named '{self.name}' in {self.node_ctrl}"


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
                if isinstance(value, (type(None), bool, int, str, list, dict, set, tuple)):
                    target = out["private_var"]

                target[attr_name] = getattr(self, attr_name)
            else:
                value = getattr(self, attr_name)

                if isinstance(value, (type(None), bool, int, str, list, dict, set, tuple)):
                    out["params"][attr_name] = value
                else:
                    out["methods"][attr_name] = value

        if not details:
            del out["methods"]
            del out["private_fn"]

        return out


    def doc(self, details=False):
        "Show mixin internal documentation"

        fqdn = f"{self.__class__.__module__}.{self.__class__.__name__}"
        print (f"Documentation for: {fqdn}")

        print ("  Usage:")
        #print ("TESTSSS", self.__doc__, "SEP" , self.__class__.__doc__)
        head_doc = self.__doc__ or self.__class__.__doc__ or "<Missing>"
        head_doc = textwrap.indent(head_doc, "    ")
        print(head_doc)

        
        other = {}
        ignore = ["payload_schema", "mixin", "_schema"]
        data = self._dump_attr(details=True, ignore=ignore)


        bases = inspect.getmro(self.__class__)
        print ("  Mixins inheritance:")
        for cls in reversed(bases):
            print (f"    - {cls.__module__}.{cls.__name__}")


        if "params" in data:
            sec = data["params"]
            print ("\n  Parameters:")
            for key, val in sec.items():
                print (f"    {key}: {val}")

        
        if "methods" in data:
            sec = data["methods"]
            print ("\n  Methods:")
            for key, val in sec.items():
                sign = type(val)
                try:
                    sign = signature(val)
                    
                except:
                    other[key] = val
                    continue
                if type(val).__name__ not in ["method"]:
                    other[key] = val
                    continue

                print (f"    {key}{sign}:")
                head_doc = textwrap.indent(val.__doc__ or "<Missing>", "      ")
                print(head_doc)

        if len(other) > 0:
            sec = other
            print ("\n  Other:")
            for key, val in sec.items():
                sign = type(val).__name__
                print (f"    {key}({sign}): {val}")
                # head_doc = textwrap.indent(val.__class__.__doc__ or "N", "      ")
                # print(head_doc)

        
        if self._schema:
            schema = self._doc_jsonschema_get()
            if details:
                print ("\n  JSON Schema:")
                #data = pformat(self.payload_schema)
                
                data = json.dumps(schema, indent = 4) 
                head_doc = textwrap.indent(data, "      ")
                print(head_doc)
            else:

                print ("\n  JSON Doc:")
                props = schema.get("properties")
                for key, val in props.items():

                    title = val.get("title", None)
                    default = val.get("default", None)
                    print (f"    {key}({default}): {title}")

                    desc = val.get("description", "")
                    head_doc = '\n'.join(textwrap.wrap(desc, width=50))
                    head_doc = textwrap.indent(head_doc, "      ")
                    print(head_doc + '\n')
                
    
    def _doc_jsonschema_get(self):
        "Build json schema from mro"

        bases = inspect.getmro(self.__class__)
        props = {}
        for base in reversed(bases):
            schema = getattr(base, "_schema", None)
            if schema:
                schema_props = schema.get("properties", {})
                for key, val in schema_props.items():
                    props[key] = val

        out = dict(self._schema)
        out["properties"] = props
        return out


    def dump(self, stdout=True, details=False, ignore=None):
        "Dump mixin for debugging purpose"

        out = []
        out.append(f"Dump of mixin: {self.__class__.__name__}:{hex(id(self))}")

        attr = self._dump_attr(details=details, ignore=ignore)
        for section, value in attr.items():

            value_ = textwrap.indent(pformat(value), "      ")
            out.append(f"  {section}:\n{value_}")

        ret = "\n".join(out)
        if stdout:
            print (ret)
        return ret


    #     ######### OLD
        

    #     out.append(f"Dump of mixin: {self.__class__.__name__}")

    #     data = { **self.__class__.__dict__ , **dict(self.__dict__)}
    #     data = dict(self.__dict__)
    #     #pprint (data)

    #     out.append (f"  class: {self}")
    #     name = data.pop("name")
    #     out.append (f"  name: {name}")
    #     node_ctrl = data.pop("node_ctrl")
    #     out.append (f"  node_ctrl: {node_ctrl}")
    #     # conf = data.pop("conf")
    #     conf = textwrap.indent(pformat(data), "      ")
    #     out.append (f"  conf:\n{conf}")

    #     attr = self._dump_attr()
    #     attr = textwrap.indent(pformat(attr), "      ")
    #     out.append(f"  attr:\n{attr}")
    #     #out.extend(self._dump_mixin(data))

    #     ret = "\n".join(out)
    #     if stdout:
    #         print (ret)
    #     return ret
        
    # def _dump_mixin(self, data):

    #     out = []

    #     data = pformat(data)
    #     data = textwrap.indent(data, "      ")
    #     out.append (f"  other:\n{data}")

    #     return out