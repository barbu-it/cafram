import copy
import logging
import os
import traceback
from pprint import pprint

from cafram.nodes import Node, addMixin, newNode
from cafram.nodes.comp.base import LoggerMixin
from cafram.nodes.comp.hier import HierChildrenMixin, HierParentMixin
from cafram.nodes.comp.path import PathMixin
from cafram.nodes.comp.tree import (  # NodeConfDict,; NodeConfList,
    ConfDictMixin,
    ConfListMixin,
    ConfMixin,
    ConfOrderedMixin,
    ConfPathMixin,
)
from cafram.utils import get_logger

__name__ = "mySuperApp"


_log = logging.getLogger(__name__)
# _log.setLevel(logging.DEBUG)


# ====================================
# App Base Classes
# ====================================

# class FakeLogger():

#     enable = None

#     def _print(self, *args):
#         if self.enable is True:
#             print ("FakeLogger: ", *args)
#         elif self.enable is None:
#             _log.warning(*args)

#     info = _print
#     warning = _print
#     debug = _print
#     error = _print


class BaseApp(Node):
    "BaseApp"

    _node_debug = False

    # __getattr__ = Node.__getattr__

    # _node__logger__mixin = LoggerMixin
    # _node__logger__mixin_key = "log"
    # _node__logger__log_level = "DEBUG"
    # _node__logger__log_colors = False
    # _node__logger__log_sformat = "time"
    # _node__logger__log_sformat = "struct"

    # log = FakeLogger()
    # log = _log

    __node___mixin__logger__mixin__ = LoggerMixin
    # __node___mixin__logger__mixin_key__ = "logger"


class BaseAppNode(BaseApp):
    "BaseAppNode"


# class RandomClass():
#     "blip"

# pprint (Node.__dict__)
# pprint (Node.name)

# pprint (RandomClass.__dict__)
# pprint (RandomClass.name)
# assert False, "sdfsdhjf"

# class BaseAppNodeDict(BaseAppNode, NodeConfDict):
#     "BaseAppNodeDict"


# class BaseAppNodeList(BaseAppNode, NodeConfList):
#     "BaseAppNodeList"


# ====================================
# App Generic Configs Components
# ====================================


class ConfigKV(BaseAppNode):
    # _node__logger__mixin = LoggerMixin
    # _node__conf__mixin = ConfDictMixin

    _node_debug = False

    __node___mixins__ = {
        # "logger": {
        #     "mixin": LoggerMixin,
        # },
        "conf": {
            "mixin": ConfMixin,
        },
    }

    def __post_init__(self, *args, **kwargs):

        pprint(self)
        pprint(self.__node__.__dict__)

        self.log.info(f"KV config: {self.conf.index}={self.conf.value}")


class ConfigVars(BaseAppNode):

    __node___mixins__ = {
        # "logger": {
        #     "mixin": LoggerMixin,
        #     "log_sformat": "struct",
        # },
        "_conf": {"mixin": ConfDictMixin, "children": ConfigKV},
    }

    def _node___conf__preparse(self, mixin, payload):

        # print("PREPARSE PAYLOAD:")
        # pprint (payload)

        if isinstance(payload, dict):
            ret = []
            for key, value in payload.items():
                ret.append(
                    {
                        key: value,
                    }
                )

            return ret

        return payload


class ConfigPath(BaseAppNode):

    __node___mixins__ = {
        # "logger": {
        #     "mixin": LoggerMixin,
        # },
        "hier": {
            "mixin": HierParentMixin,
            # "_param_raw": "payload"
            # "root": "CWD",
            # "path": "self.name"
        },
        "path": {
            "mixin": ConfPathMixin,
            "_param_raw": "payload",
            # "root": "CWD",
            # "path": "self.name"
            "parent_path": "project_path",
        },
    }

    def __post_init__(self, *args, **kwargs):

        self.app = self.hier.get_parent_by_cls(MyApp)

        # Set Path from project path
        root_path = self.app.path.get_path()
        self.path.set_root_path(root_path)

        self.log.info(f"Config PATH: {self.path.raw}={self.path.get_path()}")
        print("RAW Path:", self.path.raw)
        print("Path Auto:", self.path.get_path())
        print("Abs Path:", self.path.get_abs())
        print("Rel Path:", self.path.get_rel())
        print("")

    def _node__path__preparse(self, mixin, payload):

        if not isinstance(payload, str):
            payload = "UNSET"

        return payload

    # Node Configuration
    # -------------------------
    # Class Configuration
    # -------------------------


# ====================================
# App Specific Configs Elements
# ====================================


