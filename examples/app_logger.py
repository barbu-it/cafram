import logging
import traceback
from pprint import pprint

from cafram.nodes import Node
from cafram.nodes.comp.base import LoggerMixin

# Only relevant for entrypoints, configure root logger, get log of
# all sublibraries because it configure root logger
logging.basicConfig(level=logging.INFO)


log = logging.getLogger()
# log = logging.getLogger(__name__)
log.setLevel("INFO")


class MyApp(Node):

    __node___params__ = {
        "obj_mixins": {
            "logger": {
                "mixin": LoggerMixin,
                # "log_level": "ERROR",
                # "log_sformat": "struct",
            }
        }
    }

    def _init(self):

        self.log.info("App initialization complete!")

    def log_demo(self):

        self.log.debug("DEBUG Messages")
        self.log.info("INFO Messages")
        self.log.warning("WARNING Messages")
        self.log.error("ERROR Messages")

    def test_logging(self):

        print("=> Get info")
        print(self.log.name)

        print("=> Change log level on road")
        print("DEBUG")
        self.logger.set_level("DEBUG")
        self.log_demo()

        print("INFO")
        self.logger.set_level("INFO")
        self.log_demo()

        print("ERROR")
        self.logger.set_level("ERROR")
        self.log_demo()

        # Regular still works
        log.warning("Regular logger Warning message")

        print("End of demo\n")


# Instanciate app
app = MyApp()

print("YEAHHH")
pprint(app.__node__.__dict__)
app.test_logging()


# print ("TESTS")
log.warning("Regular logger")
log.info("Logging demo is done")
