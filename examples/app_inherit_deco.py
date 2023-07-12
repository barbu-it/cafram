# import traceback
import logging
from pprint import pprint

# from cafram.decorators import newNode, addMixin

# from cafram.nodes.comp.base import LoggerMixin, IdentMixin
# from cafram.nodes.comp.tree import (
#     ConfDictMixin,
#     ConfListMixin,
#     NodeConfDict,
#     NodeConfList,
#     ConfOrderedMixin,
# )
from cafram.nodes import newNode, addMixin


app_config = {
    "config": {
        "enabled": True,
        "desc": "This is a description",
        "remote": "http://gitlab.com/",
        "branches": ["main"],
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
            "branches": ["main", "develop"],
            "enabled": False,
        },
        # NOT IMPLEMENTED YET"my_repo3.git",
    ],
}


## Test inheritance classes
## =========================


class TestParent:
    def __init__(self, *args, **kwargs):
        print(f"OK INIT: {self} is a subclass of TestParent")
        pprint(self.__dict__)

    def test1(self):
        print(f"OK METHOD: {self} is a subclass of TestParent")


# @newNode()
# @addMixin("cafram.nodes.comp.base:LoggerMixin", "LOGME",
#     alias__log="TUTU"
# )
# class TestParentLoggerConf():
#     "Propagate logger mixin on all children"

#     # def __init__(self, *args, **kwargs):
#     #     print (f"OK INIT: {self} is a subclass of TestParent")
#     #     pprint(self.__dict__)

#     # def test1(self):
#     #     print (f"OK METHOD: {self} is a subclass of TestParent")


# ## Core App
# ## =========================


@newNode(
    # prefix="node",
    # obj_conf=[
    #     {
    #         "mixin": ConfDictMixin,
    #         # "children": Repo,
    #     },
    # ],
    # TEST: node_attr="_node"
)
@addMixin("cafram.nodes.comp.tree:ConfDictMixin")
# Many forms:
# @addMixin("MIXIN_NAME")
# @addMixin("MIXIN_NAME", "MIXIN_KEY")
# @addMixin("MIXIN_NAME" , "MIXIN_KEY", {"param1":'value1', "param2":'value2'})
# @addMixin("MIXIN_NAME" , "MIXIN_KEY", mixin_conf={"param1":'value1', "param2":'value2'})
# @addMixin("MIXIN_NAME" , "MIXIN_KEY", param1='value1', param2='value2')


class Repo(TestParent):
    def __post_init__(self, *args, **kwargs):
        print(f"OK INIT: {self} I expect this to call parent")
        print("YIII", args, kwargs)
        # pprint(self.__dict__)
        super().__init__()

    def get_name(self):

        payload = self.conf.value
        index = self.conf.index
        name = payload.get("name", f"repo{index}")

        return f"Repo{index}: {name}"

    def transform(self, payload):

        if isinstance(payload, str):
            payload = {
                "name": payload,
            }

        return payload

    def __str__(self):
        return f"{self.__class__.__qualname__} YOOO: {self.__dict__}"

    def __repr__(self):
        return f"{self.__class__.__qualname__} YOOO: {self.__dict__}"


@newNode()
@addMixin("cafram.nodes.comp.tree:ConfListMixin", children=Repo)
class Repos:
    "Represent many repos"

    def list(self):
        return self.conf.value

    def names(self):
        return [repo["name"] for repo in self.conf.value]


@newNode()
@addMixin("cafram.nodes.comp.tree:ConfDictMixin")
class Config:
    "This is my main config obj"

    RANDOM_CLS_ATTR = True

    def __init__(self, *args, **kwargs):
        print(f"OK CONFIG INIT: {self} I expect this to call parent")
        super().__init__()

    def transform(self, payload):
        print("GOT CONFIG PAYLOAD:", payload)
        return payload


@newNode()
@addMixin("cafram.nodes.comp.base:LoggerMixin")
@addMixin(
    "cafram.nodes.comp.tree:ConfOrderedMixin",
    mixin_logger_level=logging.DEBUG,
    children={
        "config": Config,
        "repos": Repos,
    },
)
# @addMixin("cafram.nodes.comp.base:LoggerMixin", "LOGME",
#     alias__log="TUTU"
# )


class MyApp:
    "This is my main app"

    _node_config1 = True
    _node_config2 = True
    _node__KEY__OPT = True
    _node__KEY__OPT2 = True

    _ZZZZZZZZZZZZZZz = True

    def __post_init__(self, my_opt=True, *args, **kwargs):
        # def __post_init__(self, my_opt=True):
        print(f"LOCAL __INIT__ !: {my_opt}, {args}, {kwargs}")

    def _init(self, **kwargs):

        self.log.info("App initialization complete!")

    def log_demo(self):

        pprint(self.__dict__)
        pprint(self.__node__.__dict__)

        self.log.debug("DEBUG_Messages")
        self.log.info("INFO_Messages")
        self.log.warning("WARNING_Messages")
        self.log.error("ERROR_Messages")


# Only relevant for entrypoints, configure root logger, get log of
# all sublibraries because it configure root logger
logging.basicConfig(level=logging.DEBUG)

# Set logger
# log = logging.getLogger(__name__)
# log.setLevel("DEBUG")

# Instanciate app
app = MyApp(payload=app_config, tutu=False)


# Tests1: Check children
assert app.value, f"Step 1 failed: {app.value}"
assert isinstance(app.config.value, dict), f"Step 1 failed: {app.config.value}"
assert isinstance(app.repos.value, list)

# Test2: Json/Yaml format
versions = {
    "get_attr": app.config.conf.to_yaml(),
    "item_attr": app.config["conf"].to_yaml(),
    "call_attr": app.config("conf").to_yaml(),
    "node_get_attr": app.config.__node__.conf.to_yaml(),
    "node_item_attr": app.config.__node__["conf"].to_yaml(),
    "node_mixin_attr": app.config.__node__._mixin_dict["conf"].to_yaml(),
}

# Check they all produce the same output
ref = versions["get_attr"]
for key, val in versions.items():
    assert val == ref

# Test3: Exploit children fueatures

ref = app.conf.value
assert app.config.value == ref["config"]
assert app.repos.value == ref["repos"]

print("=== Test 3")
print("# Application config in json")
print(app.config.conf.to_json())
print("# Application repos in yaml")
print(app.repos.conf.to_yaml())


# Test 4: Test class methods and discovery
print("=== Test 4")

app.log_demo()

print("Show node children of app and then repos")
pprint(app.conf.get_children())
pprint(app.repos.list())

print("Let's grab some repo child repo:")
pprint(app.repos[1])
pprint(app.repos[1].value)
pprint(app.repos[1].get_name())
pprint(app.repos[0].get_name())

print("EOF")