class TagList(BaseAppNode):
    # _node__logger__mixin = LoggerMixin
    # _node__conf__mixin = ConfDictMixin

    __node___mixins__ = {
        "conf": {
            "mixin": ConfListMixin,
        },
    }

    def __post_init__(self, *args, **kwargs):
        self.log.debug(f"Tag config: {self.conf.index}={self.conf.value}")


class AppConfig(BaseAppNode):

    __node___mixins__ = {
        # "logger": {
        #     "mixin": LoggerMixin,
        #     "log_sformat": "struct",
        # },
        "_conf": {
            "mixin": ConfOrderedMixin,
            "children": {
                "namespace": ConfigKV,
                "vars": ConfigVars,
                "tags": TagList,
                "tags_prefix": TagList,
                "tags_suffix": TagList,
            },
        },
    }

    # _node__conf__default = {
    #     "namespace": None,
    #     "vars": {},
    #     "tag_prefix": None,
    #     "tag_suffix": None,
    # }


# ====================================
# App Sources
# ====================================


class AppSource(BaseAppNode):

    # Node Configuration
    # -------------------------

    __node___mixins__ = {
        "logger": {
            "mixin": LoggerMixin,
        },
        "conf": {
            "mixin": ConfDictMixin,
            # "mixin": ConfDictMixin,
            "children": ConfigKV,
            # "preparse": test_toto,
            # "preparse": __node__conf__preparse,  # TODO: Allow direct inheritance now
            #   "transform": __node__conf__transform, # TODO: Allow direct inheritance now
        },
    }

    __node__conf__default = {
        "name": "BUG HERE",
        "remote": None,
        "ref": "",
    }

    def __node___mixin__conf__preparse__(self, mixin, payload):  # MODE=wrap
        # print ("YEEEEEHHH", self, mixin, payload)
        # assert False, "OKKK VALIDATED"
        # old_val = copy.copy(payload)

        if isinstance(payload, str):
            npayload = {
                "name": payload,
            }
            # self.log.debug(f"Tranform source payload: {payload} => {npayload}")
            payload = npayload

        payload["remote"] = payload.get("remote", f"./{payload['name']}")

        assert "name" in payload, payload
        assert "remote" in payload, payload

        # if old_val != payload:
        #     print ("CAHNGE PAYLAOD")
        #     pprint (old_val)
        #     pprint (payload)
        #     # assert False, "IT WORKS"

        return payload

    # Class Configuration
    # -------------------------

    def __post_init__(self, *args, **kwargs):

        print("SELF", self, self.name)
        pprint(self.__node__.__dict__)
        pprint(self.__class__.__dict__)

        self.log.info(f"New source: {self['name']}->{self['remote']}")

    @staticmethod
    def test_toto(payload):
        print("SUCCES OVERRIDE", payload)


class AppSources(BaseAppNode):

    __node___mixins__ = {
        "logger": {
            "mixin_key": "logger",
            "mixin": LoggerMixin,
            # "log_sformat": "struct",
        },
        "conf": {
            "mixin": ConfListMixin,
            "children": AppSource,
        },
    }

    # def list(self):
    #     return self.conf.value

    def names(self):

        children = self.conf.get_children()
        for t in children:
            print("Children name: ", t.name123())

        return [repo["name"] for repo in self.conf.value]

    def list(self):

        for source in self.conf.get_children():

            print(f"Source: {source['remote']}")

    def get_by_name(self, name):

        print("STARTLOOP")

        for source in self.conf.get_children():

            # print ("vvvvvvvvvvvvvvv STARTLOOP")
            # pprint (source)
            # pprint (source.conf.value)
            # pprint (source.__node__.__dict__)
            # pprint (source.name)
            # pprint (source.__node__._mixin_aliases["name"].value)
            # pprint (source.remote)
            # pprint (source.__node__._mixin_aliases["remote"].value)
            # print ("^^^^^^^^^^^^^^^ STARTLOOP")

            # pprint(dir(source))
            # pprint (source.name)
            # pprint (source.__class__.__mro__)
            # pprint (source.remote)

            # for cls in source.__class__.__mro__:
            #     if hasattr(cls, "name"):
            #         print ("MATCH CLS OK", cls, getattr(cls, "name"))
            #     else:
            #         print ("MATCH CLS KO", cls)

            # assert source.name.value, "FIX BUG HERE"

            # print ("CHECKK", source.name.value ,"==", name)

            if source.name.value == name:
                return source

        self.log.error(f"No sources matching name: {name}")
        return None


# ====================================
# App Stacks
# ====================================


def _test_preparse(mixin, payload):  # MODE=wrap

    if isinstance(payload, str):
        npayload = {
            "name": payload,
        }
        # self.log.debug(f"Tranform app payload: {payload} => {npayload}")
        payload = npayload
    return payload


