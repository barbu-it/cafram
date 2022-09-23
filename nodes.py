"""
Config Node classes
"""
# pylint: disable=too-many-lines
# pylint: disable=too-few-public-methods
# pylint: disable=arguments-renamed
# pylint: disable=arguments-differ
# pylint: disable=unused-argument

import os
import copy
import inspect
import textwrap
import json
from pprint import pprint

import jsonschema

from cafram.base import (
    Base,
    DictExpected,
    ListExpected,
    NotExpectedType,
    ClassExpected,
    InvalidSyntax,
    SchemaError,
)
from cafram.utils import serialize, json_validate


# Functions
# =====================================


def map_container_class(payload):  # map_container_class
    "Map list or dict to cafram classes, otherwise keep value as is"

    # if payload is None:
    #     return NodeVal
    if isinstance(payload, dict):
        return NodeMap
        # return NodeDict

    if isinstance(payload, list):
        return NodeList

    return type(payload)


def map_node_class(payload):  # map_node_class
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        return NodeMap
        # return NodeDict
    if isinstance(payload, list):
        return NodeList

    return NodeVal


# Simple attributes class
# =====================================

# pylint: disable=too-many-instance-attributes
class NodeVal(Base):
    """
    Base configuration class

    * conf_default: Holds the default configuration.
    if it's a dict, it will be merged with acutal user config, otherwise

    * conf_struct: If a value si present in payload, an instance will be created with
    default data, unless the key is not present (in case of dicts)
    """

    # Class public parameters
    conf_default = None
    conf_schema = None
    conf_ident = None
    conf_children = None

    # Class internal attributes
    _nodes = None
    _node_root = None
    _node_parent = None

    _node_conf_raw = None
    _node_conf_parsed = None
    _node_autoconf = 0

    def __init__(self, *args, parent=None, payload=None, autoconf=None, **kwargs):

        # Call parents
        # pylint: disable=super-with-arguments
        super(NodeVal, self).__init__(*args, **kwargs)
        self.log.debug(f"__init__: NodeVal/{self}")

        # Register parent
        self._node_parent = parent or self
        self._node_root = getattr(parent, "_node_root", None) or self

        # Manage autoconf levels
        if autoconf is None:
            autoconf = getattr(self._node_parent, "_node_autoconf", 0)
        self._node_autoconf = (autoconf - 1) if autoconf > 0 else autoconf

        # Manage node level
        self._node_lvl = getattr(self._node_parent, "_node_lvl", -1) + 1

        # Auto init object
        self.deserialize(payload)

    # Serialization
    # -----------------

    def deserialize(self, payload):
        "Transform json to object"

        # pylint: disable=W0212
        self._nodes = self.__class__._nodes
        self._node_conf_raw = payload

        # Parse config

        payload1 = self._node_conf_validate(payload)
        payload2 = self.node_hook_transform(payload1)
        payload3 = self._node_conf_defaults(payload2)

        # Preset default ident
        if self.conf_ident:
            self.ident = self.conf_ident.format(**locals())

        # Pre hook
        payload4 = self.node_hook_conf(payload3)

        # User report
        if payload1 != payload4:
            self.log.debug(
                f"Payload transformation for: {self}\nFrom: {payload1}\nTo: {payload3}"
            )

        # Create children nodes

        self._node_conf_build(payload4)

        # Post hook
        self.node_hook_children()

    def serialize(self, mode="parsed"):
        "Transform object to json"

        if mode == "raw":
            value = self._node_conf_raw
        elif mode == "parsed":
            value = self._node_conf_parsed

        return value

    # User hooks
    # -----------------

    # Available hooks:
    # node_hook_transform:
    #   - Payload modifications only
    # node_hook_conf
    #   - Payload is done, preset values
    # node_hook_children
    #   - Once the children has been created

    # pylint: disable=no-self-use
    def node_hook_transform(self, payload):
        "Placeholder to transform config after validation"
        return payload

    # pylint: disable=no-self-use
    def node_hook_conf(self, payload):
        "Placeholder to executes after configuration build"
        return payload

    def node_hook_children(self):
        "Placeholder to transform object once onfig has been done"

    # Configuration parser
    # -----------------

    def _node_conf_defaults(self, payload):
        """Return payload or default value"""

        return payload or self.conf_default

    def _node_conf_validate(self, payload):
        """Validate config against schema

        This function will only works if:
        * self.conf_schema is not None
        * self.conf_schema conatins the "$schema" key
        """

        # old_payload = payload

        # pylint: disable=E1135
        if isinstance(self.conf_schema, dict):
            if "$schema" in self.conf_schema:

                try:
                    payload = json_validate(self.conf_schema, payload)
                except jsonschema.exceptions.ValidationError as err:

                    self.log.critical(f"Value: {err.instance}")
                    self.log.critical(f"Payload: {payload}")
                    raise SchemaError(
                        f"Schema validation error for {self}: {err.message}"
                    ) from err

                except jsonschema.exceptions.SchemaError as err:
                    # print("Bug in schema for ", self)
                    # print(err)

                    # print("PAYLOAD")
                    # pprint(payload)
                    # print("SCHEMA")
                    # pprint(self.conf_schema)
                    # print("BBBUUUUUGGGGGGG on schema !!!")
                    # # print(traceback.format_exc())
                    raise Exception(err) from err

                # if old_payload != payload:
                #     print("OLD CONFIG WITHOUT DEFAULTS", old_payload)
                #     print("NEW CONFIG WITH DEFAULTS", payload)

        # else:
        #     print(f"NO SCHEMA VALIDATION FOR {self}")

        return payload

    # Simple Class implementation
    # -----------------
    def _node_conf_build(self, payload):
        "Just assign the value, thats all"
        self._nodes = None
        self._node_conf_parsed = payload

    # Misc
    # -----------------

    def from_json(self, payload):
        "Load from json string"

        payload = json.loads(payload)
        return self.deserialize(payload)

    # Node management
    # -----------------

    # Methods:
    # get_children
    #   - return only node objects
    #   - support recur
    # get_value
    #   - return ALL but node objects

    def get_children(self, lvl=0, explain=False, leaves=False):
        """A nodeVal can't have a children, so always return None"""
        result = None
        if leaves:
            result = self
        if explain:
            return {
                "obj": self,
                "value": self.get_value(),
                f"subtype (auto:{self._node_autoconf})": self.conf_children,
                "children": result,
            }
        return result

    def get_value(self, **kwargs):
        """Return the _nodes value (value+children)"""

        return self._node_conf_parsed

    # Sibling management
    # -----------------

    def is_root(self):
        """Return True if object is root"""
        if self._node_parent and self._node_parent == self:
            return True
        return False

    def get_parent(self):
        """Return first parent"""
        return self._node_parent or None

    def get_parent_root(self):
        """Return root parent object"""
        return self._node_root

    def get_parents(self):
        "Return all parent of the object"

        parents = []
        current = self
        parent = self._node_parent or None
        while parent is not None and parent != current:
            if parent not in parents:
                parents.append(parent)
                current = parent
                parent = getattr(current, "_node_parent")

        return parents

    # Dumper
    # -----------------

    # pylint: disable=redefined-builtin
    def dump(self, explain=True, all=True, **kwargs):
        """Output a dump of the object, helpful for troubleshooting prupose"""

        # pylint: disable=super-with-arguments
        super(NodeVal, self).dump(**kwargs)

        _node_conf_parsed = self._node_conf_parsed
        _node_conf_raw = self._node_conf_raw

        print("  Node info:")
        print("  -----------------")
        print(f"    Node level: {self._node_lvl}")
        print(f"    Node root: {self._node_root}")
        print(f"    Node parents: {self.get_parents()}")
        print("")

        if all and _node_conf_parsed is not None:
            msg = "(same as Raw Config)"
            if _node_conf_raw != _node_conf_parsed:
                msg = "(different from Raw Config)"

                print("  Raw Config:")
                print("  -----------------")
                out = serialize(_node_conf_raw, fmt="yaml")
                print(textwrap.indent(out, "    "))

            print("  Parsed Config:", msg)
            print("  -----------------")
            out = serialize(_node_conf_parsed, fmt="yaml")
            print(textwrap.indent(out, "    "))
            # print ("")

        if all:
            print("  Children:")
            print("  -----------------")
            children = self.get_children(lvl=-1, explain=False, leaves=True)
            out = serialize(children)
            # out = pformat(children, indent=2, width=5)
            print(textwrap.indent(out, "    "))
            print("")

            print("  Value:")
            print("  -----------------")
            children = self.get_value(explain=explain)
            # out = serialize(children, fmt="yaml")
            out = serialize(children, fmt="json")
            print(textwrap.indent(out, "    "))
            print("")

        print("  Whole config:")
        print("  -----------------")
        children = self.get_value(lvl=-1)
        # out = serialize(children, fmt="yaml")
        out = serialize(children, fmt="json")
        print(textwrap.indent(out, "    "))
        print("")

        # out = pformat(children)
        # print (textwrap.indent(out, '    '))

        # print("\n")


