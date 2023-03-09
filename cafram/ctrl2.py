"""
Node Controller Class
"""


# Imports
################################################################

import types
import importlib
import textwrap
import inspect

from pprint import pprint, pformat

from . import errors
from .mixins import BaseMixin
from .common import CaframCtrl, CaframNode
from .utils import SPrint
from .utils import SPrint

from .lib.utils import truncate

# Only relevant for entrypoints
# logging.basicConfig(level=logging.INFO)

# log = logging.getLogger(__name__)
# log = logging.getLogger("cafram2")



# functions
################################################################




# NodeCtrl Public classe
################################################################


class NodeCtrl(CaframCtrl):
    "NodeCtrl Class, primary object to interact on Nodes"

    # Deprecated !!!
    _obj_attr = "_node"

    # New config
    _obj_name = None
    _obj_prefix = "node"
    _obj_prefix_ctrl = f"_{_obj_prefix}" # Ie: _node__<mixin>__<conf_key>
    _obj_prefix_conf = f"_{_obj_prefix}__" # Ie: _node__<mixin>__<conf_key>
    _obj_prefix_method = f"_{_obj_prefix}" # Ie: _node__<mixin>__transform


    

    # Other example config
    # _obj_prefix_conf = f"_" # Ie: _<mixin>__<conf_key>
    # _obj_prefix_method = f"_" # Ie: _<mixin>__transform
    # _obj_prefix_conf = "" # Ie: <mixin>__<conf_key>
    # _obj_prefix_method = "" # Ie: <mixin>__transform
    
    _obj_conf = {}

    # Controller initialization
    # -------------------


    # def get_obj_mixin_attr(self, key, name):
    #     """Scan an object for a given attribute
    #     """

    #     prefix = f"{self._obj_prefix_method}_" if self._obj_prefix_method else ""

    #     obj = self._obj
    #     if not obj:
    #         return None

    #     middle = f"{key}__" if key else ""
    #     name = f"{prefix}{middle}{name}"
    #     ret = getattr(obj, name, None)
    #     #self._log.debug(f"Fetch obj attr '{name}': {ret}")
    #     return ret


    def get_dict_node_config(self, prefix, payload):
        """Extract from dict all keys starting with prefix
        """
        prefix = prefix or ""
        if prefix:
            prefix += "_"

        ret = {}
        for key, val in payload.items():
            if key.startswith(prefix):
                key_name = key.replace(prefix, "")
                ret[key_name] = val

        return ret
        # return {key: value for key, value in payload.items() if key.startswith(prefix)}

    def get_obj_node_config(self, prefix):
        """Scan object and return a Node config
        
        format:
            - "(PREFIX)_(CONF)"
        """
        prefix = prefix or ""
        obj = self._obj
        if not obj:
            return {}

        ret = {}
        for attr in dir(obj):
            if attr.startswith(prefix):
                short_name = attr.replace(prefix, "")
                if not short_name.startswith("_"):
                    ret[short_name] = getattr(obj, attr)

        return ret


    def get_obj_mixin_config(self, prefix=None):
        """Scan _obj and return a dict config
        
        format:
            - "(PREFIX)__(MIXIN_KEY)__(CONF)"
        """
        prefix = prefix or ""

        obj = self._obj
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
            parts = attr.split('__', 2)
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


    def _merge_mixin_configs(self, *args):
        "Merge all mixins configs given in args"

        ret = {}
        for conf in args:
            for key, value in conf.items():
                if not key in ret:
                    ret[key] = {}
                #self._log.debug(f"Merge NodeCtrl mixins '{key}' with: {value}")
                ret[key].update(value)

        return ret





    def __init__(self, *args, node_obj=None, **kwargs):

        # Save object internally
        self._obj = node_obj
            
        # Extract Node config:
        # ---------------------

        # Get Node config from obj class (Static)
        obj_conf = self.get_obj_node_config(f"{self._obj_prefix_ctrl}_")

        # Get Node config from params (Syn)
        param_conf = self.get_dict_node_config(self._obj_prefix, kwargs)
        
        # Register Node config
        tmp_prefix = "_obj_"
        stores = { "class": obj_conf, "params": param_conf}

        # print ("NODE CONFIG")
        # pprint (stores)
        log_msg = []
        for store_name, store in stores.items():
            
            for key, value in store.items():
                name = f"{tmp_prefix}{key}"
                log_msg.append(f"Register {store_name} conf '{name}': {truncate(value)}")
                setattr(self, name, value)

        self._init_logger()
        for line in log_msg:
            self._log.debug(line)


        # Extract mixins configs:
        # ---------------------

        # Extract mixins config from obj class (Static)
        cls_mixin = self.get_obj_mixin_config(self._obj_prefix_conf)            
        #cls_mixin = self.get_obj_mixin_config("conf")            
        # Extract mixins config from Node config (Dyn)
        conf_mixin = self._transform_obj_conf(obj_conf.get("conf", {}))

        # print ("MIXINS CONFIG")
        # tmp = {
        #     "cls_mixin": cls_mixin,
        #     "conf_mixin": conf_mixin,
        # }
        # pprint(tmp)
        

        # Register Mixin config
        self._obj_conf = self._merge_mixin_configs(cls_mixin, conf_mixin)


        # Sanity checks
        assert isinstance(self._obj_attr, str), f"Got: {self._obj_attr}"
        assert isinstance(self._obj_conf, dict), f"Got: {self._obj_conf}"

        # Init controller
        self._mixin_dict = {}
        self._mixin_shortcuts = {}
        self._mixin_hooks = {
            "__getattr__": [],

            # Require a proper loading order, should be loaded before the mixin children
            "child_create": [],

            # # Hooks names
            # "obj_": [],
            # "ctrl_": [],
            # "mixin_": [],

            # "obj__": [],
            # "ctrl__": [],
            # "mixin__": [],
            # # Sub keys
            # # obj___init__
            # # obj___getattr__
            # # ctrl__getattr__
            # # ctrl_children
            # # ctrl_init

        }

        # pprint (self.__dict__)

        # Auto-Attach itself to parent, only works if a derived class of cafram actually :/
        self._obj_has_attr = False
        try:
            self._log.debug(f"Attach NodeCtrl to {self._obj} as '{self._obj_attr}'")
            setattr(self._obj, self._obj_attr, self)
            self._obj_has_attr = True
        except AttributeError:
            self._log.warning(f"WEAK Node linked to '{self._obj}' as '{self._obj_attr}'")


        self._load_mixins(kwargs)

        # Instanciate parent _init()
        # TODO !!!
        #func = self.get_obj_mixin_attr(None, "init")
        #pprint (func)


        #####################################################

    def get_mixin_loadin_order(self):
        "Instanciate all mixins"

        mixin_classes = {}

        for mixin_name, mixin_conf in self._obj_conf.items():

            assert isinstance(mixin_conf, dict), mixin_conf

            # Retrieve mixin class
            mixin_ref = mixin_conf.get("mixin")
            if isinstance(mixin_ref, str):
                try:
                    mixin_cls = importlib.import_module(mixin_ref)
                except ModuleNotFoundError as err:
                    msg = f"Impossible to add mixin: {mixin_ref} from: {mixin_conf}"
                    raise errors.CaframException(msg)
            else:
                mixin_cls = mixin_ref

            # Sanity checks
            assert mixin_cls, f"Expected a Mixin class, not: {mixin_cls}"
            assert issubclass(
                mixin_cls, BaseMixin
            ), f"Mixin class {mixin_cls} is not an instance of 'BaseMixin', got: {mixin_cls}"


            loading_attr = "mixin_order"
            loading_order = int(mixin_conf.get(loading_attr, getattr(mixin_cls, loading_attr)))

            final = dict(mixin_conf)
            final["mixin"] = mixin_cls
            final["mixin_order"] = loading_order
            final["mixin_key"] = mixin_name
            final["key"] = mixin_name  # TEMPORARY
            mixin_classes[mixin_name] = final

        return mixin_classes


    def _load_mixins(self, kwargs):

        mixin_classes = self.get_mixin_loadin_order()
        load_order = sorted(mixin_classes, key=lambda key: mixin_classes[key]["mixin_order"])

        # Instanciate mixins
        self._log.info(f"Load mixins for {self._obj}: {load_order}")
        for mixin_name in load_order:

            mixin_conf = mixin_classes[mixin_name]
            mixin_cls = mixin_classes[mixin_name]["mixin"]
            
            # Instanciate mixin and register
            self._log.info(f"Instanciate mixin '{mixin_name}': {mixin_cls.__name__}")
            mixin_inst = mixin_cls(self, 
                mixin_conf=mixin_conf, 
                **kwargs)
            self.mixin_register(mixin_inst)

        #####################################################




    def _transform_obj_conf(self, payload):
        "Transform NodeCtl config"

        attr_ident = "mixin_key"

        ret = payload
        if isinstance(payload, dict):
            ret = {}
            for index, conf in payload.items():
                # Convert short forms
                if not isinstance(conf, dict):
                    _payload = {
                        "mixin": conf,
                    }
                    conf = _payload

                # Auto set name
                name = index or conf.get(attr_ident, getattr(conf["mixin"], attr_ident))
                conf[attr_ident] = name

                # Append to mixin config
                ret[name] = conf

        elif isinstance(payload, list):
            ret = {}
            for index, conf in enumerate(payload):
                # Convert short forms
                if not isinstance(conf, dict):
                    _payload = {
                        "mixin": conf,
                    }
                    conf = _payload

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

    # Mixins and alias registration
    # -------------------

    def alias_register(self, name, value, override=False):
        "Register mixin instance"

        # Check overrides
        if not override:
            keys = self.mixin_list(mixin=False, shortcuts=False)
            if name in keys:
                msg = f"Alias name '{name}' is already taken"
                raise errors.CaframException(msg)

        # Register mixin
        self._log.info(f"Register alias '{name}': {truncate(value)}")
        self._mixin_shortcuts[name] = value

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
                pprint (self.__dict__)
                print (mixin_inst)
                print(self._obj)
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
            targets.append(self._mixin_shortcuts)

        ret = []
        for mixin_dict in targets:  # [self._mixin_dict, self._mixin_shortcuts]:
            ret.extend(list(mixin_dict.keys()))

        return ret

    def get_hooks(self, name):
        "Get hook"
        return self._mixin_hooks[name]

    def set_hooks(self, name, func=None):
        "Set hook"

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

        self._log.info(f"Register hook {name} on {self._obj}: {func}")
        self._mixin_hooks[name].append(func)

    def mixin_get(self, name):
        "Get mixin instance"
        return getattr(self, name)

    # Dunders
    # -------------------

    def __getitem__(self, key):
        "Handle dict notation"
        return getattr(self, key)

    def __getattr__(self, name):
        "Forward all NodeCtrl attributes to mixins"

        # Execute hooks
        #print ("GETATTR NODE_CTRL", name)
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
        msg = f"No such mixin '{name}' in {self}"
        raise errors.AttributeError(msg)

    # Troubleshooting
    # -------------------

    def dump(self, details=False, doc=False, mixins=True, stdout=True):
        "Dump the content of a NodeCtrl for troubleshouting purpose"

        sprint = SPrint()

        sprint("\n" + "-" * 40)
        sprint(f"Dump of NodeCtrl:")
        sprint(f"\n*  Object type:")
        sprint(f"     attr: {self._obj_attr}")
        sprint(f"   linked: {self._obj_has_attr}")
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
        for name, value in self._mixin_shortcuts.items():

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
