"""
Cafram

Also known as: Pshiiit' Knackie ! Framework
"""
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument

import logging
import textwrap

from cafram.utils import serialize

_log = logging.getLogger(__name__)


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


class NotExpectedType(CaframException):
    """Raised when types mismatchs"""


class ClassExpected(CaframException):
    """Raised when a class was expected"""


class InvalidSyntax(CaframException):
    """Raised when config string are not correct"""


class SchemaError(CaframException):
    """Raised when config does not match to schema"""


class ApplicationError(CaframException):
    """Raised when the developper introduced a bug"""


# =====================================================================
# Class helpers
# =====================================================================


class Base:
    """Base cafram object class

    Provides basic features such as:
    * module name
    * object kind
    * object name
    * object logger

    Available methods:
    * dump()
    """

    # Public attributes
    # ---------------------

    # Current library name
    module = "cafram"

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
    log = None

    def __init__(self, *args, **kwargs):

        self.kind = kwargs.get("kind") or self.kind or self.__class__.__name__

        # Ident management
        if "ident" in kwargs:
            self.ident = kwargs.get("ident")
        if self.ident is None:
            raise MissingIdent(f"Missing 'ident' for __init__: {self}")

        self.ident = self.ident or kwargs.get("ident") or self.kind

        self.log = kwargs.get("log") or self.log or logging.getLogger(__name__)
        self.shared = kwargs.get("shared") or {}

    def __str__(self):
        "Return a nice str representation of object"
        return f"{self.__class__.__name__}:{self.ident}"

    def __repr__(self):
        "Return a nice representation of object"
        # return self._nodes
        return f"{self.__class__.__name__}.{id(self)} {self.ident}"
        # return f"Instance {id(self)}: {self.__class__.__name__}:{self.ident}"

    # pylint: disable=redefined-builtin
    def dump(self, format="json", filter=None, **kwargs):
        "Show a dump of an object"

        print("\n===================================================================")
        print(f"== Dump of {self.module}.{self.kind}.{self.ident} {id(self)}")
        print("===================================================================\n")

        print("  Infos:")
        print("  -----------------")
        print(f"    ID: {id(self)}")
        print(f"    Kind: {self.kind}")
        print(f"    Ident: {self.ident}")
        print(f"    Repr: {repr(self)}")
        print(f"    String: {str(self)}")
        classes = "-> ".join([x.__name__ for x in self.__class__.__mro__])
        print(f"    MRO: {classes}")

        print("")


# =====================================================================
# Pre Base Class helpers
# =====================================================================


# Logging
# --------------------------


class Log(Base):
    "Provide a per instance logging"

    log = _log

    def __init__(self, *args, **kwargs):

        # pylint: disable=redefined-outer-name
        log = kwargs.get("log")
        if log is None:
            log_name = f"{self.module}.{self.__class__.__name__}.{self.ident}"
        elif isinstance(log, str):
            log_name = f"{self.module}.{log}"
            log = None
        elif log.__class__.__name__ == "Logger":
            pass
        else:
            raise Exception("Log not allowed here")

        if not log:
            log = logging.getLogger(log_name)

        self.log = log

        # pylint: disable=super-with-arguments
        super(Log, self).__init__(*args, **kwargs)


# =====================================================================
# Post Base Class helpers
# =====================================================================


# Family
# --------------------------


class Family(Base):
    "Provides a family tree"

    root = None
    parent = None
    children = []

    def __init__(self, *args, **kwargs):

        # pylint: disable=super-with-arguments
        super(Family, self).__init__(*args, **kwargs)

        # Init family
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
        "Get children tree"

        result = []
        children = self.children or []
        for child in children:
            children = child.get_children_tree()
            result.append({str(child): children or None})

        return result

    def has_parents(self):
        "Check if has parents"
        return bool(self.parent and self.parent != self)

    def get_parent(self):
        "Return parent"
        return self.parent or None

    def get_parents(self):
        "Return all parent of the object"

        parents = []
        current = self
        parent = self.parent or None
        while parent is not None and parent != current:
            if parent not in parents:
                parents.append(parent)
                current = parent
                parent = getattr(current, "parent")

        return parents

    # pylint: disable=arguments-differ
    def dump(self, **kwargs):
        "Return a dump of the family tree"

        # pylint: disable=super-with-arguments
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


class Hooks(Base):
    """Provides a _init hook feature

    DEPRECATED
    """

    def __init__(self, *args, **kwargs):

        # pylint: disable=super-with-arguments
        super(Hooks, self).__init__(*args, **kwargs)

        if callable(getattr(self, "_init", None)):
            self._init(*args, **kwargs)
