"""
Node Controller Class
"""


# Imports
################################################################

# import types
import textwrap

# pylint: disable=W0611
from pprint import pformat, pprint
from typing import Any, Dict, List, Optional, Union

from .. import errors
from ..common import CaframCtrl
from ..lib.sprint import SPrint
from ..lib.utils import import_module, truncate
from .comp import BaseMixin

# import inspect


# Only relevant for entrypoints
# logging.basicConfig(level=logging.INFO)

# log = logging.getLogger(__name__)
# log = logging.getLogger("cafram2")

logger = None

# functions
################################################################


# Create a parsable mixin configurations


def _prepare_mixin_conf(mixin_conf, mixin_name=None, mixin_order=None, strict=False):

    assert isinstance(mixin_conf, dict), mixin_conf

    # Retrieve mixin class
    mixin_ref = mixin_conf.get("mixin")
    # print ("MIXIN_CLS", mixin_name, mixin_ref)
    mixin_cls = None
    if isinstance(mixin_ref, str):
        try:
            mixin_cls = import_module(mixin_ref)
        except ModuleNotFoundError as err:
            msg = f"Impossible to add mixin: {mixin_ref} from: {mixin_conf} ({err})"
            raise errors.CaframException(msg) from err
    elif mixin_ref:
        mixin_cls = mixin_ref

    # Class data extraction
    mixin_key_ = None
    mixin_order_ = None

    if mixin_cls:
        assert issubclass(
            mixin_cls, BaseMixin
        ), f"Mixin class {mixin_cls} is not an instance of 'BaseMixin', got: {mixin_cls}"

        mixin_key_ = mixin_cls.mixin_key
        mixin_order_ = mixin_cls.mixin_order
    else:
        if strict:
            # Because as classes may define some default parameters for classes
            if logger:
                logger.info(f"Skip unloaded module: {mixin_name}")
            return None, None

    # Checks
    mixin_name = mixin_name or mixin_conf.get("mixin_key", mixin_key_)
    assert isinstance(mixin_name, str), f"Got: {mixin_name}"
    mixin_order = mixin_order or mixin_conf.get("mixin_order", mixin_order_)

    # Final configuration
    final = dict(mixin_conf)
    if mixin_cls:
        final["mixin"] = mixin_cls
    if mixin_order is not None:
        final["mixin_order"] = int(mixin_order)
    final["mixin_key"] = mixin_name

    return mixin_name, final


def get_mixin_loading_order(payload, logger=None, strict=False):
    "Instanciate all mixins"

    mixin_classes = {}

    if isinstance(payload, dict):
        for mixin_name, mixin_conf in payload.items():
            name, conf = _prepare_mixin_conf(mixin_conf, mixin_name, strict=strict)
            mixin_classes[name] = conf

    elif isinstance(payload, list):
        for index, mixin_conf in enumerate(payload):
            name, conf = _prepare_mixin_conf(
                mixin_conf, mixin_order=index, strict=strict
            )
            mixin_classes[name] = conf
    elif not payload:
        mixin_classes = {}
    else:
        assert False, "CONFIG BUG"

    # Sanity Checks
    if None in mixin_classes:
        pprint(mixin_classes)
        assert False, f"BUG, found None Key: {payload}"

    return mixin_classes


# NodeCtrl Public classe
################################################################


