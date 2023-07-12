import itertools
from ast import literal_eval


def simplest_type(s):
    "Return the closest python typed object from string"
    try:
        return literal_eval(s)
    except:
        return s


import os


def load_environ(prefix=None, names=None, replace=None):
    "Load and filter environement vars"

    ret = {}
    for key, value in os.environ.items():

        nkey = key
        if replace:
            nkey = key.replace(*replace)

        if prefix:
            if key.startswith(prefix):
                ret[nkey] = value
        elif names:
            if key in names:
                ret[nkey] = value
        else:
            ret[nkey] = value

    return ret


def dict_flatten(data):
    "Transform complex dict (/json) to flatenned dict"

    def traverse_data(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}__{key}" if path else key
                traverse_data(value, new_path)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                new_path = f"{path}__{index}"
                traverse_data(value, new_path)
        else:
            env_dict[path] = str(data)

    env_dict = {}
    traverse_data(data)
    return env_dict


def dict_unflatten(key_values):
    """Converts denormalised dict of (string -> string) pairs, where the first string
    is treated as a path into a nested list/dictionary structure


    If all the keys for that level parse as integers, then it's treated as a list
    with the actual keys only used for sorting
    This function is recursive, but it would be extremely difficult to hit a stack
    limit, and this function would typically by called once at the start of a
    program, so efficiency isn't too much of a concern.

    Copyright (c) 2018 Department for International Trade. All rights reserved.
    This work is licensed under the terms of the MIT license.
    For a copy, see https://opensource.org/licenses/MIT.

    Source: https://charemza.name/blog/posts/software-engineering/devops/structured-data-in-environment-variables/


    :Examples:

        >>> in = {
                "FOO__1__BAR": "setting-1",
                "FOO__1__BAZ": "setting-2",
                "FOO__2__FOO": "setting-3",
                "FOO__2__BAR": "setting-4",
                "FIZZ": "setting-5",
            }

        to the nested structure that this represents

        >>> out = {
                "FOO": [{
                    "BAR": "setting-1",
                    "BAZ": "setting-2",
                }, {
                    "FOO": "setting-3",
                    "BAR": "setting-4",
                }],
                "FIZZ": "setting-5",
            }

    """

    # Separator is chosen to
    # - show the structure of variables fairly easily;
    # - avoid problems, since underscores are usual in environment variables
    separator = "__"

    def get_first_component(key):
        return key.split(separator)[0]

    def get_later_components(key):
        return separator.join(key.split(separator)[1:])

    without_more_components = {
        key: simplest_type(value)
        for key, value in key_values.items()
        if not get_later_components(key)
    }

    with_more_components = {
        key: value for key, value in key_values.items() if get_later_components(key)
    }

    # print ("YOO")
    # print (without_more_components)
    # print(with_more_components)

    def grouped_by_first_component(items):
        def by_first_component(item):
            return get_first_component(item[0])

        # groupby requires the items to be sorted by the grouping key
        return itertools.groupby(
            sorted(items, key=by_first_component),
            by_first_component,
        )

    def items_with_first_component(items, first_component):
        return {
            get_later_components(key): value
            for key, value in items
            if get_first_component(key) == first_component
        }

    nested_structured_dict = {
        **without_more_components,
        **{
            first_component: dict_unflatten(
                items_with_first_component(items, first_component)
            )
            for first_component, items in grouped_by_first_component(
                with_more_components.items()
            )
        },
    }

    def all_keys_are_ints():
        def is_int(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        return all([is_int(key) for key, value in nested_structured_dict.items()])

    def list_sorted_by_int_key():
        return [
            value
            for key, value in sorted(
                nested_structured_dict.items(), key=lambda key_value: int(key_value[0])
            )
        ]

    return list_sorted_by_int_key() if all_keys_are_ints() else nested_structured_dict


run_tests = False

if run_tests:

    test_data = {
        "key1": True,
        "key2_tutu": "Yeahhh",
        "dict1": {
            "item1": {
                "name": "toto",
                "config": "ecnale",
            },
            "item2": {
                "name": "tot2",
                "config": "ecnal2",
            },
        },
        "list1": [
            "val1",
            "val2",
            {
                "name": "toto",
                "config": "ecnale",
            },
        ],
    }

    from pprint import pprint

    print("\nTEST 1: First set")
    print("===" * 8)

    print("=== regular")
    pprint(test_data)

    flattened = dict_flatten(test_data)
    print("=== flatened")
    pprint(flattened)

    t2 = dict_unflatten(flattened)
    print("=== restore")
    pprint(t2)

    print("VALIDATED? => ", test_data == t2)

    testdict1 = {
        "dict1": {
            "item1": {"config": "ecnale", "name": "toto"},
            "item2": {"config": "ecnal2", "name": "tot2"},
        },
        "key1": True,
        "key2_tutu": "Yeahhh",
        "list1": ["val1", "val2", {"config": "ecnale", "name": "toto"}],
    }

    print("\nTEST 2: Second set")
    print("===" * 8)

    env_dict = dict_flatten(testdict1)
    print(env_dict)

    data_dict = dict_unflatten(env_dict)
    print(data_dict == testdict1)

    print("\nTEST 3: Test from env")
    print("===" * 8)

    env_vars = """
    _prefix_DICT1__ITEM1__CONFIG='ecnale'
    _prefix_DICT1__ITEM1__NAME='toto'
    _prefix_DICT1__ITEM2__CONFIG='ecnal2'
    _prefix_DICT1__ITEM2__NAME='tot2'
    _prefix_KEY1='True'
    _prefix_KEY2_TUTU='Yeahhh'
    _prefix_LIST1__0='val1'
    _prefix_LIST1__1='val2'
    _prefix_LIST1__2__CONFIG='ecnale'
    _prefix_LIST1__2__NAME='toto'
    """

    env_vars2 = (
        {}
    )  # { line.split('=', 2)[0]: line.split('=', 2)[1].strip("'") for line in env_vars.splitlines() }

    for line in env_vars.splitlines():

        try:
            key, value = line.split("=", 2)
        except ValueError:
            continue

        key = key.lower()
        env_vars2[key] = value.strip("'")

    print(env_vars)
    print("===")
    pprint(env_vars2)
    print("===")
    pprint(dict_unflatten(env_vars2))

    # pprint (load_environ())
    pprint(load_environ("LC_"))
    pprint(load_environ("LC_", replace=("_", "__")))
    pprint(dict_unflatten(load_environ("LC_", replace=("_", "__"))))

    # Nested Vars
    pprint(
        {
            k: v
            for k, v in dict_unflatten(load_environ(replace=("_", "__"))).items()
            if isinstance(v, dict) and len(list(v.keys())) > 2
        }
    )
