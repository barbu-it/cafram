"""
Cafram tools
"""

from pprint import pprint

from .nodes2 import Node
from .mixins import BaseMixin


from .lib.utils import merge_keyed_dicts, fdict_to_dict, merge_dicts


class ConfigLoader:
    "Generic Config Loader"

    def __init__(self, obj, kwargs=None, obj_src=None):

        self._obj = obj
        self._obj_src = obj_src or obj
        self._kwargs = kwargs or {}

    # Object instpection methods
    # ===========================

    def _obj_getattr(self, *args):
        "Return the target object attribute, simple getattr_wrapper"
        return getattr(self._obj_src, *args)

    def _obj_getattrs(self):
        "Return all attributes names"
        return dir(self._obj_src)

    def _obj_filter_attrs_by(self, prefix=None, suffix=None, strip=True):
        "Filter all class attributes starting/ending with and return a dict with their value"

        ret = {}
        for attr in self._obj_getattrs():

            if prefix and not attr.startswith(prefix):
                continue
            if suffix and not attr.startswith(suffix):
                continue

            # Remove prefix and suffix
            name = attr
            if strip:
                if prefix:
                    name = attr[len(prefix) :]
                if suffix:
                    name = attr[: len(suffix)]

            # If value is None, then replace
            ret[name] = self._obj_getattr(attr)

        return ret

    def _obj_update_attrs_from_conf(self, conf, creates=False):
        "Update object attributes from a dict. Fail if key does not already exists when create=False"
        conf = conf or {}

        for key, value in conf.items():

            value = self._obj_prepare_conf_value(value)

            if not creates:
                if not hasattr(self._obj, key):
                    print("OBJ", self._obj)
                    pprint(dir(self))
                    pprint(self.__dict__)
                    assert (
                        False
                    ), f"Unknown config option '{key}={value}' for mixin: {self._obj}"

            setattr(self._obj, key, value)

    def _obj_prepare_conf_value(self, value):
        "Trasnform values into comprehensible object"

        # Check for bound methods
        if callable(value) and hasattr(value, "__self__"):
            cls = value.__self__.__class__

            # If not a CaframMixin class, add mixin as second param
            # pylint: disable=cell-var-from-loop
            if not issubclass(cls, CaframMixin):
                _func = value

                def wrapper(*args, **kwargs):
                    return _func(self._obj, *args, **kwargs)

                value = wrapper

        return value


