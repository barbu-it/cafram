"""
Cafram Exceptions
"""


class CaframException(Exception):
    """Generic cafram exception"""


class MissingMixin(CaframException):
    """Raised a mixin does not exists"""


class AttributeError(CaframException, AttributeError):
    """Raised as AttributeError"""


class DictExpected(CaframException):
    "Raised when a dict was expected"


class ListExpected(CaframException):
    "Raised when a list was expected"
