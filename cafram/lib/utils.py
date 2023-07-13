"""Utils library

"""
import importlib
import inspect
import io
import json
import logging
import os
import re
import sys

# =====================================================================
# Class attribute helpers functions
# =====================================================================
from pprint import pprint

# Support both pyaml and ruamel. pyaml implementation is better here
# import ruamel.yaml
import yaml

# if "ruamel.yaml" in sys.modules:
#     # Setup YAML object
#     yaml = ruamel.yaml.YAML()
#     yaml.version = (1, 1)
#     yaml.default_flow_style = False
#     # yaml.indent(mapping=3, sequence=2, offset=0)
#     yaml.allow_duplicate_keys = True
#     yaml.explicit_start = True


# =====================================================================
# Misc functions
# =====================================================================

# Sort hthings here ...


log = logging.getLogger(__name__)


# TODO: TO be renamed: remap_classattr_from_kwargs
def update_classattr_from_dict(obj, kwargs, prefix="mixin_param__", bound_methods=True):

    """List args/kwargs parameters

    Scan a given object `obj`, find all its attributes starting with `prefix`,
    and update all matched attributes from kwargs
    """

    # Params, left part is constant !
    # mixin_param__<SOURCE> = <EXPECTED_NAME>
    assert isinstance(kwargs, dict)

    ret = {}
    reduced = [item for item in dir(obj) if item.startswith(prefix)]
    # pprint(reduced)
    for attr in reduced:

        attr_name = attr.replace(prefix, "")
        if not attr_name:
            continue

        attr_match = getattr(obj, attr, None) or attr_name
        if not isinstance(attr_match, str):
            continue

        if attr_match and attr_match in kwargs:
            attr_value2 = kwargs[attr_match]

            assert attr_value2 != "preparse", f"{attr_value2}"

            if callable(attr_value2):
                assert False, "MATCH"
                attr_value2 = attr_value2.__get__(obj)
            ret[attr_name] = attr_value2

    return ret


# =====================================================================
# String utils
# =====================================================================

# pylint: disable=redefined-builtin
def truncate(data, max=72, txt=" ..."):
    "Truncate a text to max lenght and replace by txt"

    max = -1
    data = str(data)
    if max < 0:
        return data
    if len(data) > max:
        return data[: max + len(txt)] + txt
    return data


# TODO: Add tests on this one
def to_domain(string, sep=".", alt="-"):
    "Transform any string to valid domain name"

    domain = string.split(sep)
    result = []
    for part in domain:
        part = re.sub("[^a-zA-Z0-9]", alt, part)
        part.strip(alt)
        result.append(part)

    return ".".join(result)


# =====================================================================
# Dict utils
# =====================================================================


def merge_dicts_v1(dict1, dict2):
    """Given two dictionaries, merge them into a new dict as a shallow copy.

    Compatibility for Python 3.5 and above"""
    # Source: https://stackoverflow.com/a/26853961/2352890
    result = dict1.copy()
    result.update(dict2)
    return result


def merge_dicts(*dicts):
    """Given X dictionaries, merge them into a new dict as a shallow copy.

    Compatibility for Python 3.5 and above"""

    assert len(dicts) > 1

    ret = dicts[0].copy()
    for data in dicts[1:]:
        ret.update(data)

    return ret


