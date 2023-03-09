"""
Cafram Root Classes
"""

import logging
import inspect

class CaframObj:
    "An empty root class to determine a cafram object or not"

    # Name part
    name = None

    # Domain part
    #name_prefix = f"|{__module__}|"
    name_prefix = None

    def get_name(self):
        "Retrieve node Name"
        return self.name or self.__class__.__name__

    def get_prefix(self):
        return self.name_prefix or self.__class__.__module__

    def get_fqn(self):
        "Return the class Fully Qualified Name of any object"
        return ".".join([self.get_prefix(), self.get_name()])
        

    def get_mro(self):
        "Return the class MRO of any object"
        cls = type(self)
        return inspect.getmro(cls)
        

class CaframNode(CaframObj):
    "An empty root class to determine a cafram object or not"
    pass


class CaframInternalsGroup(CaframObj):
    "Cafram Internals"


    _obj_logger_prefix = False


    def get_obj(self):
        "Return current object"
        return self._obj
    
    def _init_logger(self, prefix=None):
        "Init internal cafram logger"

        prefix_old = prefix
        prefix = prefix or self._obj_logger_prefix
        if prefix == True:
            obj = self.get_obj()
            prefix = f"{obj.__module__}.{obj.__class__.__name__}"
        elif prefix == False:
            prefix = self.__module__


        if prefix:
            name = f"{prefix}.{self.get_name()}"
        else:
            name = self.get_fqn()

        self._log = logging.getLogger(name)
        #self._log.propagate = False
        self._log.debug(f"Get Cafram logger for {self.get_name()}: {name} (prefix={prefix_old}/{prefix})")



class CaframCtrl(CaframInternalsGroup):
    "Cafram Controller Type"
    pass


class CaframMixin(CaframInternalsGroup):
    "Cafram Mixin Type"


    def get_ctrl(self):
        "Return current Node controller"
        return self.node_ctrl

    def get_obj(self):
        "Return current object"
        return self.get_ctrl()._obj