# Test Class Data
# =====================================


class NodeListIterator:
    "NodeList iterator"

    def __init__(self, conf_inst):

        self._nodes = conf_inst._nodes
        self._current_index = 0
        self._max_index = len(conf_inst._nodes)

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < self._max_index:
            result = self._nodes[self._current_index]
            self._current_index += 1
            return result
        raise StopIteration


class NodeList(NodeVal):
    """NodeList"""

    _nodes = []
    _node_conf_parsed = []

    # Overrides
    # -------------------

    def _node_conf_defaults(self, payload):
        """Return payload or default list (NodeList)"""

        payload = payload or self.conf_default or []
        if not isinstance(payload, list):
            raise ListExpected(f"A list was expected for {self}, got: {payload}")

        return payload

    def _node_conf_build(self, payload):
        "Just assign the value, thats all NodeList"

        self._node_conf_parsed = payload
        if not payload:
            self._nodes = []
            return

        cls = self.conf_children

        results = []
        count = 0
        are_children = False
        for item in payload:

            ident = f"{self.ident}_{count}"

            if self._node_autoconf != 0:
                # If not found, first element of the list determine class
                # cls = cls or map_node_class(item)
                cls = cls or map_container_class(item)
                # print ("AUTOGUESS CLASS: ", cls)

            if cls:
                if not inspect.isclass(cls):
                    raise ClassExpected(
                        f"A class was expected for {self}.conf_struct, got {type(cls)}: {cls}"
                    )

                if issubclass(cls, NodeVal):
                    are_children = True
                    result = cls(parent=self, ident=ident, payload=item)
                elif cls:

                    are_children = False

                    if item and not isinstance(item, cls):
                        msg = f"""Wrong type in list: '{item}' is not
                        a '{cls.__name__}' type in '{payload}'"""
                        raise NotExpectedType(msg)

                    result = item
                    if item:
                        result = cls(item)

                    # try:

                    # except (ValueError, TypeError) as err:
                    #     msg = f"""Wrong type in list: '{item}' is not a
                    # '{cls.__name__}' type in '{payload}'"""
                    #     raise NotExpectedType(msg) from err

                results.append(result)
            else:
                results.append(item)

            count = +1

        if are_children:
            self._nodes = results
        else:
            self._node_conf_parsed = results

    def __iter__(self):
        return NodeListIterator(self)

    def get_children(self, lvl=0, explain=False, leaves=False):
        "Return NodeList childs"
        result = []
        for child in self._nodes:
            # if isinstance(child, NodeVal):
            if lvl != 0:
                value = child.get_children(lvl=lvl - 1, explain=explain, leaves=leaves)
            else:
                value = child

            if leaves:
                value = value or child

            result.append(value)

        if explain:
            return {
                "obj": self,
                "value": self.get_value(),
                f"subtype (auto:{self._node_autoconf})": self.conf_children,
                "children": result,
            }

        return result

    def get_value(self, lvl=0, explain=False):
        "Return NodeList value"
        result = []
        for child in self._nodes:
            if lvl != 0:
                result.append(child.get_value(lvl=lvl - 1, explain=explain))
            else:
                result.append(child)

        return result or self._node_conf_parsed


