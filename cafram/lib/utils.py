"""Utils library

"""

import io
import os
import json
import re
import importlib

from io import StringIO
import ruamel.yaml


# Setup YAML object
yaml = ruamel.yaml.YAML()
yaml.version = (1, 1)
yaml.default_flow_style = False
# yaml.indent(mapping=3, sequence=2, offset=0)
yaml.allow_duplicate_keys = True
yaml.explicit_start = True


# =====================================================================
# Misc functions
# =====================================================================


def import_from_str(name):
    "Import a module from a string. Returns ModuleNotFoundError if does not exists"

    return importlib.import_module(name)


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


def merge_dicts(dict1, dict2):
    """Given two dictionaries, merge them into a new dict as a shallow copy.

    Compatibility for Python 3.5 and above"""
    # Source: https://stackoverflow.com/a/26853961/2352890
    result = dict1.copy()
    result.update(dict2)
    return result


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


# TODO: Add tests on this one
def first(array):
    "Return the first element of a list or None"
    # return next(iter(array))
    array = list(array) or []
    result = None
    if len(array) > 0:
        result = array[0]
    return result


# TODO: add tests
def from_yaml(string):
    "Transform YAML string to python dict"
    return yaml.load(string)


# TODO: add tests
def to_yaml(obj, headers=False):
    "Transform obj to YAML"
    options = {}
    string_stream = StringIO()

    if isinstance(obj, str):
        obj = json.loads(obj)

    yaml.dump(obj, string_stream, **options)
    output_str = string_stream.getvalue()
    string_stream.close()
    if not headers:
        output_str = output_str.split("\n", 2)[2]
    return output_str


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


def flatten(array):
    "Flatten any arrays nested arrays"
    if array == []:
        return array
    if isinstance(array[0], list):
        return flatten(array[0]) + flatten(array[1:])
    return array[:1] + flatten(array[1:])
