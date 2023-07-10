"""
Node Controller Class
"""


# Imports
################################################################

# import types
import importlib
import textwrap

# import inspect

from pprint import pprint, pformat

from . import errors
from .mixins import BaseMixin
from .common import CaframCtrl
from .lib.sprint import SPrint
from .lib.utils import truncate

# Only relevant for entrypoints
# logging.basicConfig(level=logging.INFO)

# log = logging.getLogger(__name__)
# log = logging.getLogger("cafram2")


# functions
################################################################


# NodeCtrl configuration getters

# DEPRECATED SHOULD BE MOVED AT DECORATOR LEVEL
def nodectrl_conf_from_attr(obj, prefix=None):
    """Scan object and return a Node config

    format:
        - "(PREFIX)_(CONF)"
    """
    prefix = prefix or ""
    if not obj:
        return {}

    ret = {}
    for attr in dir(obj):
        if attr.startswith(prefix):
            short_name = attr.replace(prefix, "")
            if not short_name.startswith("_"):
                ret[short_name] = getattr(obj, attr)

    return ret


# DEPRECATED SHOULD BE MOVED AT DECORATOR LEVEL
def mixin_conf_from_obj_attr(obj, prefix=None):
    """Scan _obj and return a dict config

    format:
        - "(PREFIX)__(MIXIN_KEY)__(CONF)"
    """
    prefix = prefix or ""

    if not obj:
        return {}

    ret = {}
    for attr in dir(obj):

        # Filter out uneeded vars
        attr_orig = attr
        if prefix:
            if not attr.startswith(prefix):
                continue

            attr = attr.replace(prefix, "", 1)

        # Parse var names
        parts = attr.split("__", 2)
        if len(parts) != 2:
            continue
        attr_name, attr_conf = parts[0], parts[1]
        if not attr_conf:
            continue

        # Save config
        if not attr_name in ret:
            ret[attr_name] = {}
        ret[attr_name][attr_conf] = getattr(obj, attr_orig)

    return ret


def nodectrl_conf_from_dict(payload, prefix=None):
    """Extract from dict all keys starting with prefix"""
    prefix = prefix or ""
    if prefix:
        prefix += "_"

    ret = {}
    for key, val in payload.items():

        if key.startswith(prefix):
            key_name = key.replace(prefix, "")
            ret[key_name] = val

    return ret


# nodectrl_conf_from_attr
# nodectrl_conf_from_dict

# Mixin configuration getters


def mixin_conf_from_obj_dict(payload):
    "Transform NodeCtl config"

    attr_ident = "mixin_key"

    ret = payload
    if isinstance(payload, dict):
        ret = {}
        for index, conf in payload.items():
            # Convert short forms
            if not isinstance(conf, dict):
                conf = {
                    "mixin": conf,
                    attr_ident: index,
                }

            # Auto set name
            name = index  # or conf.get(attr_ident, getattr(conf["mixin"], attr_ident))
            conf[attr_ident] = name

            # Append to mixin config
            ret[name] = conf

    elif isinstance(payload, list):
        # assert False, "List config is not supported anymore"
        ret = {}
        for index, conf in enumerate(payload):
            # Convert short forms
            if not isinstance(conf, dict):
                conf = {
                    "mixin": conf,
                }

            # Auto set name
            name = conf.get(attr_ident, getattr(conf["mixin"], attr_ident))
            conf[attr_ident] = name

            # Append to mixin config
            ret[name] = conf

    # if payload != ret:
    #     print("TRANSFFORM MIXIN CONFIG: ")
    #     pprint (payload)
    #     print ("TOOOO")
    #     pprint (ret)
    #     print("EOF")

    assert isinstance(ret, dict)
    return ret


def mixin_conf_merge(*args, logger=None):
    "Merge all mixins configs given in args"

    ret = {}
    for conf in args:
        for key, value in conf.items():
            if not key in ret:
                ret[key] = {}
            if logger:
                logger.debug(
                    f"Merge NodeCtrl mixins '{key}' with: {value} (BEFORE={ret[key]})"
                )
            ret[key].update(value)

    return ret


# Create a parsable mixin configurations