# NodeDict
# =====================================


class NodeDictItem:
    """Children configuration for NodeDict"""

    def __init__(
        self,
        *args,
        key=None,
        cls=None,
        action="set",
        hook=None,
        default=None,
        attr=None,
        **kwargs,
    ):

        self.key = key
        self.attr = attr or None
        self._ident = None
        self.hook = hook

        self.cls = cls or None
        self.default = default or None
        self.action = action

    @property
    def ident(self) -> str:
        "Return ident"
        return self.attr or self.key

    def __repr__(self):
        result = [f"{key}={val}" for key, val in self.__dict__.items() if val]
        result = "|".join(result)
        return f"Remap:{result}"


class NodeDict(NodeVal):
    "Node Dict container"

    _nodes = {}
    _node_conf_struct = None
    _node_conf_parsed = {}

    # # TODO: https://www.pythonlikeyoumeanit.com/Module4_OOP/Special_Methods.html
    # __len__
    # __getitem__(self, key)
    # __setitem__(self, key, item)
    # __contains__(self, item)
    # __iter__(self)
    # __next__(self)

    # Overrides
    # -------------------

    def get_children(self, lvl=0, explain=False, leaves=False):
        "Return NodeDict childs"
        result = {}
        for name, child in self._nodes.items():
            if isinstance(child, NodeVal):
                if lvl != 0:
                    value = child.get_children(
                        lvl=lvl - 1, explain=explain, leaves=leaves
                    )
                else:
                    value = child

                if leaves:
                    value = value or child

                result[name] = value

        if explain:
            return {
                "obj": self,
                f"subtype (auto:{self._node_autoconf})": self.conf_children,
                "value": self.get_value(),
                "children": result,
            }
        return result

    def get_value(self, lvl=0, explain=False):
        "Return NodeDict value"
        result = dict(self._node_conf_parsed)
        for name, child in self._nodes.items():
            if lvl != 0:
                result[name] = child.get_value(lvl=lvl - 1)
            else:
                del result[name]

        return result

    def _node_conf_gen_struct(self, payload):
        """Assemble conf_struct fron conf_children for NodeDict"""

        # Conf_children default behavior: auto from dict
        conf_children = self.conf_children or {}
        conf_struct = None

        # 1. Leave as is
        if isinstance(conf_children, list):
            self.log.debug(f"    > Confstruct for list")
            pass

        # 2. Direct generate
        elif inspect.isclass(conf_children):
            self.log.debug(f"    > Confstruct for {conf_children}")

            conf_children = [
                {"key": key, "default": val, "cls": conf_struct}
                for key, val in payload.items()
            ]

        # 3. Auto generate
        elif self._node_autoconf != 0:
            self.log.debug(f"    > Confstruct for {self._node_autoconf}")

            conf_children = [
                {"key": key, "default": val, "cls": map_container_class(val)}
                for key, val in payload.items()
            ]

        # 4. Auto guess from payload
        elif not conf_children:
            self.log.debug("    > Confstruct for {}")
            conf_children = [
                {"key": key, "default": val, "cls": type(val)}
                for key, val in payload.items()
            ]

        # Actually build conf_Struct
        conf_struct = [NodeDictItem(**conf) for conf in conf_children]

        # Developper sanity check
        if not isinstance(conf_struct, list):
            raise ListExpected(
                f"A list was expected for conf_children, got : {conf_struct}, {conf_children}"
            )

        return conf_struct

    def _node_conf_defaults(self, payload):
        """Return payload merged with default value (NodeDict)"""

        payload = payload or {}
        conf_default = self.conf_default or {}

        # Payload sanity check
        if not isinstance(payload, dict):
            raise DictExpected(f"A dict was expected for {self}, got: {payload}")
        if not isinstance(conf_default, dict):
            raise DictExpected(
                f"A dict was expected for {self}/conf_default, got: {conf_default}"
            )

        # Update payload
        result = copy.deepcopy(conf_default)
        result.update(payload)
        payload = result

        # Generate conf_struct
        conf_struct = self._node_conf_gen_struct(payload)
        self.log.debug(f"Applied conf_children for {self}: {conf_struct}")
        self._node_conf_struct = conf_struct

        # Clean config
        for item_def in conf_struct:

            key = item_def.key
            cls = item_def.cls
            action = item_def.action

            # Get value
            if key is None:
                continue

            # Check value
            value = payload.get(key, item_def.default or None)
            if action == "unset":
                value = value or None
            elif action == "drop":
                del payload[key]
                continue

            if key == "TEST":
                pprint(conf_struct)

            payload[key] = value

        # print(f"Actual payload {self}: {payload}")

        return payload

    def _node_conf_build(self, payload):
        "For NodeDict"

        payload = payload or {}
        self._node_conf_parsed = payload
        self._nodes = {}

        # Developper sanity check
        if not isinstance(payload, dict):
            self.log.warning(
                "Developper must call node_hook_conf() first if data are not dict"
            )
            raise DictExpected(
                f"A dictionnary was expected for {self}, got {type(payload).__name__}: {payload}"
            )

        conf_struct = self._node_conf_struct

        # # 1. Append other keys only if not already set
        # done_keys = [remap.key for remap in conf_struct if remap.ident]
        # for key, val in payload.items():
        #     if key not in done_keys:
        #         self._nodes[key] = val

        # 2. Process each children

        for item_def in conf_struct:

            # Required for modified items during the loop to let __getattr__ to work correctly
            # self._node_conf_parsed = payload

            key = item_def.key
            attr = item_def.attr or key
            cls = item_def.cls
            action = item_def.action
            hook = item_def.hook

            # Get value
            value = None
            if key:
                value = self._node_conf_parsed.get(key)

            # Check action
            if not value:
                if action == "unset":
                    # value = None
                    cls = None
                elif action == "drop":
                    continue

            if cls:
                # Instanciate or cast value
                if issubclass(cls, NodeVal):
                    self.log.debug(
                        f"    > Instanciate Node object: {attr}={cls}(payload={value})"
                    )
                    node = cls(parent=self, ident=item_def.ident, payload=value)

                    # Update parsed conf
                    value = node.serialize(mode="parsed")
                    if attr:
                        self._nodes[attr] = node

                else:
                    if not value:
                        self.log.debug(
                            f"    > Instanciate null child object: {attr}={cls}()"
                        )
                        value = cls()
                    elif isinstance(value, cls):
                        self.log.debug(
                            f"    > Instanciate child object: {attr}={cls}({value})"
                        )
                        value = cls(value)
                    else:
                        self.log.debug(
                            f"    > Instanciate empty child object: {attr}={cls}()"
                        )
                        try:
                            value = cls(value)
                        except Exception as err:
                            self.log.critical(
                                f"Type mismatch between: {cls} and {value}"
                            )
                            raise NotExpectedType(err)
            else:
                # Forward value
                self.log.debug(f"    > Instanciate direct assignment: {attr}={value}")
                value = value

            if key:
                self._node_conf_parsed[key] = value

            if hook:
                fun = getattr(self, hook)
                self.log.debug("Execute hook: ", hook, fun)
                fun()
                # _payload = fn(payload)
                # if _payload != payload:
                #     print ("Payload modified!")
                #     self._node_conf_parsed = _payload

        # 1. Append other keys only if not already set
        # done_keys = [remap.key for remap in conf_struct if remap.ident]
        # for key, val in payload.items():
        #     if key not in done_keys:
        #         self._nodes[key] = val

        # 3. Create children
        # self._nodes = result

    def add_child(self, ident, obj):
        "Add a child node"

        # TODO: Check it's always a NodeVal obj !!!
        self._nodes[ident] = obj


