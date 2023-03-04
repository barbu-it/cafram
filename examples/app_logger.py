import logging
from pprint import pprint

from cafram.nodes import Node
from cafram.mixins.base import LoggerMixin


# Only relevant for entrypoints
# logging.basicConfig(level=logging.INFO)

# log = logging.getLogger(__name__)

# log = logging.getLogger(__name__)
# log = logging.getLogger("cafram2")


class MyApp(Node):

    _node_conf = [
        {
            "mixin": LoggerMixin,
            # "log_level": "DEBUG",
            "log_sformat": "struct",
        }
    ]

    def _init(self):

        self.log.debug("App initialization complete!")

    def test_logging(self):

        self.log.debug("DEBUG Messages")
        self.log.info("INFO Messages")
        self.log.warning("WARNING Messages")
        self.log.error("ERROR Messages")


app = MyApp()

# app._node.dump()
# pprint (app._node.__dict__)

app.test_logging()