class AppStack(BaseAppNode):

    # Node Configuration
    # -------------------------

    __node___mixins__ = {
        # "logger": {
        #     "mixin": LoggerMixin,
        # },
        "conf": {
            "mixin": ConfOrderedMixin,
            # "children": GenericKV,
            "children": {
                "name": ConfigKV,
                # "dir": ConfigPath ,
                "app": ConfigKV,
                "source": ConfigKV,
                # "vars": ConfigVars,
                # "tags": TagList,
                # "tags_prefix": TagList,
                # "tags_suffix": TagList,
            },
            "default": {
                "name": None,
                "app": None,
                "vars": {},
                "source": "default",
            },
            "preparse": _test_preparse,
            # "transform" overrided by: __node___mixin__conf__transform__
        },
    }

    # __node__conf__default = {
    #     "name": None,
    #     "app": None,
    #     "vars": {},
    #     "source": "default",
    # }

    # def __node___mixin__conf__preparse__(self, mixin, payload):  # MODE=wrap
    #     if isinstance(payload, str):
    #         npayload = {
    #             "name": payload,
    #         }
    #         # self.log.debug(f"Tranform app payload: {payload} => {npayload}")
    #         payload = npayload
    #     return payload

    def __node___mixin__conf__transform__(self, mixin, payload):  # MODE=wrap
        assert payload["name"], f"Got: {payload}"

        payload["dir"] = payload.get("dir") or payload["name"]

        return payload

    # Class Configuration
    # -------------------------

    def __post_init__(self, *args, **kwargs):
        self.log.debug(f"Stack initialization complete! {self['name']}")

        self.app = self.conf.get_parent_by_cls(MyApp)

        _log.info("YOOOOOOOOOOOOO! STACK MODULE")
        self.log.info("YOOOOOOOOOOOOO! STACK INSTANCE")

        # Prepare paths

        # stack_dir = self.dir.value or self.name.value
        # print ("STACK DIR", stack_dir)

        # self.path.set_path()

        # print ("STACK PATH", self.path.get_path())

    # @property
    def name123(self):
        return self["name"]

    def get_source(self):

        # print("DEBUG")
        # pprint (self)
        # pprint (self.__dict__)
        # pprint (self.__class__)
        # pprint (self.__class__.__mro__)
        # pprint (self.__class__.__dict__)
        # pprint (self.__node__.__dict__)

        # #source_name = getattr(self, "source", "default")

        # print ("MIXIN STATE")
        # pprint (self.__node__._mixin_dict["conf"].__dict__)
        # print ("MIXIN CLASS")
        # pprint (dir(self.__node__._mixin_dict["conf"].__class__))

        # print ("=== Parents")
        # pprint (self.conf.get_parent(target="mixin"))
        # pprint (self.conf.get_parent(target="ctrl"))
        # pprint (self.conf.get_parent(target="node"))

        # print ("=== Parents")
        # pprint (self.conf.get_parents(target="mixin"))
        # pprint (self.conf.get_parents(target="ctrl"))
        # pprint (self.conf.get_parents(target="node"))
        # #pprint ([ x.__class__ for x in self.conf.get_parents()])

        source_name = self.source.value

        app = self.conf.get_parent_by_cls(MyApp)
        # print ("SEARCH SOURCE: ", source_name, source_name.value)
        # assert False
        # print( app)

        # print("PARENT SOURCES")
        # pprint (app.sources.__node__.__dict__)
        # pprint (app.sources.__node__._mixin_dict["conf"].__dict__)
        # print("PARENT SOURCES OVER")
        # assert False, source_name

        src = app.sources.get_by_name(source_name)

        if not src:
            tutu = app.sources.conf.get_children()
            valid = [item.name.value for item in tutu]
            raise Exception(
                f"No sources matching name: {source_name}, valid sources: {valid}"
            )
        assert src, source_name
        return src


class AppStacks(BaseAppNode):

    # Node Configuration
    # -------------------------

    __node___mixins__ = {
        "conf": {
            "mixin": ConfListMixin,
            "mixin_logger_impersonate": False,  # BROKEN ?
            "mixin_logger_level": logging.INFO,
            "children": AppStack,
        },
    }

    # Class Configuration
    # -------------------------

    def __post_init__(self, *args, **kwargs):
        # print("App initialization complete!", self.log.name, self.log.level)

        _log.info("YOOOOOOOOOOOOO! MODULE")
        self.log.info("YOOOOOOOOOOOOO! INSTANCE")

        # pprint (self._node.conf.__dict__)

    def list(self):
        return self.conf.value

    def names(self):

        children = self.conf.get_children()
        for t in children:
            print("Children name: ", t.name123())

        return [repo["name"] for repo in self.conf.value]