def merge_keyed_dicts(*dicts, skip_invalid=False):
    """Given two keyed dictionaries, merge them into a new dict as a shallow copy.

    :Examples:
        >>> dict1 = {
                 "key1": {
                     "subkey1": "val1",
                     "subkey2": "val2",
                 },
                 "key2": {
                     "subkey1": "val1",
                     "subkey2": "val2",
                 },
             }
        >>> dict2 = {
                 "key2": {
                     "subkey2": "UPDATED",
                 },
                 "key3": {
                     "subkey1": "CREATED",
                 },
             }
        >>> out = {
                 "key1": {
                     "subkey1": "val1",
                     "subkey2": "val2",
                 },
                 "key2": {
                     "subkey1": "val1",
                     "subkey2": "UPDATED",
                 },
                 "key3": {
                     "subkey1": "CREATED",
                 },
             }


    Compatibility for Python 3.5 and above"""
    # Source: https://stackoverflow.com/a/26853961/2352890

    assert len(dicts) > 1

    ret = dicts[0].copy()

    if not isinstance(ret, dict):
        if not skip_invalid:
            assert isinstance(ret, dict), f"Expected a dict, got {type(ret)}: {ret}"

    for data in dicts[1:]:

        if not isinstance(data, dict):
            if not skip_invalid:
                assert isinstance(
                    data, dict
                ), f"Expected a dict, got {type(data)}: {data}"
            continue

        for key, val in data.items():

            if not key in ret:
                ret[key] = {}

            assert isinstance(val, dict)
            assert isinstance(ret[key], dict)

            ret[key].update(val)

    return ret


def dict_to_fdict(payload, sep="__"):
    """Transform dict to fdict"""
    assert False, f"Not implemented yet: {payload}, {sep}"


def fdict_to_dict(payload, sep="__"):
    """Transform fdict to dict


    :Examples:

        >>> payload = {
                "lvl1__key1": "val1",
                "lvl1__key2": "val2",
                "lvl1__lvl2__key1": "val1",
                "lvl1__lvl2__key2": "val1",
            }
        >>> out = {
                "lvl1: {
                    "key1: "val1",
                    "key2: "val2",
                    "lvl2": {
                        "key1: "val1",
                        "key2: "val2",
                    }
                },
            }
    """

    ret = {}
    for key, val in payload.items():

        parts = key.split(sep)

        parent = ret
        if len(parts) > 1:
            for part in parts[:-1]:
                if not part in parent:
                    parent[part] = {}
                parent = ret[part]
        key = parts[-1]
        parent[key] = val

    return ret


# =====================================================================
# List utils
# =====================================================================


# TODO: Add tests on this one
def first(array):
    "Return the first element of a list or None"
    # return next(iter(array))
    array = list(array) or []
    result = None
    if len(array) > 0:
        result = array[0]
    return result


def duplicates(_list):
    """Check if given list contains duplicates"""
    known = set()
    dup = set()
    for item in _list:
        if item in known:
            dup.add(item)
        else:
            known.add(item)

    if len(dup) > 0:
        return list(dup)
    return []


# TODO: Rename this to flatten_lists
def flatten(array):
    "Flatten any arrays nested arrays"
    if array == []:
        return array
    if isinstance(array[0], list):
        return flatten(array[0]) + flatten(array[1:])
    return array[:1] + flatten(array[1:])


# =====================================================================
# Data conversion
# =====================================================================

# This is redundant with other functions ....
def serialize(obj, fmt="json"):
    "Serialize anything, output json like compatible (destructive)"

    # pylint: disable=unnecessary-lambda
    obj = json.dumps(obj, default=lambda o: str(o), indent=2)

    if fmt in ["yaml", "yml"]:
        # Serialize object in json first
        obj = json.loads(obj)

        # Convert json to yaml
        string_stream = io.StringIO()
        yaml.dump(obj, string_stream)
        output_str = string_stream.getvalue()
        string_stream.close()

        # Remove 2 first lines of output
        obj = output_str.split("\n", 2)[2]

    return obj


def to_bool(string):
    "Return a boolean"
    if isinstance(string, bool):
        return string
    return string.lower() in ["true", "1", "t", "y", "yes"]


# if "ruamel.yaml" in sys.modules:

#     # TODO: add tests
#     def from_yaml(string):
#         "Transform YAML string to python dict"
#         return yaml.load(string)

#     # TODO: add tests
#     def to_yaml(obj, headers=False):
#         "Transform obj to YAML"
#         options = {}
#         string_stream = StringIO()

#         if isinstance(obj, str):
#             obj = json.loads(obj)

#         yaml.dump(obj, string_stream, **options)
#         output_str = string_stream.getvalue()
#         string_stream.close()
#         if not headers:
#             output_str = output_str.split("\n", 2)[2]
#         return output_str


