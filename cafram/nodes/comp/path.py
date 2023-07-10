"""
Path mixins
"""

# Imports
################################################################

import os
from pprint import pprint

from ... import errors
from ...lib.utils import list_parent_dirs
from ...nodes import Node
from . import BaseMixin, LoadingOrder
from .base import PayloadMixin

# class FileReference:
#     """A FileReference Object

#     Useful for managing project paths

#     The path, once created is immutable, you choose how it behave one time
#     and done forever. They act a immutable local variable.


#     path: The path you want to manage
#     root: The root of your project, CWD else
#     keep: Returned path will be returned as absolute
#         True: Return default path from origin abs/rel
#         False: Return default path from root_path abs/rel

#     """

#     def __init__(self, path, root=None, keep=False):

#         assert isinstance(path, str), f"Got: {type(path)}"
#         root = root or os.getcwd()
#         self.raw = path
#         self.root = root
#         self.keep = keep


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

    # Param to store raw path
    raw = "."
    mixin_param__raw = "path"

    # Root (aka CWD) of path
    root = "."
    mixin_param__root = "path_root"

    # Mode can be: abs, rel or auto
    _enum_mode = ["abs", "rel", "auto"]
    mode = "auto"

    # Keep tells if get_path should return original path or not
    keep = True

    # pylint: disable=line-too-long
    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: ConfMixin",
        "description": "ConfMixin Configuration",
        "default": {},
        "properties": {
            "index": {
                "title": "Index",
                "description": "Name of the index key",
                # "default": index,
                "oneOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._super__init__(super(), *args, **kwargs)

        if not self.mode in self._enum_mode:
            msg = f"Invalid value for mode: {self.mode}, must be one of: {self._enum_mode}"
            raise errors.CaframException(msg)

        # Ensure default values are OK

        self.raw = self.raw or "."
        self.root = self.root or self.set_root_path()

    # Path helpers
    # -----------------
    # def __str__(self):
    #     return self.get_path()

    def set_path(self, value):
        "Set the path"
        self.raw = value

    def set_root_path(self, value=None):
        "Set the root path"
        if value is None:
            if self.is_abs():
                value = os.getcwd()
            else:
                value = "."
        self.root = value

    def is_abs(self):
        "Return true if the path is absolute"
        return os.path.isabs(self.raw)

    def is_root_abs(self):
        "Return true if the root path is absolute"
        return os.path.isabs(self.root)

    # Path methods
    # -----------------
    def get_path(self, start=None):
        "Return the absolute or relative path from root depending if root is absolute or not"

        if self.keep:
            if self.is_abs():
                return self.get_abs(start=start)
            return self.get_rel(start=start)
        else:
            if self.is_root_abs():
                return self.get_abs(start=start)
            return self.get_rel(start=start)

    def get_abs(self, start=None):
        "Return the absolute path from root"

        if self.is_abs():
            result = self.raw
        else:
            start = start or self.root
            real_path = os.path.join(start, self.raw)
            result = os.path.abspath(real_path) or "."
        return result

    def get_rel(self, start=None):
        "Return the relative path from root"

        if self.is_abs():
            start = start or self.root
            result = os.path.relpath(self.raw, start=start)
        else:
            start = start or self.root
            real_path = os.path.join(start, self.raw)
            result = os.path.relpath(real_path) or "."
        return result

    # Path extended methods
    # -----------------
    def get_dir(self):
        "Return directory name"
        return os.path.dirname(self.get_path())

    def get_name(self):
        "Return filename"
        return os.path.basename(self.get_path())

    def get_ext(self):
        "Return filename extensions, or empty string if not found"

        split = os.path.splitext(self.get_path())
        ret = ".".join(split[1:])
        return ret


class FilePathMixin(PathMixin):
    "Conf mixin that manage a file"


#     mixin_key = "file"

#     # # Param to store raw path
#     # raw = "."
#     # mixin_param__raw = "path"

#     # # Root (aka CWD) of path
#     # root = "."
#     # mixin_param__root = "path_root"

#     # # Mode can be: abs, rel or auto
#     # _enum_mode = ["abs", "rel", "auto"]
#     # mode = "auto"

#     # # Keep tells if get_path should return original path or not
#     # keep = True

#     file = "my_super_file.toto.yml"
#     file_prefix = "docker-compose"
#     file_suffix = ["yml", "yaml", "toml", "json"]
#     file_location = "current/up/down"

#     # mixin_param__raw = "path"


#     # pylint: disable=line-too-long
#     _schema = {
#         # "$defs": {
#         #     "AppProject": PaasifyProject.conf_schema,
#         # },
#         "$schema": "http://json-schema.org/draft-07/schema#",
#         "type": "object",
#         "title": "Mixin: ConfMixin",
#         "description": "ConfMixin Configuration",
#         "default": {},
#         "properties": {
#             "index": {
#                 "title": "Index",
#                 "description": "Name of the index key",
#                 # "default": index,
#                 "oneOf": [
#                     {
#                         "type": "string",
#                     },
#                     {
#                         "type": "null",
#                     },
#                 ],
#             },
#         },
#     }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # self._super__init__(super(), *args, **kwargs)

#         if not self.mode in self._enum_mode:
#             msg = f"Invalid value for mode: {self.mode}, must be one of: {self._enum_mode}"
#             raise errors.CaframException(msg)

#         # Ensure default values are OK

#         self.raw = self.raw or "."
#         self.root = self.root or self.set_root_path()


class PathFinderMixin(PathMixin):
    "Conf mixin that search files in paths"

    mixin_key = "file"

    # # Param to store raw path
    # raw = "."
    # mixin_param__raw = "path"

    # # Root (aka CWD) of path
    # root = "."
    # mixin_param__root = "path_root"

    # # Mode can be: abs, rel or auto
    # _enum_mode = ["abs", "rel", "auto"]
    # mode = "auto"

    # # Keep tells if get_path should return original path or not
    # keep = True

    file_name = None  # "my_super_file.toto.yml"
    file_prefix = None  # "docker-compose"
    file_suffix = None  # ["yml", "yaml", "toml", "json"]
    # file_location = "current/up/down"
    file_location = None
    file_type = "file"
    # file_type = "file|symlink|dir"

    # file_match = "first|last|all"
    file_match = "first"

    # mixin_param__raw = "path"

    # pylint: disable=line-too-long
    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: ConfMixin",
        "description": "ConfMixin Configuration",
        "default": {},
        "properties": {
            "index": {
                "title": "Index",
                "description": "Name of the index key",
                # "default": index,
                "oneOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_path(self.find_files())

    def find_files(self, file_name=None, file_match=None, file_location=None):
        "Find files"

        search_paths = None
        file_name = file_name or self.file_name
        file_match = file_match or self.file_match
        file_location = file_location or self.file_location

        search_path = self.get_path()

        if file_location is None:
            search_paths = [self.get_path()]
        elif file_location == "up":
            search_paths = list_parent_dirs(self.get_path())
        else:
            assert False, "Not supported"

        if not search_paths:
            return None

        files = []

        if isinstance(file_name, list):
            files = file_name
        elif file_name is None:

            # Get prefix and suffix
            file_prefix = self.file_prefix or []
            file_suffix = self.file_suffix or []
            if not isinstance(file_prefix, list):
                file_prefix = [file_prefix]
            if not isinstance(file_suffix, list):
                file_suffix = [file_suffix]

            # Assemble
            files = []
            if file_prefix and file_suffix:
                for prefix in file_prefix:
                    for suffix in file_suffix:
                        fpath = f"{prefix}.{suffix}"
                        files.append(fpath)
            elif not file_suffix:
                files = file_prefix
            else:
                assert False, "Extension search is not supported yet"

        else:
            files = [file_name]

        print("SEARCH FILE in", self.get_path())
        print("SEARCH FOR FILES", files)

        matches = []
        for i in search_paths:
            if self.file_type == "file":
                for file_ in files:
                    fpath = os.path.join(i, file_)
                    if os.path.isfile(fpath):
                        matches.append(os.path.join(i, file_))
                        if file_match == "first":
                            break

        if not matches:
            msg = f"Can't find any files matching: {self.file_name}/{self.file_prefix}.{self.file_suffix}"
            raise FileNotFound(msg)

        if file_match == "last":
            matches = matches[-1]
        elif file_match == "first":
            matches = matches[0]
        elif file_match != "all":
            msg = f"Invalid config file_match: {file_match}"
            raise FileNotFound(msg)

        # print ("MATCHES")
        # pprint(matches)
        return matches

        # # self._super__init__(super(), *args, **kwargs)

        # if not self.mode in self._enum_mode:
        #     msg = f"Invalid value for mode: {self.mode}, must be one of: {self._enum_mode}"
        #     raise errors.CaframException(msg)

        # # Ensure default values are OK

        # self.raw = self.raw or "."
        # self.root = self.root or self.set_root_path()