# ====================================
# Main App
# ====================================


class MyApp(BaseAppNode):

    # # 0. TLDR syntax
    # # =========================

    # # Like inherited
    # __node__ _param_ <KEY> =
    # __node__ _param_ obj_mixins = {}/[]
    # __node__ _mixin__ <KEY>__<CONF> =

    # # Like decorator
    # __node__ _params__ = {}
    # __node__ _params__ = {
    #                   obj_mixins = {}/[]
    #                   }
    # __node__ _mixins__ = {}/[]

    # # Like kwargs in __init__
    # (obj_<key> = , obj_mixins = {}/[])

    # # 1. Inheritable attributes
    # # =========================

    # # Simple inherited param config
    # __node___param_opt_inherit__ = True

    # # Simple inherited mixin OVERRIDE config
    # __node___param_obj_mixins__ = {
    #     "log": {
    #         "mixin_key": "Blihh",
    #         #"mixin": "Blihh",
    #         "mixin_many": "YEAH",
    #     }
    # }

    # # Simple inherited mixin config
    # __node___mixin__log__mixin__ = LoggerMixin
    # __node___mixin__log__mixin_key__ = "logger"
    # __node___mixin__log__mixin_one__ = "YEAH"

    # # 2. Decorator attributes
    # # =========================
    # __node___params__ = {
    #     "param1": "Yeahhh",

    #     "obj_mixins": {
    #         "mixin1": {
    #             "mixin": "MixinClsOverride"
    #         },
    #         "mixin2": {
    #             "mixin": "MixinCls"
    #         },
    #     },
    # }
    # __node___mixins__ = {
    #     "mixin1": {
    #         "mixin": "MixinCls"
    #     },
    #     "mixin3": {
    #         "mixin": "MixinCls3"
    #     },
    # }

    # 3. Via init kwargs
    # =========================
    # MyClass(obj_<KEY>=<VALUE>, obj_mixins=dict())

    # Node Configuration
    # -------------------------

    __node___mixins__ = [
        # {
        #     "mixin_key": "logger",
        #     "mixin": LoggerMixin,
        #     #"log_sformat": "struct",
        # },
        {
            "mixin_key": "path",
            "mixin": PathMixin,
            #  "ConfPathMixin"
        },
        {
            "mixin_key": "_conf",
            "mixin": ConfOrderedMixin,
            "children": [
                {
                    "key": "config",
                    "cls": AppConfig,
                },
                {
                    "key": "sources",
                    "cls": AppSources,
                },
                {
                    "key": "stacks",
                    "cls": AppStacks,
                },
            ],
        },
    ]

    # Class Configuration
    # -------------------------

    def __post_init__(self, *args, **kwargs):
        # print("App initialization complete!", self.log.name, self.log.level)

        _log.error("App initialization complete! MODULE")
        self.log.error("App initialization complete! INSTANCE")

        self.log_demo()

    def log_demo(self):

        print("\n==> Module logger:", _log.name)
        _log.debug("DEBUG Messages")
        _log.info("INFO Messages")
        _log.warning("WARNING Messages")
        _log.error("ERROR Messages")

        print("\n==> Instance logger:", self.log.name)
        self.log.debug("DEBUG Messages")
        self.log.info("INFO Messages")
        self.log.warning("WARNING Messages")
        self.log.error("ERROR Messages")


# App Instanciation
################################################################

app_config = {
    "config": {
        "namespace": None,
        "vars": {
            "app_domain": "totot.com",
            "another_var": 456,
        },
        "tags_prefix": [
            "first.env",
            "second.env",
        ],
        "tags_suffix": [
            "first.env",
            "second.env",
        ],
    },
    "sources": [
        {
            "name": "default",
            "remote": "https://github.com/default",
        },
        {
            "name": "my_repo4",
            "remote": "https://github.com",
        },
        {
            "name": "my_repo5",
            "branches": ["main", "develop"],
        },
        "my_repo6",
    ],
    "stacks": [
        {
            "name": "my_app1",
            "source": "my_repo5",
            "dir": "/absolute/dir/icitte",
            "app": "default:traefik",
            "tags": [
                {
                    "tag1": {
                        "tag_var1": {},
                    },
                }
            ],
        },
        {
            "name": "my_app2",
            "dir": "../above_rel/icitte",
            "source": "my_repo6",
        },
        {
            "name": "my_app3",
            "dir": "subdir_rel/icitte",
            "app": "default:traefik",
            "vars": ["TUTU=tata"],
        },
    ],
}


