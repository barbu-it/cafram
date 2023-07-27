"""
Node Controller Class
"""


# Imports
################################################################

import inspect

# import types
import textwrap
import weakref

# pylint: disable=W0611
from pprint import pformat, pprint
from typing import Any, Dict, List, Optional, Union

import cafram.nodes.errors as errors
from cafram.lib.utils import import_module, merge_dicts, merge_keyed_dicts, truncate

from ..common import CaframCtrl
from ..lib.sprint import SPrint
from .comp import BaseMixin

# import inspect


# Only relevant for entrypoints
# logging.basicConfig(level=logging.INFO)

# log = logging.getLogger(__name__)
# log = logging.getLogger("cafram2")

BETA_WEAK_REF = True

logger = None

# functions
################################################################


# Create a parsable mixin configurations


def _prepare_mixin_conf(mixin_conf, mixin_name=None, mixin_order=None, lazy=False):

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
            raise errors.MixinImportError(msg) from err

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
        if not lazy:
            assert False, f"Can't load mixin conf: {mixin_conf}"

        # if strict:
        #     # Because as classes may define some default parameters for classes
        #     if logger:
        #         logger.info(f"Skip unloaded module: {mixin_name}")
        #     return None, None

    # Checks
    mixin_name = mixin_name or mixin_conf.get("mixin_key", mixin_key_)
    mixin_order = mixin_order or mixin_conf.get("mixin_order", mixin_order_)

    # Final configuration
    final = dict(mixin_conf)
    final["mixin_key"] = mixin_name
    if mixin_cls:
        final["mixin"] = mixin_cls
    if mixin_order is not None:
        final["mixin_order"] = int(mixin_order)

    assert isinstance(mixin_name, str), f"Got: {mixin_name}"

    return mixin_name, final


def mixin_get_loading_order(payload, logger=None):
    "Instanciate all mixins"

    assert isinstance(payload, dict)

    mixin_classes = {}
    for mixin_name, mixin_conf in payload.items():
        name, conf = _prepare_mixin_conf(mixin_conf, mixin_name, lazy=False)
        mixin_classes[name] = conf

    # Sanity Checks
    if None in mixin_classes:
        pprint(payload)
        pprint(mixin_classes)
        assert False, f"BUG, found None Key"

    return mixin_classes


# NodeCtrl Config Parser classe
################################################################


class Bunch(dict):
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self


class PrefixMgr:
    "Prefix Manager/Resolver"

    prefix = None
    _prefixes = None

    def __init__(self, prefix="__node__"):

        self.prefix = prefix

        self._prefixes = self.get_prefixes(prefix)
        for key, val in self._prefixes.items():
            setattr(self, key, val)

        # assert self.prefix, self.prefix

    @staticmethod
    def get_prefixes(prefix, strip=False):
        "Return prefixes from prefix"

        if not prefix:
            ret = Bunch(
                prefix=prefix,
                config_param=None,
                config_mixin=None,
                decorator_param=None,
                decorator_mixin=None,
            )
            return ret

        # BETA
        oprefix = prefix
        if strip:
            prefix = prefix.rstrip("_")

        # Future !!!
        # ====================
        # ret2 = Bunch(
        #     prefix=oprefix,
        #     config_param = f"{prefix}_",
        #     config_mixin = f"{prefix}__",
        #     decorator_param = f"{prefix}_params",
        #     decorator_mixin = f"{prefix}_mixins",
        # )

        ret2 = Bunch(
            prefix=oprefix,
            config_param=f"{prefix}_param_",
            config_mixin=f"{prefix}__mixin__",
            decorator_param=f"{prefix}_params__",
            decorator_mixin=f"{prefix}_mixins__",
        )

        return ret2