class MixinConfigLoader(ConfigLoader):
    "Config loader for Mixin"

    # def build_v1(self, mixin_conf=None, kwargs=None, save=True, strict=True):
    #     """Build Mixin Configuration from various sources

    #     Processing order:
    #     -------------------
    #     1. merge mixin_conf into instance attrs. Raise error if settings does not exists
    #     2. scan class attributes for kwargs_params/mixin_param__
    #         Extract relevant params from kwargs_params
    #         Inject params as attributes
    #     3. Scan aliases from class attrs and register them

    #     """
    #     conf_override, conf_update = self.build_config(mixin_conf=mixin_conf, kwargs=kwargs)
    #     #return self._build_aliases()

    #     if save:
    #         self._obj_update_attrs_from_conf(conf_override, creates=True)
    #         self._obj_update_attrs_from_conf(conf_update, creates=(not strict))

    #     return merge_dicts(conf_override, conf_update)

    def build(self, strict=True, save=True, **kwargs):
        """Build Mixin Configuration from various sources

        Processing order:
        -------------------
        1. merge mixin_conf into instance attrs. Raise error if settings does not exists
        2. scan class attributes for kwargs_params/mixin_param__
            Extract relevant params from kwargs_params
            Inject params as attributes
        3. Scan aliases from class attrs and register them

        """

        # Build core config
        conf_override, conf_update = self.build_config(**kwargs)

        # print ("RESULT")
        # pprint (
        #     {
        #         "conf_override": conf_override,
        #         "conf_update": conf_update,
        #     }
        # )

        if save:
            self._obj_update_attrs_from_conf(conf_override, creates=True)
            self._obj_update_attrs_from_conf(conf_update, creates=(not strict))

        return merge_dicts(conf_override, conf_update)

    def build_config(self, mixin_conf=None, kwargs=None):
        "Build Core Config"

        conf_override = {}
        conf_update = {}

        # Algorithm
        # ------------------------

        # 1. Read param config from class attrs: mixin_param__<ATTR> = <PARAM_NAME>
        param_config = self._obj_filter_attrs_by(prefix="mixin_param__", strip=False)
        if param_config:
            print("1. Update mixin conf from class")
            pprint(param_config)
            conf_update.update(param_config)

        # 2. Read config from __init__ kwargs:
        if mixin_conf:
            print("2. Update mixin conf from dict")
            pprint(mixin_conf)
            # self._obj_update_attrs_from_conf(mixin_conf, creates=False)
            conf_update.update(mixin_conf)

        # 3. Read live param config for kwargs
        _PREFIX = "mixin_param__"
        param_config = {
            key[len(_PREFIX) :]: val
            for key, val in conf_update.items()
            if key.startswith(_PREFIX)
        }
        param_config = {key: val if val else key for key, val in param_config.items()}

        kwargs_params = {
            key: kwargs[name] for key, name in param_config.items() if name in kwargs
        }
        if kwargs_params:
            print("3. Update mixin live params")
            pprint(kwargs_params)
            conf_update.update(kwargs_params)

        # 4. Build Alias config
        _PREFIX = "mixin_alias__"
        alias_config = self._obj_filter_attrs_by(prefix=_PREFIX)
        alias_config.update(
            {
                key[len(_PREFIX) :]: val
                for key, val in conf_update.items()
                if key.startswith(_PREFIX)
            }
        )
        alias_config = {key: val for key, val in alias_config.items() if val}

        if alias_config:
            print("4. Update alias config")
            pprint(alias_config)
            conf_update["BUILT_CONFIG"] = alias_config

        # print ("WIPPP MIXIN")
        # pprint (conf_update)
        # pprint (param_config)
        # pprint (kwargs_params)
        # assert False

        return conf_override, conf_update

        # param_config = self._obj_filter_attrs_by(prefix="mixin_param__")
        param_config = {
            key.replace("mixin_param__", ""): val
            for key, val in conf_update.items()
            if key.startswith("mixin_param__")
        }
        param_config.update(self._obj_filter_attrs_by(prefix="mixin_param__"))
        # Tweak to replace val by key if val is ~None
        print("PRE CLEAN")
        pprint(param_config)
        param_config = {key: val if val else key for key, val in param_config.items()}
        params = {
            key: kwargs[val] for key, val in param_config.items() if val in kwargs
        }

        # 3. Save into Mixin Attributes
        if params:
            print("1. Update mixin init params")
            pprint(kwargs)
            pprint(param_config)
            pprint(params)
        # self._obj_update_attrs_from_conf(params, creates=True)
        conf_override.update(params)

        # 4. Save alias config
        conf_update["BUILT_CONFIG"] = self._build_aliases()

        return conf_override, conf_update

    def _build_aliases(self):
        "Build Aliases Config"

        # 4. Parse alias config
        alias_config = self._obj_filter_attrs_by(prefix="mixin_alias__")
        if alias_config:
            print("3. Mixin alias config")
            pprint(alias_config)

        # Return alias_conf
        return alias_config