def get_mixin_loading_order(payload, logger=None):
    "Instanciate all mixins"

    assert isinstance(payload, dict), f"Got: {payload}"

    mixin_classes = {}

    for mixin_name, mixin_conf in payload.items():

        assert isinstance(mixin_conf, dict), mixin_conf

        # Retrieve mixin class
        mixin_ref = mixin_conf.get("mixin")
        if isinstance(mixin_ref, str):
            try:
                mixin_cls = importlib.import_module(mixin_ref)
            except ModuleNotFoundError as err:
                msg = f"Impossible to add mixin: {mixin_ref} from: {mixin_conf}"
                raise errors.CaframException(msg) from err
        else:
            mixin_cls = mixin_ref

        # Sanity checks
        if not mixin_cls:
            # Because as classes may define some default parameters for classes
            if logger:
                logger.info(f"Skip unloaded module: {mixin_name}")
            continue
            # assert mixin_cls, f"Expected a Mixin class, not: {mixin_cls}"

        assert issubclass(
            mixin_cls, BaseMixin
        ), f"Mixin class {mixin_cls} is not an instance of 'BaseMixin', got: {mixin_cls}"

        loading_attr = "mixin_order"
        loading_order = int(
            mixin_conf.get(loading_attr, getattr(mixin_cls, loading_attr))
        )

        final = dict(mixin_conf)
        final["mixin"] = mixin_cls
        final["mixin_order"] = loading_order
        final["mixin_key"] = mixin_name
        # final["key"] = mixin_name  # TEMPORARY
        mixin_classes[mixin_name] = final

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
    _obj_conf = {}

    # Deprecated !!!
    # ----
    # obj_attr
    # _obj_prefix = "node"
    # _obj_prefix_ctrl = f"_{_obj_prefix}"  # Ie: _node__<mixin>__<conf_key>
    # _obj_prefix_conf = f"_{_obj_prefix}__"  # Ie: _node__<mixin>__<conf_key>
    # _obj_prefix_method = f"_{_obj_prefix}"  # Ie: _node__<mixin>__transform

    # Other example config
    # _obj_prefix_conf = f"_" # Ie: _<mixin>__<conf_key>
    # _obj_prefix_method = f"_" # Ie: _<mixin>__transform
    # _obj_prefix_conf = "" # Ie: <mixin>__<conf_key>
    # _obj_prefix_method = "" # Ie: <mixin>__transform

    # Controller Initialization
    # -------------------

    # def __init__v1(self, *_,
    #     node_obj=None,      # Provide reference to object

    #     obj_conf = None,   # Provide mixin configurations, should be a dict
    #     obj_attr = None,   # How the NodeCtrl is accessed from object, default is "_node": obj._node...

    #     # DEprecated !
    #     obj_prefix="node",  # Prefix of the configs lookups
    #     obj_prefix_ctrl = None,      # NodeCtrl config from obj cls ...
    #     obj_prefix_conf = None,      # Mixin config from obj cls ...
    #     obj_prefix_method = None,  # Unused

    #     **kwargs):

    #     # Args:
    #     # BREAKING CHANGE obj_prefix = obj_prefix or self._obj_attr
    #     _obj_prefix_ctrl = obj_prefix_ctrl or f"_{obj_prefix}"  # Ie: _node__<mixin>__<conf_key>
    #     _obj_prefix_conf = obj_prefix_conf or f"_{obj_prefix}__"  # Ie: _node__<mixin>__<conf_key>
    #     _obj_prefix_method = obj_prefix_method or f"_{obj_prefix}"  # Ie: _node__<mixin>__transform

    #     obj_attr = obj_attr or self._obj_attr
    #     obj_conf_param = obj_conf or {}

    #     # Save settings

    #     # Init controller
    #     self._obj_attr = obj_attr
    #     self._mixin_dict = {}
    #     self._mixin_aliases = {}
    #     self._mixin_hooks = {
    #         "__getattr__": [],
    #         # Require a proper loading order, should be loaded before the mixin children
    #         "child_create": [],
    #         # # Hooks names
    #         # "obj_": [],
    #         # "ctrl_": [],
    #         # "mixin_": [],
    #         # "obj__": [],
    #         # "ctrl__": [],
    #         # "mixin__": [],
    #         # # Sub keys
    #         # # obj___init__
    #         # # obj___getattr__
    #         # # ctrl__getattr__
    #         # # ctrl_children
    #         # # ctrl_init
    #     }

    #     # Save object internally
    #     self._obj = node_obj
    #     #print (f"T1: Start new NodeCtrl for {node_obj}: {kwargs}")

    #     # Extract Node config:
    #     # ---------------------

    #     # Get Node config from obj class (Static) and params (Dyn)
    #     # Grab params from
    #     _obj_conf = nodectrl_conf_from_attr(
    #         self._obj,
    #         prefix=f"{_obj_prefix_ctrl}_"
    #     )
    #     _param_conf = nodectrl_conf_from_dict(
    #         kwargs,
    #         prefix=obj_prefix
    #     )

    #     # Register Node config
    #     tmp_prefix = "_obj_"
    #     stores = {"_obj_conf": _obj_conf, "_param_conf": _param_conf}
    #     # print (f"======== Ctrl Mgr Stores (obj_prefix={obj_prefix})")
    #     # pprint (stores)
    #     log_msg = []
    #     for store_name, store in stores.items():

    #         for key, value in store.items():
    #             name = f"{tmp_prefix}{key}"
    #             log_msg.append(
    #                 f"Register conf '{name}': {truncate(value)} (from store '{store_name}')"
    #             )
    #             setattr(self, name, value)

    #     self._init_logger()
    #     for line in log_msg:
    #         self._log.debug(line)
    #         #print ("YOOO", line)

    #     # pprint (self.__dict__)

    #     # Extract mixins configs:
    #     # ---------------------

    #     # Extract mixins config from obj class and params
    #     cls_mixin = mixin_conf_from_obj_attr(self._obj, prefix=_obj_prefix_conf)
    #     #print (f"VSSSS: {self._obj_conf} ANNNNNNNNNND {obj_conf_param}")
    #     conf_mixin = mixin_conf_from_obj_dict(self._obj_conf)
    #     # if conf_mixin:
    #     #     print ("Is this useful ???")
    #     #     assert False, conf_mixin

    #     conf_mixin2 = mixin_conf_from_obj_dict(obj_conf_param)
    #     #conf_mixin = _4_transform_obj_conf(_obj_conf)
    #     # Build and Register Mixin config
    #     self._obj_conf = mixin_conf_merge(cls_mixin, conf_mixin, conf_mixin2, logger=self._log)
    #     # print (f"VSSSS GIVES: {self._obj_conf}")

    #     # New names
    #     # mixin_conf_from_obj_attr
    #     # mixin_conf_from_obj_dict
    #     # mixin_conf_merge

    #     # Sanity checks
    #     assert isinstance(obj_attr, str), f"Got: {obj_attr}"
    #     assert isinstance(self._obj_conf, dict), f"Got: {self._obj_conf}"
    #     # print("NodeCtrl REcap", self._obj)
    #     # pprint(self._obj_conf)
    #     # print("---")

    #     # Parent Attach
    #     # ---------------------

    #     # Auto-Attach itself to parent, only works if a derived class of cafram actually :/
    #     self._obj_has_attr = False
    #     try:
    #         if getattr(self._obj, obj_attr, None) != self:
    #             self._log.debug(f"Attach {self} to {self._obj} as '{obj_attr}'")
    #             setattr(self._obj, obj_attr, self)
    #         self._obj_has_attr = True
    #     except AttributeError:
    #         self._log.warning(
    #             f"WEAK Node {self} linked to '{self._obj}' as '{obj_attr}'"
    #         )

    #     # Init Ctrl
    #     # ---------------------
    #     self._load_mixins(kwargs)
    #     self._log.debug(f"NodeCtrl {self} initialization is over")

    def __init__(
        self,
        obj,  # Provide reference to object
        obj_mixins=None,  # Provide mixin configurations, should be a dict
        obj_attr="__node__",  # How the NodeCtrl is accessed from object, default is "_node": obj._node...
        obj_clean=False,  # Remove from object configuration settings
        obj_prefix_mixin="n_",
        obj_prefix_alias="a_",
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
        self._obj_attr = obj_attr  # "__node__" #TODO: Make this variable ?
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
            delattr(self._obj, "__node__mixins__")
            delattr(self._obj, "__node__params__")

        # Auto-Attach itself to parent, only works if a derived class of cafram actually :/
        if obj_attr:
            self._log.debug(f"Attach {self} to {self._obj} as '{obj_attr}'")
            setattr(self._obj, obj_attr, self)

        # Init Ctrl
        # ---------------------
        # print ("MIXIN", self._obj_mixins, mixin_kwargs)
        self._load_mixins(self._obj_mixins, mixin_kwargs)
        self._log.debug(f"NodeCtrl {self} initialization is over: {obj_mixins}")

    def _load_mixins(self, mixin_confs, mixin_kwargs):
        "Load mixins from requested configuration"

        mixin_classes = get_mixin_loading_order(mixin_confs, logger=self._log)
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
            # print(f"MIXIN mixin {self} '{mixin_name}': {mixin_cls.__name__} with {mixin_kwargs} ({mixin_conf})")
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

        # TODO: Make this a failure !!!
        if name in self._mixin_aliases:
            msg = (
                f"Aliase: '{name}' is already defined for: {self._mixin_aliases[name]}"
            )
            print("ERROR: " + msg)
            # assert name not in self._mixin_aliases, msg
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

        # return getattr(self, name)

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

    def dump(self, details=False, doc=False, mixins=True, stdout=True):
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