class ConfigParser(PrefixMgr):
    "NodeCtrl Configuration Builder"

    @staticmethod
    def _obj_filter_attrs_by(
        obj, prefix, suffix=None, strip=True, rtrim="_", level_max=0, level_split="__"
    ):
        "Filter all class attributes starting/ending with and return a dict with their value"

        # print (prefix)
        # pprint (dir(obj))

        if prefix is None:
            return {}
        elif not isinstance(prefix, str):
            assert False, "BUG HERE"

        ret = {}
        for attr in dir(obj):

            # Skip unmatching names
            if prefix and not attr.startswith(prefix):
                # print ("IGNORE prefix", prefix, attr)
                continue
            if suffix and not attr.endswith(suffix):
                # print ("IGNORE sufix", suffix, attr)
                continue

            # Remove prefix and suffix
            name = attr
            if strip:
                if prefix:
                    name = attr[len(prefix) :]
                if suffix:
                    name = attr[: len(suffix)]

            # Remove extra end chars
            if rtrim:
                name = name.rstrip(rtrim)

            if name:

                # print ("==> OBJ SCAN", attr, name, "=>", getattr(obj, attr))

                if level_max:
                    parts = name.split(level_split, level_max)

                    target = ret
                    for part in parts[:-1]:
                        if not part in target:
                            target[part] = {}
                        target = target[part]
                    # print ("PROCESS part", prefix, attr, name)
                    target[parts[-1]] = getattr(obj, attr)

                else:

                    # print ("PROCESS flat", prefix, attr, name)
                    # If value is None, then replace
                    assert (
                        name not in ret
                    ), f"Duplicate key: {attr}/{name} for object: {obj}"
                    ret[name] = getattr(obj, attr)

        if None in ret:
            assert "BUG", ret

        # print ("==> OBJ ATTR SCAN RESULT", obj, prefix, suffix)
        # pprint (ret)

        return ret

    @staticmethod
    def ensure_mixin_config(payload):
        "Instanciate all mixins"

        ret = {}

        if isinstance(payload, dict):
            ret = payload
        elif isinstance(payload, list):
            for index, mixin_conf in enumerate(payload):

                if isinstance(mixin_conf, str):
                    mixin_conf = {"mixin": mixin_conf}
                name, conf = _prepare_mixin_conf(
                    mixin_conf, mixin_order=index, lazy=True
                )
                ret[name] = conf
        elif not payload:
            ret = {}
        else:
            assert False, f"Bug here, unknown configuration: {payload}"

        return ret

    def get_configs(
        self,
        obj=None,
        kwargs=None,
        prefixes=None,
    ):
        "Return object vonfig from prefixes"

        prefixes = prefixes or self.get_prefixes(self.prefix)

        kwargs = kwargs or {}
        assert isinstance(prefixes, dict)
        assert isinstance(kwargs, dict)

        # 1. From inheritable attributes
        param_cls_prefix = self._obj_filter_attrs_by(obj, prefixes.config_param)
        mixin_cls_prefix = self._obj_filter_attrs_by(
            obj, prefixes.config_mixin, level_max=1
        )
        mixin_cls_prefix = self.ensure_mixin_config(mixin_cls_prefix)

        assert isinstance(mixin_cls_prefix, dict)
        mixin_cls_prefix = merge_keyed_dicts(
            mixin_cls_prefix, param_cls_prefix.get("obj_mixins", {})
        )

        # 2. From decorator attributes
        param_cls_attrs = {}
        if prefixes.decorator_param:
            param_cls_attrs = getattr(obj, prefixes.decorator_param, {})

        mixin_cls_attrs = {}
        if prefixes.decorator_mixin:
            mixin_cls_attrs = getattr(obj, prefixes.decorator_mixin, {})
            mixin_cls_attrs = self.ensure_mixin_config(mixin_cls_attrs)

        assert isinstance(mixin_cls_attrs, dict)
        # mixin_cls_attrs = merge_keyed_dicts(mixin_cls_attrs, param_cls_attrs.get("obj_mixins", {}))
        # V2: Make params obj_conf as default instead of override like in attrs
        mixin_cls_attrs = merge_keyed_dicts(
            param_cls_attrs.get("obj_mixins", {}), mixin_cls_attrs
        )

        # 3. From kwargs
        param_kwargs = kwargs  # {key: val for key, val in kwargs.items() if key.startswith("obj_")}
        mixin_kwargs = param_kwargs.get("obj_mixins", None)
        mixin_kwargs = self.ensure_mixin_config(mixin_kwargs)

        # 4. Build final configuration
        node_params = merge_dicts(param_cls_prefix, param_cls_attrs, param_kwargs)
        mixin_conf = merge_keyed_dicts(mixin_cls_prefix, mixin_cls_attrs, mixin_kwargs)
        node_params["obj_mixins"] = mixin_conf

        return node_params

    @staticmethod
    def inject_conf(nodectrl, conf=None):

        conf = conf or {}
        assert isinstance(conf, dict)

        # Inject nodeCtrl config
        cleaned_keys = []
        for key, val in conf.items():
            if key.startswith("obj_"):
                assert hasattr(nodectrl, f"_{key}"), f"Missing NodeCtrl key: _{key}"
                setattr(nodectrl, f"_{key}", val)
                cleaned_keys.append(key)

        # Clean consumed keys
        for key in cleaned_keys:
            if key in conf:
                del conf[key]

        return conf

    @staticmethod
    def mixin_get_loading_order(payload, logger=None):
        "Instanciate all mixins"

        assert isinstance(payload, dict)

        mixin_classes = {}
        for mixin_name, mixin_conf in payload.items():
            name, conf = _prepare_mixin_conf(mixin_conf, mixin_name, lazy=False)
            mixin_classes[name] = conf

        # Sanity Checks
        if None in mixin_classes:
            pprint(payload)
            pprint(mixin_classes)
            assert False, f"BUG, found None Key"

        return mixin_classes


