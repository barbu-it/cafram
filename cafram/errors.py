"""
Cafram Exceptions
"""

# Parent classes
# ====================


class CaframException(Exception):
    """Generic cafram exception"""


class CaframMixinException(CaframException):
    """Generic Mixin cafram exception"""


class CaframCtrlException(CaframException):
    """Generic Controller cafram exception"""


# Parent classes
# ====================


class MissingMixin(CaframException):
    """Raised a mixin does not exists"""


class AttributeError(CaframException, AttributeError):
    """Raised as AttributeError"""


class DictExpected(CaframException):
    "Raised when a dict was expected"


class ListExpected(CaframException):
    "Raised when a list was expected"
