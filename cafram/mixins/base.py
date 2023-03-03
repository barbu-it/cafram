import types
import logging
from pprint import pprint

# from cafram2.mixins import BaseMixin
from . import BaseMixin


log = logging.getLogger(__name__)


# Utils Mixins
################################################################


class MapAttrMixin(BaseMixin):

    # key = "attr"
    mixin_map = {}

    # default_conf = {
    #     # Allow mixin map overrides
    #     "attr_override": False,

    #     # Set your static mapping here
    #     "attr_map": {
    #             # "conf": None,
    #             # "log": "log2",
    #         },

    #     # Set True to map obj attributes to known mixins
    #     "attr_forward": False,

    #     # Set a function to forward unknown attr
    #     "attr_forward": True,
    # }

    attr_override = False

    # Set your static mapping here
    attr_map = {
        # "conf": None,
        # "log": "log2",
    }

    # Set True to map obj attributes to known mixins
    # attr_forward = False

    # Set a function to forward unknown attr
    attr_forward = True

    def _init(self, *args, **kwargs):

        # attr_map = self.conf["attr_map"]
        attr_map = self.attr_map

        # Init manual mapping
        for name, key in attr_map.items():
            key = key or name
            value = self.node_ctrl.mixin_get(key)

            if not value:
                raise errors.MissingMixin(f"Missing mixin: {key}")

            self.node_ctrl.mixin_set(value, name=name)

        # Add hooks
        this = self

        def func(name):
            "Hook gettattr"
            if name in this.mixin_map:
                return True, this.mixin_map[name]
            return False, None

        self.node_ctrl.mixin_hooks("__getattr__", func)

        # Patch object __getattr__
        if self.attr_forward is True:

            def func2(self, name):
                "Hook gettattr for top object"
                return getattr(this.node_ctrl, name)

            self.node_ctrl._obj.__class__.__getattr__ = types.MethodType(
                func2, self.node_ctrl._obj.__class__
            )


class LoggerMixin(BaseMixin):

    key = "logger"
    conf_logger = None

    default_conf = {
        # Set True to map to known mixins
        "logger_key": "log",
        # Define the logger name, class name if not used
        "logger_name": None,
        # Define the logger name prefix, None for internal use
        "logger_prefix": None,
        # Define if this config is inherited by children
        "logger_propagate": True,
        # Define logging format
        "logger_sformat": "default",
        # Define time format
        "logger_tformat": "default",
    }

    # Log and time formats
    sformats = {
        "default": "%(levelname)8s: %(message)s",
        "struct": "%(name)-40s%(levelname)8s: %(message)s",
        "time": "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s",
        "precise": (
            "%(asctime)s.%(msecs)03d"
            + " (%(process)d/%(thread)d) "
            + "%(pathname)s:%(lineno)d:%(funcName)s"
            + ": "
            + "%(levelname)s: %(message)s"
        ),
    }
    tformats = {
        "default": "%H:%M:%S",
        "precise": "%Y-%m-%d %H:%M:%S",
    }

    def _init(self, *args, **kwargs):

        logger_key = self.conf["logger_key"]

        # Try to get node_ctrl logger

        # parent = self.node_ctrl._parent
        # #print ("PARENT")
        # #pprint(self.node_ctrl.__dict__)
        # if parent:
        #     parent_logger = "WIP"
        #     print ("YOOOO ", self)
        #     pprint (parent)
        #     # #parent_logger = self.node_ctrl.mixin_get(self.key)
        #     print ("PARENT LOGGER CONFIG:", parent_logger)

        # self.log =
        self.set_logger()

        # Register logger into node_ctrl
        # self.node_ctrl._mixin_dict[logger_key] = self.log
        # if self.node_ctrl:

        # print (self)
        # pprint (self.__dict__)
        self.node_ctrl.mixin_set(self.log, name=logger_key, shortcut=True)

    def set_format(self, sformat=None, tformat=None):

        sformat = sformat or self.conf["logger_sformat"]
        tformat = tformat or self.conf["logger_tformat"]

        _sformat = self.sformats.get(sformat, sformat)
        _tformat = self.sformats.get(tformat, tformat)

        ch = logging.StreamHandler()
        formatter = logging.Formatter(_sformat)
        ch.setFormatter(formatter)

        # ch.setLevel(logging.DEBUG)

        self.log.addHandler(ch)

    def set_logger(self, conf_logger=None, attribute_name="log"):
        """Set instance logger name or instance"""

        logger_name = self.conf["logger_name"]
        logger_prefix = self.conf["logger_prefix"]
        if not logger_name:
            logger_name = self.node_ctrl._obj.__class__.__name__
            logger_name = self.ident
        if not logger_prefix:
            logger_prefix = __name__

        logger_fqdn = f"{logger_prefix}.{logger_name}"

        self.logger_name = logger_name
        self.logger_prefix = logger_prefix
        self.logger_fqdn = logger_fqdn

        # Get logger
        self.log = logging.getLogger(logger_fqdn)
        # pprint (self.log.__dict__)

        # Set level
        self.log.setLevel(logging.DEBUG)

        self.set_format()

        # log = None
        # log_name = None
        # conf_logger = conf_logger or self.conf_logger

        # if conf_logger is None:
        #     #log_name = f"{self.module}.{self.__class__.__name__}"
        #     log_name = f"{self.__class__.__name__}"
        #     ident = getattr(self, "ident", None)
        #     if ident:
        #         #log_name = f"{self.module}.{self.__class__.__name__}.{ident}"
        #         log_name = f"{self.__class__.__name__}.{ident}"
        # elif isinstance(conf_logger, str):
        #     log_name = f"{conf_logger}"
        # elif log.__class__.__name__ == "Logger":
        #     log = conf_logger

        # else:
        #     raise Exception(f"Log not allowed here: {conf_logger}")

        # if not log:
        #     log = logging.getLogger(log_name)

        # return log