# NodeMap
# =====================================


class NodeMap(NodeDict):
    "A nodeDict accessible via its attributes"

    def add_child(self, ident, obj):
        "Add a child node"

        # pylint: disable=super-with-arguments
        super(NodeMap, self).add_child(ident, obj)
        setattr(self, ident, obj)

    def __getattr__(self, key):

        if key in self._nodes:
            # print (f"Get value: {key} for {id(self)} from _nodes")
            return self._nodes[key]

        if key in self._node_conf_parsed:
            # print (f"Get value: {key} for {id(self)} from _conf_parsed")
            return self._node_conf_parsed[key]

        # Todo: Implement nice warning for dropped childrens !!!
        # if self.conf_children:
        #     matches = [ remap.attr for remap in self.conf_children if remap.attr]
        #     self.conf_children
        #     print ("NodeDict Struct2")
        #     return self._node_conf_build_future(payload)

        raise AttributeError(f"Missing attribute: {key} in {self}")

    def __setattr__(self, key, value):

        if key in self._nodes:
            # Set attribute if in _nodes
            # print (f"Set node value: {key}={value} for {self}")
            self._nodes[key] = value
            # self.__dict__[key] = value
        elif key in self._node_conf_parsed:
            # print (f"Set conf value: {key}={value} for {self}")
            self._node_conf_parsed[key] = value
        else:
            # or just set regular attribute
            # print (f"Set attr value: {key}={value} for {self}")
            # pylint: disable=super-with-arguments
            super(NodeMap, self).__setattr__(key, value)


