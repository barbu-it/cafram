# Import the whole parent library in way to prevent user to add all exception
# pylint: disable=unused-wildcard-import, wildcard-import
# from cafram.errors import *

import cafram.errors as errors

# NodeCtrl Exceptions
# ====================


class CaframCtrlException(errors.CaframException):
    """Generic Controller cafram exception"""


# Missings

# Mixin exceptions


class AlreadyDefinedMixin(errors.CaframCtrlException):
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


class BadArguments(CaframCtrlException):
    "Raised when calling a function wihtout proper args/kwargs"


# Mixin Exceptions
# ====================


class CaframMixinException(errors.CaframException):
    """Generic Mixin cafram exception"""