if "yaml" in sys.modules:

    # TODO: add tests
    def from_yaml(string):
        "Transform YAML string to python dict"
        return yaml.safe_load(string)

    # TODO: add tests
    def to_yaml(obj, headers=False):
        "Transform obj to YAML"
        options = {}
        return yaml.safe_dump(obj)


# TODO: add tests
def to_json(obj, nice=True):
    "Transform JSON string to python dict"
    if nice:
        return json.dumps(obj, indent=2)
    return json.dumps(obj)


# TODO: add tests
def from_json(string):
    "Transform JSON string to python dict"
    return json.loads(string)


# TODO: add tests
def to_dict(obj):
    """Transform JSON obj/string to python dict

    Useful to transofmr nested dicts as well"""
    if not isinstance(obj, str):
        obj = json.dumps(obj)
    return json.loads(obj)


# =====================================================================
# Python modules
# =====================================================================


def import_from_str(name):
    "Import a module from a string. Returns ModuleNotFoundError if does not exists"

    return importlib.import_module(name)


def get_pkg_dir(name):
    """Return the dir where the actual paasify source code lives"""

    # pylint: disable=import-outside-toplevel
    mod = import_from_str(name)
    return os.path.dirname(mod.__file__)


# New API

# Duplicate of import_from_str
def import_module_pkg(package):
    "Simple helper to load dynamically python modules"
    return importlib.import_module(package)


def import_module_from(package, *names):
    "Allow to import from python packages"

    mod = import_module(package)

    names_len = len(names)
    if names_len == 0:
        return mod
    if names_len == 1:
        return getattr(mod, names[0])
    if names_len > 1:
        ret = []
        for name in names:
            ret.append(getattr(mod, name))
        return set(ret)


def import_module(name):
    "Simple helper to load python modules"

    if ":" in name:
        package, comp = name.rsplit(":", 1)
        return import_module_from(package, comp)

    return import_module_pkg(name)


# =====================================================================
# File management
# =====================================================================


def read_file(file):
    "Read file content"
    with open(file, encoding="utf-8") as _file:
        return "".join(_file.readlines())


def write_file(file, content):
    "Write content to file"

    file_folder = os.path.dirname(file)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    with open(file, "w", encoding="utf-8") as _file:
        _file.write(content)


# =====================================================================
# Dir management
# =====================================================================


# Migrated into cafram2
def ensure_dir_exists(path):
    """Ensure directories exist for a given path"""
    if not os.path.isdir(path):
        log.info(f"Create directory: {path}")
        os.makedirs(path)
        return True
    return False


# Migrated into cafram2
def ensure_parent_dir_exists(path):
    """Ensure parent directories exist for a given path"""
    parent = os.path.dirname(os.path.normpath(path))
    return ensure_dir_exists(parent)


def filter_existing_files(root_path, candidates):
    """Return only existing files"""
    result = [
        os.path.join(root_path, cand)
        for cand in candidates
        if os.path.isfile(os.path.join(root_path, cand))
    ]
    return list(set(result))


def list_parent_dirs(path):
    """
    Return a list of the parents paths
    path treated as strings, must be absolute path
    """

    result = [path]

    was_relative = False
    path_abs = path
    pwd = None
    if not os.path.isabs(path):
        pwd = os.getcwd()
        path_abs = os.path.join(pwd, path)
        was_relative = True

    val = path_abs
    while val and val != os.sep:
        val = os.path.split(val)[0]
        result.append(val)

    if was_relative:
        return [os.path.relpath(path, start=pwd) for path in result]
    return result


def find_file_up(names, paths):
    """
    Find every files names in names list in
    every listed paths
    """
    assert isinstance(names, list), f"Names must be array, not: {type(names)}"
    assert isinstance(paths, list), f"Paths must be array, not: {type(names)}"

    result = []
    for path in paths:
        for name in names:
            file_path = os.path.join(path, name)
            if os.access(file_path, os.R_OK):
                result.append(file_path)

    return result
