"""
Path mixins
"""

# Imports
################################################################

import os
from pprint import pprint
from typing import Optional

from ... import errors

# from ...lib.utils import list_parent_dirs
# from ...nodes import Node
from . import BaseMixin, LoadingOrder

# from .base import PayloadMixin


# Parent exceptions
class PathMixinException(errors.CaframMixinException):
    """Path Mixin Exceptions"""


# Child exceptions
class FileNotFound(PathMixinException):
    """When a file can't be find"""


# Conf mixins (Composed classes)
################################################################


class PathMixinGroup(BaseMixin):
    "Conf mixin that group all ConfMixins"

    mixin_order = LoadingOrder.POST


class PathMixin(PathMixinGroup):
    "Conf mixin that manage a path"

    mixin_key = "path"
    mixin_order = LoadingOrder.PRE

    # Get path
    path_dir = "."
    mixin_param__path_dir = "path"

    # Get default mode
    path_mode = None
    mixin_param__path_mode = "path_mode"

    # Get default anchor
    path_anchor = None
    mixin_param__path_anchor = "path_anchor"

    # Mode can be: abs, rel or auto
    _enum_mode = ["abs", "rel", None]

    # Comp schema
    _schema = {}

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not self.path_mode in self._enum_mode:
            msg = f"Invalid value for mode: {self.path_mode}, must be one of: {self._enum_mode}"
            raise errors.CaframException(msg)

        # Autoinit attrs:
        # self.path_anchor = anchor
        # self.path_dir = path
        # self.path_mode = mode

    def set_path(self, value, mode=None, anchor=None):
        self.path_dir = value
        if mode:
            self.path_mode = mode
        if anchor:
            self.path_anchor = anchor

    # Path helpers
    # -----------------
    def __repr__(self):
        "Represent itself"

        name = self.__class__.__name__
        ret = f"<{name} {self.get_path()}"

        # Change if anchored
        anchor = self.path_anchor
        if anchor:
            ret = f"<{name} [{anchor.get_dir()}]{self.get_path()}"

        # Add suffix
        suffix = ">"
        if self.path_mode:
            suffix = f" (mode={self.path_mode})>"
        ret = ret + suffix

        return ret

    def get_mode(self, lvl=0):
        "Return current path mode, abs or rel"

        if isinstance(self.path_mode, str):
            ret = self.path_mode
            return ret

        if self.path_anchor:
            lvl += 1
            ret = self.path_anchor.get_mode(lvl=lvl)
            return ret

        return None

    def get_anchor(self):
        "Return anchor if any"
        return self.path_anchor

    def get_anchors(self, itself: bool = False):
        """_summary_

        Args:
            itself (bool, optional): Leave current node in result if True. Defaults to True.

        Returns:
            _type_: _description_
        """

        ret = []

        ret.append(self)

        if self.path_anchor:
            tmp = self.path_anchor.get_anchors(itself=True)
            ret.extend(tmp)

        if not itself:
            ret = ret[1:]
        return ret

    def get_dir(
        self,
        mode: Optional[str] = None,
        clean: Optional[bool] = True,
        expand: Optional[bool] = True,
        start: Optional[str] = None,
        anchor=None,
    ):
        """_summary_

        Args:
            mode (Optional[str], optional): Can be 'abs' or 'rel'. If None, do not change. Defaults to None.
            clean (Optional[bool], optional): Clean the path, aka clean dir1/dir2/../../ . Defaults to False.
            start (Optional[str], optional): Enable 'rel' mode automatically, get relative path from a different dir that cwd. Defaults to None.
            anchor (_type_, optional): Anchor to use. Defaults to None.

        Returns:
            _type_: path
        """

        ret = None
        mode = mode or self.get_mode()
        start = start or None  # os.getcwd()
        if start:
            mode = "rel"

        # Prepare result
        path_dir = self.path_dir
        if expand:
            path_dir = os.path.expanduser(path_dir)
            path_dir = os.path.expandvars(path_dir)

        # Resolve name
        if os.path.isabs(path_dir):
            ret = path_dir
        else:
            anchor = anchor or self.path_anchor
            if anchor:
                ret = os.path.join(anchor.path_dir, path_dir)
            else:
                ret = path_dir

        # Clean
        if clean:
            ret = os.path.normpath(ret)

        # Ensure output format
        if mode == "rel":
            if os.path.isabs(ret) or start:
                ret = os.path.relpath(ret, start=start)
        elif mode == "abs":
            if not os.path.isabs(ret):
                ret = os.path.abspath(ret)
        elif mode is None:
            pass
        else:
            assert False, f"Bug Here, got;;: {mode}"

        return ret

    def get_path(self, **kwargs):
        return self.get_dir(**kwargs)