# Instanciate app


def simple_app():
    return MyApp(payload=app_config)


def test1():

    app = simple_app()

    ret = app.config.vars.value
    pprint(ret)

    ret = app.config.namespace.value
    pprint(ret)

    # assert False, "WIPPP OOKKKKK"


def test2():

    app = simple_app()

    for stack in app.stacks.conf.get_children():

        # print (f"\n\nSTACK: {stack}")
        # pprint (stack.__class__.__mro__)
        # pprint (stack.__dict__)
        # pprint ([x for x in dir(stack) if not x.startswith("__")])

        # pprint (stack.__node__.__dict__)

        # src = stack.get_source()
        # pprint (src)

        # break

        src = stack.get_source()
        if src:
            print(f"Get stack source '{stack['name']}': {src['name']} => {src.remote}")
        else:
            print(f"No stack source '{stack['name']}'")

        # print("---")
        # print(stack.conf.to_yaml())
        # print("...")


def test3_paths():

    # log.setLevel("WARNING")

    for path in [".", os.getcwd()]:
        path += "/TOTOTOTO/"
        print("============== Test avec path=", path)
        app = MyApp(payload=app_config, path=path)
        print("App Path:", app.path.get_path())

        # pprint (app._node.__dict__)

        for stack in app.stacks.conf.get_children():

            print(f"Stack: {stack['name'].value}")
            pprint(stack.__node__.__dict__)
            path_node = stack["dir"]
            path = path_node.path.get_path()
            print(f"  => Path: {path}")

            # if not path:
            #     print ("  => No sources")
            #     continue
            # if not src:
            #     print ("  => No sources")
            #     continue


def test4_infos():

    app = MyApp(payload=app_config)

    app._node.dump()

    for mixin_name, mixin in app._node._mixin_dict.items():
        print("====> Doc for mixin", mixin.mixin_key)
        # mixin.doc()
        # mixin.dump()


def test5_wrapper(**kwargs):

    app = MyApp(payload=app_config, **kwargs)


test1()

test2()
# test3_paths()
# test4_infos()
# test5_wrapper()


from cafram.lib.logger import app_logger


def call_cli():
    level = logging.INFO
    tfmt = None
    sfmt = None

    sfmt = "=== APP> %(name)-50s%(levelname)8s: %(message)s"
    # sfmt = "APP> %(name)-40s: %(message)s"
    # sfmt = "basic"
    # sfmt = "struct"

    # logger_name = None # Get all logs
    logger_name = __name__  # Get current module logs
    log = app_logger(name=logger_name, colors=True, level=level, sfmt=sfmt, tfmt=tfmt)

    kwargs = {
        # "node_logger_"
    }

    # Test logging
    log.warning("This is the internal logger")
    test5_wrapper(**kwargs)
    log.warning("CLI loading OK")
    pprint(log.__dict__)


# def call_cli():
#     level = logging.DEBUG
#     sfmt = "CLI> %(name)-40s%(levelname)8s: %(message)s"
#     #sfmt = "struct"
#     #sfmt = "struct"
#     #tfmt = "default"
#     tfmt=None

#     logger_name = None # Get all logs
#     logger_name = __name__ # Get current module logs

#     # logging.basicConfig(
#     #     logger=logging.getLogger(NAME),
#     #     level=level,
#     #     format=sfmt)

#     # If name=None, then you have better to use basicConfig
#     #print ("SFMT", sfmt)
#     log = app_logger(name=logger_name, level=level, sfmt=sfmt, tfmt=tfmt)


#     log.warning("This is the internal logger")

#     #log = logging.getLogger(NAME)
#     #logger.setLevel(level)

#     #assert log == _log
#     #pprint (log.__dict__)

#     test5_wrapper()

#     log.warning("CLI loading OK")


# call_cli()


# This is only required on the CLI interface
# Only relevant for entrypoints, configure root logger, get log of
# # all sublibraries because it configure root logger
# level = logging.DEBUG
# fmt = "> %(name)-40s%(levelname)8s: %(message)s"

# logging.basicConfig(level=level, format=fmt) # Get root logger
# # log = logging.getLogger()
# log.setLevel(level)
# _log.setLevel(level)


# Set logger
# log = logging.getLogger(NAME) # Get file/Lib logger
# log = logging.getLogger() # Get Root Logger
# log.setLevel("DEBUG")


# logging.basicConfig(level = loglevel)


# test1()
# test2()

# test3_paths()
# test4_infos()


# pprint (logging.__dict__)
# pprint (log.__dict__)
# pprint (_log.__dict__)
