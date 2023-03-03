import types
import logging
import importlib
from pprint import pprint, pformat

import textwrap
import inspect

# import .errors as errors
from . import errors  # as errors
from .mixins import BaseMixin
from .common import CaframCtrl, CaframNode  # CaframObj, CaframCtrl, CaframMixin

# from cafram2.mixins import Instance
# from cafram2.mixins import BaseMixin
# from cafram2.mixins.base import LoggerMixin, MapAttrMixin
# from cafram2.mixins.tree import (
#     ValueMixin,
#     SimpleConfMixin,
#     DictConfMixin,
#     ListConfMixin,
# )


# Init
################################################################

# Only relevant for entrypoints
# logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)
# log = logging.getLogger(__name__)
# log = logging.getLogger("cafram2")


# Base classes
################################################################


class Empty:
    pass


# NodeCtrl Public classe
################################################################

# CAFRAM_MIXINS = {
#     # Simple mixins
#     "LoggerMixin": LoggerMixin,
#     "MapAttrMixin": MapAttrMixin,
#     # Hierarchical mixins
#     "ValueMixin": ValueMixin,
#     "SimpleConfMixin": SimpleConfMixin,
#     "DictConfMixin": DictConfMixin,
#     "ListConfMixin": ListConfMixin,
# }


class NodeCtrl(CaframCtrl):

    # Public attributes
    # ---------------------

    _obj_attr = "_node"
    _obj_conf = []

    def _transform(self, payload):
        "Transform NodeCtl config"

        ret = payload
        if isinstance(payload, dict):

            ret = []
            for index, conf in payload.items():

                # Convert short forms
                if not isinstance(conf, dict):
                    _payload = {
                        "mixin": conf,
                    }
                    conf = _payload

                conf["name"] = index
                ret.append(conf)

        elif isinstance(payload, list):

            ret = []
            for index, conf in enumerate(payload):

                # Convert short forms
                if not isinstance(conf, dict):
                    _payload = {
                        "mixin": conf,
                    }
                    conf = _payload
                    # payload[index] = conf
                # payload.append(conf)
                ret.append(conf)

        # if payload != ret:
        #     print("Transform")
        #     pprint (ret)
        assert isinstance(ret, list)
        return ret

    def __init__(self, *args, node_obj=None, node_attr=None, node_conf=None, **kwargs):

        # Save arguments in instance
        self._obj = node_obj
        self._obj_attr = node_attr or self._obj_attr
        # setattr(self, f"{self._obj_attr}_conf", list(self._obj_conf))
        _obj_conf = node_conf or getattr(
            node_obj, f"{self._obj_attr}_conf", list(self._obj_conf)
        )
        self._obj_conf = self._transform(_obj_conf)

        # Sanity checks
        assert isinstance(self._obj_attr, str), f"Got: {self._obj_attr}"
        assert isinstance(self._obj_conf, list), f"Got: {self._obj_conf}"

        # Init controller
        self._mixin_dict = {}
        self._mixin_shortcuts = {}
        self._mixin_hooks = {
            "__getattr__": [],
            "child_create": [],
        }

        # Auto-Attach itself to parent, only works if a derived class of cafram actually :/
        self._obj_has_attr = False
        try:
            setattr(self._obj, self._obj_attr, self)
            self._obj_has_attr = True
            log.info(f"New Node attached to {self._obj} as '{self._obj_attr}'")
        except AttributeError:
            log.warning(f"WEAK Node linked to '{self._obj}' as '{self._obj_attr}'")

        # # Patch object __getattr__
        # self._obj_has_forward = False
        # #this = self
        # def func1(this, name):
        #     "Hook gettattr for top object"
        #     return self.mixin_get(name)
        #     # return getattr(this, name)

        # def func2(this, name):
        #     "Hook gettattr for top object"
        #     #pprint (self)
        #     #return self._node.mixin_get(name)

        #     # print ("OBJ ATTR", this._node)
        #     # pprint(this._node.__dict__)

        #     #print (this._node.value)
        #     #return this._node[name]
        #     return getattr( this._node, name)
        #     # return getattr(self, name)

        # self._obj.__class__.__getattr__ = types.MethodType(func2, self._obj)
        # #self._obj.__getattr__ = types.MethodType(func2, self._obj.__class__)
        # self._obj_has_forward = True

        # Instanciate mixins
        log.info(f"Instanciate mixins for: {self._obj}")
        for mixin_conf in self._obj_conf:

            assert isinstance(mixin_conf, dict), self._obj_conf

            # Retrieve mixin class
            mixin_name = mixin_conf.get("mixin")
            if isinstance(mixin_name, str):
                try:
                    mixin_cls = importlib.import_module(mixin_name)
                except ModuleNotFoundError as err:
                    msg = f"Impossible to add mixin: {mixin_name} from: {mixin_conf}"
                    raise errors.CaframException(msg)
            else:
                mixin_cls = mixin_name

            # Sanity checks
            assert issubclass(
                mixin_cls, BaseMixin
            ), f"Mixin class {mixin_cls} is not an instance of 'BaseMixin'"
            log.info(f"  Instanciate mixin: {type(self._obj)}, {mixin_conf}")

            # Instanciate mixin and register
            mixin_inst = mixin_cls(self, mixin_conf=mixin_conf, **kwargs)
            # self.mixin_set(mixin_inst, mixin_inst.instance, shortcut=False)
            self.mixin_register(mixin_inst)

        return

    def alias_register(self, name, value, override=False):
        "Register mixin instance"

        # Check overrides
        if not override:
            keys = self.mixin_list(mixin=False, shortcuts=False)
            if name in keys:
                msg = f"Alias name '{name}' is already taken"
                raise errors.CaframException(msg)

        # Register mixin
        self._mixin_shortcuts[name] = value

    def mixin_register(self, mixin_inst, override=False):
        "Register mixin instance"

        # Skip ephemeral instances
        name = mixin_inst.name
        if not name:
            return

        # Check overrides
        if not override:
            keys = self.mixin_list(mixin=False, shortcuts=False)
            if name in keys:
                msg = f"Mixin name instance '{name}' is already taken"
                raise errors.CaframException(msg)

        # Sanity check
        assert issubclass(mixin_inst.__class__, BaseMixin)

        # Register mixin
        self._mixin_dict[name] = mixin_inst

    def mixin_list(self, mixin=False, shortcuts=False):
        "Get mixin names"

        if not mixin and not shortcuts:
            mixin = True

        targets = []
        if mixin:
            targets.append(self._mixin_dict)
        if shortcuts:
            targets.append(self._mixin_shortcuts)

        ret = []
        for mixin_dict in targets:  # [self._mixin_dict, self._mixin_shortcuts]:
            ret.extend(list(mixin_dict.keys()))

        return ret

    def mixin_hooks(self, name, func=None):
        "Get mixin instance"

        # Strict mode
        if name not in self._mixin_hooks:
            msg = f"Unknown hook type: {name}"
            raise CaframException(msg)

        if name not in self._mixin_hooks:
            if func is None:
                return []

            self._mixin_hooks[name] = []

        if func is None:
            return self._mixin_hooks[name]

        log.info(f"Register hook {name} on {self._obj}: {func}")
        self._mixin_hooks[name].append(func)

    def mixin_get(self, name):
        "Get mixin instance"
        return getattr(self, name)

    # def mixin_set(self, mixin, name=None, override=False, shortcut=True):
    #     "Register mixin instance"
    #     name = name or getattr(mixin, "key", None)

    #     # Skip ephemeral instances
    #     if not name:
    #         return

    #     # Check overrides
    #     if not override:
    #         keys = list(self._mixin_dict.keys()) + list(self._mixin_shortcuts.keys())
    #         if name in keys:
    #             msg = f"Mixin name instance '{name}' is already taken"
    #             raise errors.CaframException(msg)

    #     # Sanity check
    #     if not shortcut:
    #         assert issubclass(mixin.__class__, BaseMixin)

    #     # Register mixin
    #     target = self._mixin_shortcuts if shortcut else self._mixin_dict
    #     target[name] = mixin

    def __getitem__(self, key):
        "Handle dict notation"
        return getattr(self, key)

    def __getattr__(self, name):

        # print ("GETATTR", name, self, self._obj)
        # pprint (self.__dict__)

        # Execute hooks
        for hook in self._mixin_hooks.get("__getattr__", []):
            found, result = hook(name)
            if found is True:
                return result

        # Look internally
        if name in self._mixin_dict:
            return self._mixin_dict[name]

        # Look shortcuts
        if name in self._mixin_shortcuts:
            return self._mixin_shortcuts[name]

        # Return error
        # print ("\nMISSING ATTR DUMP", name)
        # pprint (self.__dict__)
        msg = f"No such mixin '{name}' in {self}"
        raise errors.AttributeError(msg)
        # raise AttributeError(msg)
        # raise errors.CaframException(msg)

    # def __repr__(self):
    #     keys_mixins = self.mixin_list(mixin=True, shortcuts=False)
    #     keys_aliases = self.mixin_list(mixin=False, shortcuts=True)

    #     keys_mixins = ','.join(keys_mixins)
    #     keys_aliases = ','.join(keys_aliases)

    #     return f"Ctrl: <{self.__class__.__name__}:{hex(id(self))}>[{keys_mixins}|{keys_aliases}]"
    #     # return f"<{self.__class__.__module__} object at {hex(id(self))}> with mixins: {keys_mixins}|{keys_aliases}"

    def dump(self, details=False, doc=False, mixins=True, stdout=True):

        out = []

        out.append("")
        out.append("-" * 40)
        out.append(f"Dump of NodeCtrl:")

        out.append("")
        out.append(f"  Object type:")
        out.append(f"            attr == {self._obj_attr}")
        out.append(f"          linked == {self._obj_has_attr}")
        out.append(f"            type == {type(self._obj)}")
        out.append(f"           value == {self._obj}")
        out.append(
            f"          mixins == {self.mixin_list(mixin=True, shortcuts=False)}"
        )
        out.append(
            f"         aliases == {self.mixin_list(mixin=False, shortcuts=True)}"
        )

        out.append("")
        out.append("  Mixin Configs:")
        mixin_confs = self._obj_conf
        if isinstance(mixin_confs, list):
            for index, conf in enumerate(mixin_confs):
                out.append(f"    {index}:")
                for key, value in conf.items():
                    out.append(f"        {key:<12}: {value}")
        else:
            out.append(pformat(mixin_confs))

        out.append("")

        # Mixins part !
        ################
        out.append("")
        out.append("  Mixins Instances:")
        ignore = ["_schema"]

        for name, value in self._mixin_shortcuts.items():

            value_ = pformat(value)

            # Reformat ouput if more than 1 line
            if len(value_.split("\n")) > 1:
                value_ = "\n" + textwrap.indent(value_, "      ")

            out.append(f"    {name}: {value_}")

        for name, value in self._mixin_dict.items():
            out.append(f"    {name}:")
            if mixins:
                dump = value.dump(stdout=False, details=details, ignore=ignore)
                out.append(textwrap.indent(dump, "      "))

        out.append("-" * 40)
        out.append("")

        # pprint (out)

        ret = "\n".join(out)
        if stdout:
            print(ret)
        return ret
