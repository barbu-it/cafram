import traceback
import logging
from pprint import pprint

from cafram.mixins.base import LoggerMixin, IdentMixin
from cafram.mixins.tree import ConfDictMixin, ConfListMixin, NodeConfDict, NodeConfList
from cafram.nodes2 import Node




app_config = {
        "shared_dict": {
            "enabled": True,
            "desc": "This is a description",
            "remote": "http://gitlab.com/",
            "var_files": [
                "first.env",
                "second.env",
            ],
        },
        # "repos": [
        #     {
        #         "name": "my_repo1.git",
        #         "nested1": {
        #             "nested2": {
        #                 "nested3": {},
        #             },
        #         },
        #     },
        #     {
        #         "name": "my_repo2.git",
        #         "branches": [
        #             "main",
        #             "develop"
        #         ],
        #         "enabled": False,
        #     },
        #     "my_repo3.git",
        # ],
           
    }



class MyApp(Node):

    # Test override IdentMixin via native Cafram Node Methods
    # name = "TotoApp"
    # name_prefix = "bluuuu.blaaa.bliiii"


    # Node logger setting
    _node_logger_prefix = False # Use cafram.<module> or None
    #_node_logger_prefix = True # Use object instance name
    #_node_logger_prefix = "custom444" # Use custom prefix
    #_node_logger_prefix = None

    _node_conf = {
        "logger": {
            "mixin": LoggerMixin,
            # "log_sformat": "default",
             "log_sformat": "struct",
            #"log_sformat": "precise",
            #"log_colors": True,
        },
        "ident": {
            "mixin": IdentMixin,
            # "children": {
            #     "repos": Repos,
            # }
        },
        "conf": {
            "mixin": ConfDictMixin,
            "children": False,
            # "children": {
            #     "repos": Repos,
            # }
        },

    }


    def _init(self, **kwargs):

        print("App initialization complete!")

        self.log.info("App initialization complete!")

    def log_demo(self):
        #self.logger.set_format("struct")
        
        self.log.debug("DEBUG Messages")
        self.log.info("INFO Messages")
        self.log.warning("WARNING Messages")
        self.log.error("ERROR Messages")

        print ("Logger Name:", self.log.name)


# Only relevant for entrypoints, configure root logger, get log of
# all sublibraries because it configure root logger
#logging.basicConfig(level=logging.DEBUG)

# Set logger
log = logging.getLogger(__name__)
log.setLevel("DEBUG")

# Instanciate app
app = MyApp(payload=app_config)

app.log_demo()


check = {
    "name_name": app.ident.get_name(),
    "name_prefix": app.ident.get_prefix(),
    "name": app.ident.get_fqn(),
}
pprint (check)



check = {
    "ident_name": app.ident.get_ident_name(),
    "ident_prefix": app.ident.get_ident_prefix(),
    "ident": app.ident.get_ident(),
}
pprint (check)