# NodeMap
# =====================================


def expand_envar_syntax(payload, cls):
    "Expand serialized dict/list from env syntax"

    if not cls:
        return payload
    if isinstance(payload, cls):
        return payload
    if not isinstance(payload, str):
        return payload

    result = payload
    if cls == dict:
        result = {}
        for statement in payload.split(","):

            keyval = statement.split("=", 1)
            if len(keyval) != 2:
                raise InvalidSyntax(
                    f"Invalid syntax, expected 'key=value', got: {statement}"
                )
            key = keyval[0]
            value = keyval[1]
            result[key] = value

    if cls == list:
        result = []
        for statement in payload.split(","):
            result.append(statement)

    return result


class NodeMapEnv(NodeMap):
    "Like a NodeMap, but fetch value from env"

    conf_env_prefix = None

    def _node_conf_defaults(self, payload):
        """Override payload from environment vars"""

        # pylint: disable=super-with-arguments
        result = super(NodeMapEnv, self)._node_conf_defaults(payload)
        conf_struct = self._node_conf_struct

        # Override from environment
        for key, val in result.items():
            value = self.get_env_conf(key) or val

            cls = [item.cls for item in conf_struct if item.key == key]
            if len(cls) > 0:
                value = expand_envar_syntax(value, cls[0])

            result[key] = value

        return result

    def get_env_conf(self, key=None):
        "Return the value of environment var associated to this object"
        # name = f"{self.module}_{self.kind}_{self.ident}"
        # name = f"{self.kind}_{self.ident}"
        name = f"{self.conf_env_prefix or self.kind}"

        if key:
            name += f"_{key}"
        name = name.upper()
        result = os.getenv(name)

        if result:
            self.log.info(f"Fetch value from env: {name}={result}")
        else:
            self.log.debug(f"Skip value from env: {name}")

        return result


# Test decorators
# =====================================


def makemap(cls):
    "Test decorator to create NodeMap classes"

    class Class(cls, NodeMap):
        "Generated class"
        pass

    return Class


# Test Class Data
# =====================================


class NodeAuto:
    """
    Autoconfiguration Configuration

    This class will autodetermine what kind of object and apply magically
    the associated classe upon is source object type.
    """

    def __init__(self, *args, ident=None, payload=None, autoconf=-1, **kwargs):

        # Map json object to Node class
        self.__class__ = map_node_class(payload)

        # Forward to class
        self.__init__(*args, ident=ident, payload=payload, autoconf=autoconf, **kwargs)