class NodeCtrl(CaframCtrl):
    "NodeCtrl Class, primary object to interact on Nodes"

    # Reference to the object (Required)
    _obj = None

    # Object name/ident? (optional)
    _obj_name = None

    # Name of the attribute to use to access the object
    _obj_attr = "__node__"

    # Configuration of object
    _obj_conf: Dict = {}

    def __init__(
        self,
        obj,  # Provide reference to object
        obj_mixins=None,  # Provide mixin configurations, should be a dict
        obj_attr="__node__",  # How the NodeCtrl is accessed from object
        obj_clean=False,  # Remove from object configuration settings
        # obj_prefix_mixin="n_",
        # obj_prefix_alias="a_",
        **mixin_kwargs,  # Options forwarded to ALL mixins
    ):
        """Instanciate new NodeCtl instance

        :param obj: The object where it is attached
        :type obj: Any

        :param obj_mixins: A dict with mixin configurations
        :type obj_mixins: dict

        :returns: a list of strings representing the header columns
        :rtype: list

        """

        # Respect OOP
        super().__init__(debug=None, impersonate=None, log_level=None)

        # Init Node Controller
        self._obj = obj
        self._obj_name = None
        self._obj_attr = obj_attr
        self._obj_mixins = obj_mixins or {}

        self._mixin_dict = {}
        self._mixin_aliases = {}
        self._mixin_hooks = {
            "__getattr__": [],
            # "child_create": [],
        }

        # Parent Obj Manipulation
        # ---------------------

        # Autoclean config?
        if obj_clean:
            delattr(self._obj, f"{self._obj_attr}_mixins__")
            delattr(self._obj, f"{self._obj_attr}_params__")

        # Auto-Attach itself to parent, only works if a derived class of cafram actually :/
        if obj_attr:
            self._log.debug(f"Attach {self} to {self._obj} as '{obj_attr}'")
            setattr(self._obj, obj_attr, self)

        # Init Ctrl
        # ---------------------
        # print ("MIXIN CONF", self._obj, mixin_kwargs)
        # pprint(self._obj_mixins)
        self._load_mixins(self._obj_mixins, mixin_kwargs)
        self._log.debug(f"NodeCtrl {self} initialization is over: {self._obj_mixins}")
        # print(f"NodeCtrl {self} initialization is over: {self._obj_mixins}")

    def _load_mixins(self, mixin_confs, mixin_kwargs):
        "Load mixins from requested configuration"

        mixin_classes = get_mixin_loading_order(
            mixin_confs, logger=self._log, strict=True
        )
        load_order = sorted(
            mixin_classes, key=lambda key: mixin_classes[key]["mixin_order"]
        )

        # Instanciate mixins
        self._log.info(f"Load mixins for {self._obj}: {load_order}")
        for mixin_name in load_order:

            mixin_conf = mixin_classes[mixin_name]
            mixin_cls = mixin_classes[mixin_name]["mixin"]

            # Instanciate mixin and register
            self._log.info(f"Instanciate mixin '{mixin_name}': {mixin_cls.__name__}")
            mixin_inst = mixin_cls(self, mixin_conf=mixin_conf, **mixin_kwargs)
            self.mixin_register(mixin_inst)

        #####################################################

    # Mixins and alias registration
    # -------------------

    def alias_register(self, name, value, override=False):
        "Register mixin instance"

        # Check overrides TOFIX: ALWAYS FAILURE !
        if not override:
            keys = self.mixin_list(mixin=False, shortcuts=False)
            if name in keys:
                msg = f"Alias name '{name}' is already taken"
                raise errors.CaframException(msg)

        # Register mixin
        self._log.info(f"Register alias '{name}': {truncate(value)}")

        if name in self._mixin_aliases:
            msg = (
                f"Aliase: '{name}' is already defined for: {self._mixin_aliases[name]}"
            )
            print("ERROR: " + msg)
            print("TOFIX: Currently loaded mixins/aliases:")
            tmp = {
                "__node__": {
                    "_mixin_dict": self._mixin_dict,
                    "_mixin_aliases": self._mixin_aliases,
                }
            }
            pprint(tmp)
            assert name not in self._mixin_aliases, msg

        self._mixin_aliases[name] = value

    def mixin_register(self, mixin_inst, override=False):
        "Register mixin instance"

        # Skip ephemeral instances
        name = mixin_inst.mixin_key
        if not name:
            return

        # Check overrides
        if not override:
            keys = self.mixin_list(mixin=False, shortcuts=False)
            if name in keys:
                # pprint (self.__dict__)
                # print (mixin_inst)
                # print(self._obj)
                msg = f"Mixin name instance '{name}' is already taken"
                raise errors.CaframException(msg)

        # Sanity check
        assert issubclass(mixin_inst.__class__, BaseMixin)

        # Register mixin
        self._log.info(f"Register mixin '{name}': {mixin_inst}")
        self._mixin_dict[name] = mixin_inst

    def mixin_list(self, mixin=False, shortcuts=False):
        "Get mixin names"

        if not mixin and not shortcuts:
            mixin = True

        targets = []
        if mixin:
            targets.append(self._mixin_dict)
        if shortcuts:
            targets.append(self._mixin_aliases)

        ret = []
        for mixin_dict in targets:  # [self._mixin_dict, self._mixin_aliases]:
            ret.extend(list(mixin_dict.keys()))

        return ret

    def get_hooks(self, name=None):
        "Get hook"
        if name:
            return self._mixin_hooks[name]
        return self._mixin_hooks

    def mixin_get(self, name):
        "Get mixin instance"

        # Execute hooks
        for hook in self._mixin_hooks.get("__getattr__", []):
            found, result = hook(name)
            if found is True:
                return result

        # Look internally
        if name in self._mixin_dict:
            return self._mixin_dict[name]

        # Look shortcuts
        if name in self._mixin_aliases:
            return self._mixin_aliases[name]

        # Return error
        msg = f"No such mixin '{name}' in {self}"
        raise errors.AttributeError(msg)

    # Dunders
    # -------------------

    def __getitem__(self, name):
        "Handle dict notation"
        return self.mixin_get(name)

    def __getattr__(self, name):
        "Forward all NodeCtrl attributes to mixins"
        ret = self.mixin_get(name)
        return ret

    # Troubleshooting
    # -------------------

    def dump(self, details=False, mixins=True, stdout=True):
        "Dump the content of a NodeCtrl for troubleshouting purpose"

        sprint = SPrint()

        sprint("\n" + "-" * 40)
        sprint("Dump of NodeCtrl:")
        sprint("\n*  Object type:")
        sprint(f"     attr: {self._obj_attr}")
        # sprint(f"   linked: {self._obj_has_attr}")
        sprint(f"     type: {type(self._obj)}")
        sprint(f"    value: {self._obj}")
        sprint(f"   mixins: {self.mixin_list(mixin=True, shortcuts=False)}")
        sprint(f"  aliases: {self.mixin_list(mixin=False, shortcuts=True)}")

        sprint("\n*  Mixin Configs:")
        mixin_confs = self._obj_conf
        if isinstance(mixin_confs, list):
            for index, conf in enumerate(mixin_confs):
                sprint(f"    [{index}]:")
                for key, value in conf.items():
                    sprint(f"         {key:<12}: {value}")
        else:
            sprint(pformat(mixin_confs))

        # Aliases part
        ignore = ["_schema"]
        sprint("\n*  Mixins Aliases:")
        for name, value in self._mixin_aliases.items():

            value_ = pformat(value)

            # Reformat ouput if more than 1 line
            if len(value_.split("\n")) > 1:
                value_ = "\n" + textwrap.indent(value_, "      ")

            sprint(f"    [{name}]: {value_}")

        # Mixins part
        sprint("\n*  Mixins Instances:")
        for name, value in self._mixin_dict.items():
            sprint(f"    [{name}]:")
            if mixins:
                dump = value.dump(stdout=False, details=details, ignore=ignore)
                sprint(textwrap.indent(dump, "      "))

        sprint("-" * 40 + "\n")
        sprint.render(stdout=stdout)
