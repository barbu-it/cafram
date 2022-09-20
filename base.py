# Pshiiit' Knackie ! Library

import sys
import logging
import json
import io
import textwrap
import inspect

from pprint import pprint, pformat

from cafram.utils import serialize, flatten, json_validate
import jsonschema

log = logging.getLogger(__name__)


# See: https://stackoverflow.com/questions/328851/printing-all-instances-of-a-class


# =====================================================================
# Exceptions
# =====================================================================


class CaframException(Exception):
    """Generic cafram exception"""


class DictExpected(CaframException):
    """Raised a dict was expected"""


class ListExpected(CaframException):
    """Raised a list was expected"""


class MissingIdent(CaframException):
    """Raised ident is not set"""


class NotImplemented(CaframException):
    """Raised when missing features"""


class NotExpectedType(CaframException):
    """Raised when types mismatchs"""


# =====================================================================
# Class helpers
# =====================================================================


class Base:

    # Public attributes
    # ---------------------

    # Current library name
    _app = "cafram"

    # Objects can have names
    ident = None

    # Object kind, nice name to replace raw class name, should be a string
    kind = None

    # Define live runtime data
    # To be renamed: shared
    # runtime = {}

    # Optional attributes
    # ---------------------

    # Object shortcut to logger
    log = log

    def __init__(self, *args, **kwargs):
        self.log.debug(
            f"__init__: Base/{self} => {[ x.__name__ for x in  self.__class__.__mro__]}"
        )
        # print (f"__init__: Base/{self} => {[ x.__name__ for x in  self.__class__.__mro__]}")

        # print ("INIT Base", args, kwargs)

        # print ("init base")
        self.kind = kwargs.get("kind") or self.kind or self.__class__.__name__

        # Ident management
        if "ident" in kwargs:
            self.ident = kwargs.get("ident")
        if self.ident is None:
            raise MissingIdent(f"Missing 'ident' for __init__: {self}")

        self.ident = self.ident or kwargs.get("ident") or self.ident or self.kind

        self.log = kwargs.get("log") or self.log
        # print ("Update in INIT BASE", self.ident, id(self))

        self.shared = kwargs.get("shared") or {}
        # if "runtime" in kwargs:
        #     self.runtime = kwargs.get("runtime") or {}

        # print ("OVER Base")

    def __str__(self):
        return f"{self.__class__.__name__}:{self.ident}"

    def __repr__(self):
        # return self._nodes
        return f"{self.__class__.__name__}.{id(self)} {self.ident}"
        # return f"Instance {id(self)}: {self.__class__.__name__}:{self.ident}"

    def dump(self, format="json", filter=None, **kwargs):

        print("\n===================================================================")
        print(f"== Dump of {self._app}.{self.kind}.{self.ident} {id(self)}")
        print("===================================================================\n")

        print("  Infos:")
        print(f"    ID: {id(self)}")
        print(f"    Kind: {self.kind}")
        print(f"    Ident: {self.ident}")
        print(f"    Repr: {self.__repr__()}")
        print(f"    String: {self.__str__()}")
        classes = "-> ".join([x.__name__ for x in self.__class__.__mro__])
        print(f"    MRO: {classes}")

        # cls = self.__class__.__bases__
        # cls = inspect.getmro(self.__class__)
        # data = serialize(cls, fmt="yaml")
        # print ("  Features:")
        # print (textwrap.indent(data, '    '))

        # print ("  Runtime config:")
        # print (serialize(list(self.runtime.keys())))

        print("")

    def dump2(self, *args, **kwargs):
        self.log.warning("WARNING: dump2 method is deprecated in favor of dump")
        self.dump(*args, **kwargs)


# =====================================================================
# Pre Base Class helpers
# =====================================================================


# Logging
# --------------------------


class Log(Base):

    log = log

    def __init__(self, *args, **kwargs):

        self.log.debug(f"__init__: Log/{self}")

        log = kwargs.get("log")
        if log is None:
            log_name = f"{self._app}.{self.kind}.{self.ident}"
        elif isinstance(log, str):
            log_name = f"{self._app}.{log}"
            log = None
        elif log.__class__.__name__ == "Logger":
            pass
        else:
            raise Exception("Log not allowed here")

        if not log:
            log = logging.getLogger(log_name)

        self.log = log

        super(Log, self).__init__(*args, **kwargs)


# =====================================================================
# Post Base Class helpers
# =====================================================================


# Family
# --------------------------


class Family(Base):

    root = None
    parent = None
    children = []

    def __init__(self, *args, **kwargs):

        super(Family, self).__init__(*args, **kwargs)

        self.log.debug(f"__init__: Family/{self}")

        # Init family
        # print ("init family")
        parent = kwargs.get("parent") or self.parent

        # Register parent
        if parent and parent != self:
            self.parent = parent
            self.root = parent.root
        else:
            self.parent = self
            self.root = self

        # Register children
        self.children = []
        if self.has_parents():
            self.parent.children.append(self)

    def get_children_tree(self):

        result = []
        children = self.children or []
        for child in children:
            children = child.get_children_tree()
            result.append({str(child): children or None})

        return result

    def has_parents(self):
        return True if self.parent and self.parent != self else False

    def get_parent(self):
        return self.parent or None

    def get_parents(self):
        "Return all parent of the object"

        parents = []
        current = self
        parent = self.parent or None
        while parent is not None and parent != current:
            if not parent in parents:
                parents.append(parent)
                current = parent
                parent = getattr(current, "parent")

        return parents

    def dump(self, **kwargs):
        super(Family, self).dump(**kwargs)

        parents = self.get_parents()
        children = self.get_children_tree()

        if parents or children:
            print("  Family:")
            print("  -----------------")
            print(f"    Parents/Children: {len(parents)}/{len(children)}")

        if parents:
            print("    Parents:")
            # print ("    -----------------")
            parents.reverse()
            parents = serialize(parents, fmt="yaml")
            print(textwrap.indent(parents, "      "))

        if children:
            print("    Children:")
            # print ("    -----------------")
            children = serialize(children, fmt="yaml")
            print(textwrap.indent(children, "      "))

        print("\n")


# Hooks
# --------------------------


class Hooks:
    def __init__(self, *args, **kwargs):

        super(Hooks, self).__init__(*args, **kwargs)

        self.log.debug(f"__init__: Hooks/{self}")
        if callable(getattr(self, "_init", None)):
            self._init(*args, **kwargs)
