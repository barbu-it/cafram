"""
Cafram Exceptions
"""


class CaframException(Exception):
    """Generic cafram exception"""


class MissingMixin(CaframException):
    """Raised a mixin does not exists"""


class AttributeError(CaframException, AttributeError):
    """Raised as AttributeError"""