class NodeConfigLoader(ConfigLoader):
    "Config loader for Nodes"

    # def build(self, kwargs_mixins=None, kwargs=None, strict=True, save=True, **kwargs):
    def build(self, strict=True, save=True, **kwargs):
        """Build Node Configuration from various source of data

        Processing order:
        -------------------
        1. General config: (OVERRIDE)
            search for Node class nodectrl params with prefix _node__<ATTR>
                Assign result into nodectrl attrs
            search for decorator nodectrl params with prefix __node_params__
                Assign result into nodectrl attrs
            Append NodeCtrl kwargs
                Assign result into nodectrl attrs

        2. Mixin config (MERGED)
            search for Node class nodectrl params with prefix _node_mixin__<KEY>__<ATTR>
                Assign result into mixin_confs
            search for decorator nodectrl params with prefix __node_mixins__
                Assign result into mixin_confs
            Append NodeCtrl mixin_confs from kwargs
                Assign result into mixin_confs

        """

        # Build core config
        conf_override, conf_update = self.build_config(**kwargs)

        print("RESULT")
        pprint(
            {
                "conf_override": conf_override,
                "conf_update": conf_update,
            }
        )

        if save:
            self._obj_update_attrs_from_conf(conf_override, creates=True)
            self._obj_update_attrs_from_conf(conf_update, creates=(not strict))

        return merge_dicts(conf_override, conf_update)

    def build_config(self, kwargs=None, kwargs_mixins=None, strict=True):
        "Build Core Config"

        # Algorithm - NodeCtrl
        # ------------------------
        ret = {}

        # 1. Read config from class attributes: _node__<KEY> = <VALUE>
        nodectrl_conf = self._obj_filter_attrs_by(prefix="_node__")
        if nodectrl_conf:
            print("a.1. Update nodectrl conf from inherited class attr", strict)
            pprint(nodectrl_conf)
        # self._obj_update_attrs_from_conf(nodectrl_conf, creates=(not strict))
        ret.update(nodectrl_conf)

        # 2. Read config from class attribute: __node_params__ = {}
        nodectrl_conf = self._obj_getattr("__node_params__")
        if nodectrl_conf:
            print(
                "a.2. Update nodectrl conf from decorator class attr: __node_mixins__"
            )
            pprint(nodectrl_conf)
        # self._obj_update_attrs_from_conf(nodectrl_conf, creates=(not strict))
        ret.update(nodectrl_conf)

        # 3. Read config from __init__ kwargs: obj_.*
        if kwargs:
            print("a.3. Update nodectrl conf from kwargs")
            pprint(kwargs)
        # self._obj_update_attrs_from_conf(kwargs, creates=(not strict))
        ret.update(kwargs)

        # Build mixin configs
        mixin_config = self._build_mixins(kwargs_mixins=kwargs_mixins)

        ret["obj_conf"] = mixin_config

        return {}, ret

    def _build_mixins(self, kwargs_mixins=None):
        "Build Mixin Config"

        # Algorithm - MixinConfig
        # ------------------------
        ret = {}

        # 1. Read mixin_config from class attributes: _node_mixin__<KEY>__<ATTR> = <VALUE>
        mixin_confs = self._obj_filter_attrs_by(prefix="_node_mixin__")
        if mixin_confs:
            mixin_confs = fdict_to_dict(mixin_confs)
            print(
                "b.1. Update mixin conf from inherited class attr: _node_mixin__<KEY>__<ATTR> = <VALUE>"
            )
            pprint(mixin_confs)
            ret = merge_keyed_dicts(ret, mixin_confs)

        # 2. Read mixin_config from class attribute: __node_mixins__ = {}
        mixin_confs = self._obj_getattr("__node_mixins__")
        if mixin_confs:
            print(
                "b.2. Update nodectrl conf from decorator class attr: __node_mixins__"
            )
            pprint(mixin_confs)
            ret = merge_keyed_dicts(ret, mixin_confs)

        # 3. Read mixin_config from __init__ kwargs: {}
        mixin_confs = kwargs_mixins
        if mixin_confs:
            print("b.3. Update nodectrl conf from kwargs")
            pprint(mixin_confs)
            ret = merge_keyed_dicts(ret, mixin_confs)

        # Return mixin_conf
        return ret


class MixinLoader:
    "Helper class to instanciate a Mixin class"

    def __init__(self, mixin):

        # Prepare mixin
        self._mixin_src = mixin or BaseMixin
        self._mixin_src_name = self._mixin_src.name

        class MixinLoaderInst(self._mixin_src):
            name = "debug"

        # Instanciate empty node
        self._mixin = Node(node_conf=[MixinLoaderInst])
        self.ctrl = self._mixin._node

    def dump(self, **kwargs):
        "Execute mixin dump method"
        self._mixin.debug.dump(**kwargs)

    def doc(self, **kwargs):
        "Display mixin documentation"
        print(f"Default mixin name: {self._mixin_src_name} (instead of debug)\n")
        self._mixin.debug.doc(**kwargs)
