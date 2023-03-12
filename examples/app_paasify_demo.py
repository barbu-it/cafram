import os
import traceback
import logging
from pprint import pprint

from cafram.mixins.base import LoggerMixin
from cafram.mixins.tree import (
    ConfDictMixin,
    ConfListMixin,
    NodeConfDict,
    NodeConfList,
    ConfMixin,
    ConfPathMixin,
    ConfOrderedMixin,
)
from cafram.mixins.hier import HierChildrenMixin, HierParentMixin
from cafram.mixins.path import PathMixin

from cafram.nodes2 import Node

from cafram.utils import get_logger


__name__ = "paaSiFy"

# NAME = __name__
NAME = "paaSiFy"


_log = logging.getLogger(NAME)
# _log.setLevel(logging.DEBUG)


# Nodes helpers
################################################################

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

    # _node__conf__
    _node_logger_prefix = False

    _node__logger__mixin = LoggerMixin
    _node__logger__mixin_key = "log"
    # _node__logger__log_level = "DEBUG"
    # _node__logger__log_colors = False
    # _node__logger__log_sformat = "time"
    # _node__logger__log_sformat = "struct"

    # log = FakeLogger()
    # log = _log


class BaseAppNode(BaseApp, Node):
    "BaseAppNode"


class BaseAppNodeDict(BaseAppNode, NodeConfDict):
    "BaseAppNodeDict"


class BaseAppNodeList(BaseAppNode, NodeConfList):
    "BaseAppNodeList"


# App definitions
################################################################


# Config Elements
# ----------------------------------


class ConfigKV(BaseAppNode):
    # _node__logger__mixin = LoggerMixin
    # _node__conf__mixin = ConfDictMixin

    _node_conf = {
        # "logger": {
        #     "mixin": LoggerMixin,
        # },
        "conf": {
            "mixin": ConfMixin,
        },
    }

    def _init(self, *args, **kwargs):
        self.log.info(f"KV config: {self.conf.index}={self.conf.value}")


