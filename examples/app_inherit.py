import traceback
import logging
from pprint import pprint

from cafram.mixins.base import LoggerMixin, IdentMixin
from cafram.mixins.tree import (
    ConfDictMixin,
    ConfListMixin,
    NodeConfDict,
    NodeConfList,
    ConfOrderedMixin,
)
from cafram.nodes2 import Node


app_config = {
    "shared_dict": {
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


class Repo(NodeConfDict):

    _node_conf = [
        {
            "mixin": ConfDictMixin,
            # "children": Repo,
        },
    ]

    def transform(self, payload):

        if isinstance(payload, str):
            payload = {
                "name": payload,
            }

        return payload


class Repos(NodeConfList):

    _node_conf = [
        {
            "mixin": ConfListMixin,
            "children": Repo,
        },
    ]

    def list(self):
        return self.conf.value

    def names(self):
        return [repo["name"] for repo in self.conf.value]


class MyApp(Node):

    _node_conf = [
        {
            "mixin": LoggerMixin,
        },
        {
            "mixin": ConfOrderedMixin,
            "children": {
                "repos": Repos,
            },
        },
    ]

    def _init(self, **kwargs):

        self.log.info("App initialization complete!")

    def log_demo(self):

        self.log.debug("DEBUG Messages")
        self.log.info("INFO Messages")
        self.log.warning("WARNING Messages")
        self.log.error("ERROR Messages")


# Only relevant for entrypoints, configure root logger, get log of
# all sublibraries because it configure root logger
logging.basicConfig(level=logging.DEBUG)

# Set logger
# log = logging.getLogger(__name__)
# log.setLevel("DEBUG")

# Instanciate app
app = MyApp(payload=app_config)

# app.dump()

ret = app.repos.list()
pprint(ret)

ret = app.repos.names()
pprint(ret)
