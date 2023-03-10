import traceback
import logging
from pprint import pprint

from cafram.mixins.base import LoggerMixin
from cafram.mixins.tree import ConfDictMixin, ConfListMixin, NodeConfDict, NodeConfList, ConfMixin
from cafram.nodes2 import Node


# Nodes helpers
################################################################


class BaseApp(Node):
    "BaseApp"

    #_node__conf__
    _node_logger_prefix = False

    _node__logger__mixin = LoggerMixin
    _node__logger__logger_level = "DEBUG"
    _node__logger__log_sformat= "struct"


class BaseAppNode(BaseApp, Node):
    "BaseAppNode"

class BaseAppNodeDict(BaseAppNode, NodeConfDict):
    "BaseAppNodeDict"
    

class BaseAppNodeList(BaseAppNode, NodeConfList):
    "BaseAppNodeList"








# App definitions
################################################################


class Repo(BaseAppNodeDict):

    _node_logger_prefix = True

    _node_conf = {
        "logger": {
            "mixin": LoggerMixin,
        },
        "conf": {
            "mixin": ConfDictMixin,
            #"children": GenericKV,
        },
    }

    _node__conf__default = {
        "name": None,
        "branches": ["main123", "custom_default"],
        "ENABLED": True,
    }

    def _init(self, *args, **kwargs):
        self.log.info(f"Single Repo initialization complete! {self['name']}")
        #pprint (self.value)
        #pprint (self._node.conf.__dict__)

    def _node__conf__transform(self, mixin, payload):

        if isinstance(payload, str):
            npayload = {
                "name": payload,
            }
            self.log.info(f"Tranform payload: {payload} => {npayload}")
            payload = npayload
        return payload

        # conf = {} # dict(self._node__conf__default)
        # conf.update(payload)

        # return conf

    #@property
    def name123(self):
        return self

class Repos(BaseAppNodeList):

    _node_conf = {
        "conf": {
            "mixin": ConfListMixin,
            "children": Repo,
        },
    }

    def list(self):
        return self.conf.value

    def names(self):

        #pprint (self.conf.value)
        print ("DEBUUUUUG")
        children = self.conf.get_children()
        pprint (children)

        for t in children:
            print ("CHILDREN", t)
            pprint (t.name123())

        
        return [ repo["name"] for repo in self.conf.value]



class ConfigKV(BaseAppNode):
    #_node__logger__mixin = LoggerMixin
    #_node__conf__mixin = ConfDictMixin

    _node_conf = {
        "logger": {
            "mixin": LoggerMixin,
        },
        "conf": {
            "mixin": ConfMixin,
        },
    }

    def _init(self, *args, **kwargs):
        self.log.info(f"KV config: {self.conf.index}={self.conf.value}")


class Config(BaseAppNodeDict):

    _node_conf = {
        "logger": {
            "mixin": LoggerMixin,
            "log_sformat": "struct",
        },
        "_conf": {
            "mixin": ConfDictMixin,
            "children": ConfigKV,
        },
    }

class MyApp(BaseApp):

    #name_prefix = ""



    #_node__conf__mixin = ConfDictMixin
    # _node__conf__children = "WARNING"
    # _node__conf__children = "DEBUG"
    #_node__conf__schema = False

    #_node_logger_prefix = True

    _node_conf = {
        "logger": {
            "mixin": LoggerMixin,
            "log_sformat": "struct",
        },
        "_conf": {
            "mixin": ConfDictMixin,
            "children": {
                "repos": Repos,
                "shared_dict": Config,
            }
        },
        # "repos": {
        #     "mixin": ConfListMixin,
        #     "children":{
        #         "repos": Repos,
        #     }
        # },
    }

    #_node_logger_integrate = True

    def _init(self, **kwargs):
        self.log.info("App initialization complete!")

    # def _node_init(self, *args, **kwargs):
    #     print ("Node Init")
    #     self.log.info("App initialization complete!")

    # def _node__conf__transform(self, mixin, payload):
    #     print ("YOOOO MAIN")
    #     return payload


    #def _node__conf__transform(self, mixin, payload):
    #    print ("iiiiiiiiiiiiiiii   Node transform APPPPPP")
    #    print ("self:", self)
    #    print ("payload:", payload)
    #    print ("mixin:", mixin)

    #@staticmethod
    #def _node__conf__transformsss(payload, mixin=None, obj=None):
    #    print ("iiiiiiiiiiiiiiii   Node transform APPPPPP")
    #    print ("obj", obj)
    #    print ("mixin", mixin)

    def log_demo(self):

        self.log.debug("DEBUG Messages")
        self.log.info("INFO Messages")
        self.log.warning("WARNING Messages")
        self.log.error("ERROR Messages")

        print ("Logger Name:", self.log.name)




# App Instanciation
################################################################

app_config = {
        "shared_dict": {
            "enabled": True,
            "desc": "This is a description",
            "remote": "http://gitlab.com/",
            "branches": [
                    "main"
                ],
            "var_files": [
                "first.env",
                "second.env",
            ],
        },
        "repos": [
            {
                "name": "my_repo1.git",
                "nested1": {
                    "nested2": {
                        "nested3": {},
                    },
                },
            },
            {
                "name": "my_repo2.git",
                "branches": [
                    "main",
                    "develop"
                ],
                "enabled": False,
            },
            "my_repo3.git",
        ],
           
    }



# Only relevant for entrypoints, configure root logger, get log of
# all sublibraries because it configure root logger
fmt = "> %(name)-20s%(levelname)8s: %(message)s"

#logging.basicConfig(level=logging.DEBUG, format=fmt)

# Set logger
log = logging.getLogger(__name__)
log.setLevel("DEBUG")

# Instanciate app
app = MyApp(payload=app_config)

app.log_demo()




print ("REPOS CONFIG")
ret = app.repos.list()
pprint (ret)

print ("WHOLE CONFIG")
ret = app._conf.value
pprint (ret)


print ("GLOBAL CONFIG")
ret = app.shared_dict.value
pprint (ret)

# ret = app.repos.names()
# pprint (ret)