class ConfigVars(BaseAppNode):

    _node_conf = {
        # "logger": {
        #     "mixin": LoggerMixin,
        #     "log_sformat": "struct",
        # },
        "_conf": {"mixin": ConfListMixin, "children": ConfigKV},
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


# Tag Management
# ----------------------------------


class TagList(BaseAppNode):
    # _node__logger__mixin = LoggerMixin
    # _node__conf__mixin = ConfDictMixin

    _node_conf = {
        "conf": {
            "mixin": ConfListMixin,
        },
    }

    def _init(self, *args, **kwargs):
        self.log.debug(f"Tag config: {self.conf.index}={self.conf.value}")


# Config
# ----------------------------------


class AppConfig(BaseAppNode):

    _node_conf = {
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


# Sources
# ----------------------------------


class AppSource(BaseAppNode):

    _node_conf = {
        # "logger": {
        #     "mixin": LoggerMixin,
        # },
        "conf": {
            "mixin": ConfDictMixin,
            # "children": ConfigKV,
        },
    }

    _node__conf__default = {
        "name": None,
        "remote": None,
        "ref": "",
    }

    def _node__conf__preparse(self, mixin, payload):

        if isinstance(payload, str):
            npayload = {
                "remote": payload,
            }
            self.log.debug(f"Tranform source payload: {payload} => {npayload}")
            payload = npayload
        return payload

    def _init(self, *args, **kwargs):

        self.log.info(f"New source: {self['name']}->{self['remote']}")


class AppSources(BaseAppNode):

    _node_conf = {
        "conf": {
            "mixin": ConfListMixin,
            "children": AppSource,
        },
    }

    def list(self):
        return self.conf.value

    def names(self):

        children = self.conf.get_children()
        for t in children:
            print("Children name: ", t.name123())

        return [repo["name"] for repo in self.conf.value]

    def list(self):

        for source in self.conf.get_children():

            print(f"Source: {source['remote']}")

    def get_by_name(self, name):

        for source in self.conf.get_children():
            if source["name"] == name:
                return source

        self.log.error(f"No sources matching name: {name}")
        return None


# Stack management
# ----------------------------------


class ConfigPath(BaseAppNode):

    _node_conf = {
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

    def _init(self, *args, **kwargs):

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


#######$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


class AppStack(BaseAppNode):

    # _node_logger_prefix = False
    _node_logger_impersonate = False

    _node_conf = {
        # "logger": {
        #     "mixin": LoggerMixin,
        # },
        "conf": {
            "mixin": ConfOrderedMixin,
            # "children": GenericKV,
            "children": {
                "name": ConfigKV,
                # "dir": ConfigPath ,
                # "app": ConfigKV ,
                # "source": ConfigKV ,
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
        },
    }

    _node__conf__default = {
        "name": None,
        "app": None,
        "vars": {},
        "source": "default",
    }

    def _init(self, *args, **kwargs):
        self.log.debug(f"Stack initialization complete! {self['name']}")

        self.app = self.conf.get_parent_by_cls(MyApp)

        # Prepare paths

        # stack_dir = self.dir.value or self.name.value
        # print ("STACK DIR", stack_dir)

        # self.path.set_path()

        # print ("STACK PATH", self.path.get_path())

    def _node__conf__preparse(self, mixin, payload):

        # print ("PREPARSE PAYLOAD", payload)

        if isinstance(payload, str):
            npayload = {
                "name": payload,
            }
            self.log.debug(f"Tranform app payload: {payload} => {npayload}")
            payload = npayload
        return payload

    def _node__conf__transform(self, mixin, payload):

        assert payload["name"]

        payload["dir"] = payload.get("dir") or payload["name"]

        # pprint (payload)
        return payload

    # @property
    def name123(self):
        return self["name"]

    def get_source(self):
        source_name = self.source
        src = self.app.sources.get_by_name(source_name)
        return src


class AppStacks(BaseAppNode):

    # VALID LOGGING TESTSSSSSSSS !!!!

    _node_logger_impersonate = True
    # _node_logger_level = logging.DEBUG

    # _node_logger_level = logging.INFO

    # AKA IMPERSONATE
    # _node__conf__mixin_logger_impersonate = "custom_logger"
    # _node__conf__mixin_logger_impersonate = True
    # #_node__conf__mixin_logger_impersonate = False
    # _node__conf__mixin_logger_level = logging.INFO

    _node_conf = {
        "conf": {
            "mixin": ConfListMixin,
            "mixin_logger_impersonate": False,
            "mixin_logger_level": logging.INFO,
            "children": AppStack,
        },
    }

    def _init(self, *args, **kwargs):
        # print("App initialization complete!", self.log.name, self.log.level)

        _log.info("YOOOOOOOOOOOOO! MODULE")
        self.log.info("YOOOOOOOOOOOOO! INSTANCE")

    def list(self):
        return self.conf.value

    def names(self):

        children = self.conf.get_children()
        for t in children:
            print("Children name: ", t.name123())

        return [repo["name"] for repo in self.conf.value]


# Main App
# ----------------------------------


class MyApp(BaseAppNode):

    _node_conf = [
        # {
        #     "mixin_key": "logger",
        #     "mixin": LoggerMixin,
        #     "log_sformat": "struct",
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
                    "key": "stacks",
                    "cls": AppStacks,
                },
                # {
                #     "key": "sources",
                #     "cls": AppSources,
                # },
            ],
        },
    ]

    def _init(self, *args, **kwargs):
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


def test2():

    app = simple_app()

    for stack in app.stacks.conf.get_children():

        src = stack.get_source()
        if src:
            print(f"Get stack source '{stack['name']}': {src['name']} => {src.remote}")
        else:
            print(f"No stack source '{stack['name']}'")

        print("---")
        print(stack.conf.to_yaml())
        print("...")


def test3_paths():

    log.setLevel("WARNING")

    for path in [".", os.getcwd()]:
        path += "/TOTOTOTO/"
        print("============== Test avec path=", path)
        app = MyApp(payload=app_config, path=path)
        print("App Path:", app.path.get_path())

        # pprint (app._node.__dict__)

        for stack in app.stacks.conf.get_children():
            print(f"Stack: {stack['name'].value}")
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


call_cli()


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
