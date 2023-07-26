# Import the whole parent library in way to prevent user to add all exception
# pylint: disable=unused-wildcard-import, wildcard-import
from cafram.errors import *

# NodeCtrl Exceptions
# ====================


class CaframCtrlException(CaframException):
    """Generic Controller cafram exception"""


# Missings

# Mixin exceptions


class AlreadyDefinedMixin(CaframCtrlException):
    """Raised when trying to define an already existing Mixin"""


class MissingMixin(CaframCtrlException):
    """Raised when a mixin does not exists"""


class MixinImportError(CaframCtrlException):
    """Raised when failed to import a Mixin"""


# Alias exceptions
class AlreadyDefinedAlias(CaframCtrlException):
    """Raised when trying to define an already existing alias"""


class MissingAlias(CaframCtrlException):
    """Raised when an alias does not exists"""


class ReadOnlyAlias(CaframCtrlException):
    """Raised when failed to import a Mixin"""


# Other


class NotMappingObject(CaframCtrlException):
    """Raised trying to patch an imutable object"""


class MissingCtrlAttr(CaframCtrlException):
    """Raised when trying to access an unknown key"""


# Mixin Exceptions
# ====================


class CaframMixinException(CaframException):
    """Generic Mixin cafram exception"""