# NodeCtrl Public classe
################################################################


class AliasReference:
    """Temporary proxy wrapper"""

    def __init__(self, obj, key=None, attr=None, desc=None, updatable=False):
        self.obj = obj
        self.key = key
        self.attr = attr
        self.desc = desc or "UNSET"
        self.updatable = updatable

    def __repr__(self):
        return f"AliasReference to mixin: {self.desc}[{self.key}]"

    def resolve(self):
        "Method to get the value of the proxied object"

        if self.key:
            return self.obj[self.key]
        elif self.attr:
            return getattr(self.obj, self.attr)
        else:
            assert False, "Bug, missing attr or key!"

    def update(self, value):
        "Method to allow to change value (if allowed)"

        if not self.updatable:
            raise errors.ReadOnlyAlias(f"Alias '{self.key}' is not updatable!")

        if self.key:
            self.obj[self.key] = value
        elif self.attr:
            setattr(self.obj, self.attr, value)
        else:
            assert False, "Bug, missing attr or key!"


class NodeCtrl(CaframCtrl):
    "NodeCtrl Class, primary object to interact on Nodes"

    # Reference to the object (Required)
    _obj = None

    # Object name/ident? (optional)
    _obj_name = None

    # Name of the attribute to use to access the object
    _obj_attr = "__node__"

    # Configuration of object
    _obj_conf: Dict = {}  # DEPRECATED
    _obj_mixins: Dict = {}

    _obj_wrapper_class = None

    _obj_clean = False

    def __init__(
        self,
        obj,  # Provide reference to object
        *args,
        # obj_mixins=None,  # Provide mixin configurations, should be a dict
        obj_attr="__node__",  # How the NodeCtrl is accessed from object
        # obj_clean=False,  # Remove from object configuration settings
        # obj_wrapper_class=None,  # Wrapper class to use for children
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

        # Fetch Node Params
        # --------------------------
        oconf = ConfigParser(prefix=obj_attr)
        _conf = oconf.get_configs(obj=obj, kwargs=mixin_kwargs)
        mixin_kwargs = oconf.inject_conf(self, conf=_conf)

        # Init Node Controller
        # --------------------------

        # Attach object to NodeCtrl
        if BETA_WEAK_REF:
            try:
                self._obj = weakref.proxy(obj)
            except TypeError as err:
                if obj_attr:
                    msg = f"Impossible to link '{obj_attr}' attribute to {self._obj}. Please set obj_attr=None to allow NodeCtrl to be used."
                    raise errors.NotMappingObject(msg) from err
        else:
            self._obj = obj

        # Attach NodeCtrl to object
        if obj_attr:
            self._log.debug(f"Attach {self} to {self._obj} as '{obj_attr}'")
            # TODO: Test for __dict__ presence instead ?
            try:
                setattr(self._obj, obj_attr, self)
            except AttributeError as err:
                msg = f"Impossible to add '{obj_attr}' attribute to {self._obj}. Please set obj_attr=None to allow NodeCtrl to be used."
                raise errors.NotMappingObject(msg) from err

        # NodeCtrl
        # --------------------------
        self._obj_attr = obj_attr
        self._mixin_dict = {}
        self._mixin_aliases = {}
        self._mixin_hooks = {
            "__getattr__": [],
            # "child_create": [],
        }

        # Parent Obj Manipulation
        # --------------------------

        # Autoclean config?
        if self._obj_clean:
            delattr(self._obj, f"{self._obj_attr}_mixins__")
            delattr(self._obj, f"{self._obj_attr}_params__")

        # Init Ctrl
        # --------------------------
        # print ("MIXIN CONF", self._obj, mixin_kwargs)
        # pprint(self._obj_mixins)
        self._load_mixins(self._obj_mixins, mixin_kwargs)
        self._log.debug(f"NodeCtrl {self} initialization is over: {self._obj_mixins}")
        # print(f"NodeCtrl {self} initialization is over: {self._obj_mixins}")

        self._load_post_init(args, mixin_kwargs)

    def _load_post_init(self, args, kwargs):
        "Load object __post_init__ method"

        obj = self._obj
        if hasattr(obj, "__post_init__"):
            try:
                obj.__post_init__(*args, **kwargs)
            except TypeError as err:

                fn_details = inspect.getfullargspec(obj.__post_init__)
                msg = f"{err}.\nFirst argument is self: {obj}\nCallable signature: {fn_details}\n"
                if not fn_details.varargs or not fn_details.varkw:
                    msg = f"Missing *args or **kwargs in __post_init__ method of {obj}"

                raise errors.BadArguments(msg) from err

    def _load_mixins(self, mixin_confs, mixin_kwargs):
        "Load mixins from requested configuration"

        assert isinstance(mixin_confs, dict)

        # mixin_classes = {}
        # for mixin_name, mixin_conf in mixin_confs.items():
        #     name, conf = _prepare_mixin_conf(mixin_conf, mixin_name, lazy=False)
        #     mixin_classes[name] = conf

        mixin_classes = mixin_get_loading_order(mixin_confs, logger=self._log)
        load_order = sorted(
            mixin_classes, key=lambda key: mixin_classes[key]["mixin_order"]
        )

        # print (">>>> LOAD NODE", self.get_obj())

        # Instanciate mixins
        self._log.info(f"Load mixins for {self._obj}: {load_order}")
        for mixin_name in load_order:

            mixin_conf = mixin_classes[mixin_name]
            mixin_cls = mixin_classes[mixin_name]["mixin"]

            # Instanciate mixin and register

            self._log.info(f"Instanciate mixin '{mixin_name}': {mixin_cls.__name__}")

            # print ("========== LOAD MXIN", mixin_cls, mixin_kwargs)
            mixin_inst = mixin_cls(self, mixin_conf=mixin_conf, **mixin_kwargs)
            self.mixin_register(mixin_inst)

        #####################################################

    # Mixins and alias registration
    # -------------------

    def alias_register(self, name, value, override=False):
        "Register mixin alias"

        # Check overrides TOFIX: ALWAYS FAILURE !
        if not override:
            keys = self.mixin_list(mixin=False, shortcuts=False)
            if name in keys:
                msg = f"Alias name '{name}' is already taken"
                raise errors.AlreadyDefinedAlias(msg)

        # Register mixin
        self._log.info(f"Register alias '{name}': {truncate(value)}")

        self._mixin_aliases[name] = value

    def alias_list(self):
        "List aliases names"

        return list(self._mixin_aliases)

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
                raise errors.AlreadyDefinedMixin(msg)

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

    def hooks_get(self, name=None):
        "Get hook"
        if name:
            return self._mixin_hooks[name]
        return self._mixin_hooks

    def alias_get(self, name):
        "Get alias instance"

        # Forward to nodectrl
        if name in self.__class__.__dict__:
            return getattr(self, name)

        # Look shortcuts
        if name in self._mixin_aliases:
            val = self._mixin_aliases[name]
            if isinstance(val, AliasReference):
                return val.resolve()
            return val

        # Return error
        msg = f"No such alias '{name}' in {self}"
        raise errors.MissingAlias(msg)

    def mixin_get(self, *args):
        "Get mixin instance"

        no_fail = False
        if len(args) == 1:
            name = args[0]
        elif len(args) == 2:
            name = args[0]
            default = args[1]
            no_fail = True
        else:
            assert False, f"Error on calling mixin_get: {args}"

        if name is None:
            # Return nodectrl when no args
            return self

        # Look internally
        if name in self._mixin_dict:
            return self._mixin_dict[name]

        # Forward to nodectrl
        if name in self.__class__.__dict__:
            return getattr(self, name)

        # Return error
        if no_fail:
            return default

        msg = f"No such mixin '{name}' in {self}"
        raise errors.MissingMixin(msg)

    def node_get(self, name):
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
            val = self._mixin_aliases[name]
            if isinstance(val, AliasReference):
                return val.resolve()
            return val

        # Forward to nodectrl
        if name in self.__class__.__dict__:
            return getattr(self, name)

        # Return error
        msg = f"No such mixin, alias or method called: '{name}' in {self}"
        raise errors.MissingCtrlAttr(msg)

    def set_alias(self, name, value):
        "Get mixin instance"

        # Look shortcuts
        if name in self._mixin_aliases:
            val = self._mixin_aliases[name]
            if isinstance(val, AliasReference):
                return val.update(value)
            return val

        # Return error
        msg = f"No such alias '{name}' in {self}"
        raise errors.MissingAlias(msg)

    # Dunders
    # -------------------

    # def __getitem__(self, name):
    #     "Handle dict notation"
    #     return self.mixin_get(name)

    # def __getattr__(self, name):
    #     "Forward all NodeCtrl attributes to mixins"
    #     ret = self.mixin_get(name)
    #     return ret

    # Troubleshooting
    # -------------------

    def dev_help(self):
        "Help develop"

        mixin_list = self.mixin_list()
        alias_list = self.alias_list()

        mixin_list = ",".join([str(item) for item in mixin_list])
        alias_list = ",".join([str(item) for item in alias_list])

        ret = f"List of components: {mixin_list}; list of aliases: {alias_list}"
        return ret

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
