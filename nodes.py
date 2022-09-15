

import copy
import inspect
import textwrap


from cafram.base import Base
from cafram.utils import serialize, flatten, json_validate

from pprint import pprint, pformat

# Types
# =====================================

# class unset:
#     "Represent an unset attribute"

#     def __repr__(self):
#         return "UNSET"


# class drop:
#     "Represent an dropped attribute"

#     def __repr__(self):
#         return "DROP"

class _unset(object):
    "Represent an unset attribute"

    def __repr__(self):
        return '<cafram.unset>'

    def __reduce__(self):
        return 'unset'  # when unpickled, refers to "unset" below (singleton)


unset = _unset()


class _drop(object):
    """Represents a value that will be dropped from the schema if it
    is missing during *serialization* or *deserialization*.  Passed as
    a value to the `missing` or `default` keyword argument
    of :class:`SchemaNode`.
    """

    def __repr__(self):
        return '<cafram.drop>'

    def __reduce__(self):
        return 'drop'  # when unpickled, refers to "drop" below (singleton)


drop = _drop()



# Functions
# =====================================

def map_node_class(payload):
    "Map list or dict to cafram classes, otherwise keep value as is"

    # if payload is None:
    #     return NodeVal
    if isinstance(payload, dict):
        return NodeMap
        #return NodeDict
    elif isinstance(payload, list):
        return NodeList
    else:
        return type(payload)


def map_all_class(payload):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        return NodeMap
        return NodeDict
    elif isinstance(payload, list):
        return NodeList
    else:
        return NodeVal




















# Simple attributes class
# =====================================

class NodeVal(Base):
    """
    Base configuration class

    * conf_default: Holds the default configuration.
    if it's a dict, it will be merged with acutal user config, otherwise

    * conf_struct: If a value si present in payload, an instance will be created with
    default data, unless the key is not present (in case of dicts)
    """

    _nodes = None
    _node_root = None

    # Class parameters
    conf_default = None
    conf_schema = None
    # conf_struct = None
    conf_ident = None

    _node_conf_current = None
    _node_conf_parsed = None

    _node_autoconf = 0

    # Beta: _node_children
    _node_children = None

    def __init__(self, *args, parent=None, payload=None, autoconf=None, **kwargs):


        # Call parents
        super(NodeVal, self).__init__(*args, **kwargs)

        self.log.debug(f"__init__: NodeVal/{self}")

        # Register structure
        self._nodes = copy.deepcopy(self._nodes)

        # Register parent
        self._node_parent = parent or self
        self._node_root = getattr(parent, "_node_root", None) or self

        # Manage autoconf levels
        if autoconf is None:
            autoconf = getattr(self._node_parent, "_node_autoconf", 0)
        self._node_autoconf = (autoconf - 1) if autoconf > 0 else autoconf

        # self.runtime = NodeMap(payload=runtime or {})
        self._node_conf_current = None
        self._node_conf_parsed = None
        self._node_conf_current = None

        # Auto init object
        self.deserialize(payload)



    # Serialization
    # -----------------

    def deserialize(self, payload):
        "Transform json to object"

        self._node_conf_current = {}
        self._node_conf_raw = payload
        conf = self._node_conf_parse(payload)
        self._node_conf_parsed = conf

        self._node_conf_build(conf)

        try:
            self.node_hook_post()
        except Exception as err:
            self.dump()
            raise err

        if self.conf_ident:
            self.ident = self.conf_ident.format(**locals())

    def serialize(self, mode="parsed"):
        "Transform object to json"

        if mode == "raw":
            return self._node_conf_raw
        elif mode == "current":
            return self._node_conf_current
        elif mode == "parsed":
            return self._node_conf_parsed
        # else:
        #     raise NotImplemented("Unknown mode '{mode}' for serialize()")

    # User hooks
    # -----------------

    def node_hook_pre(self, payload):
        "Placeholder to transform config"
        return payload

    def node_hook_post(self):
        "Placeholder to transform object once onfig has been done"
        pass

    # Configuration parser
    # -----------------

    def _node_conf_parse(self, payload, mode="input"):
        "Transform json to valid json config"

        # Parse config
        payload1 = self._node_conf_defaults(payload)
        payload2 = self._node_conf_validate(payload1)
        payload3 = self.node_hook_pre(payload2)

        if payload1 != payload3:
            self.log.debug(
                f"Payload transformation for: {self}\nFrom: {payload1}\nTo: {payload3}"
            )
            # print (f"Payload transformation for: {self}\nFrom: {payload1}\nTo: {payload3}")

        return payload3

    def _node_conf_defaults(self, payload):

        if payload:
            # Skip if payload is provided
            return payload

        default = None

        # Check if defaults are presents in conf_schema
        if isinstance(self.conf_schema, dict):
            if "default" in self.conf_schema:
                default = copy.deepcopy(self.conf_schema["default"])

        # Check if defaults are presents in conf_default
        else:
            if isinstance(self.conf_default, dict):
                default = copy.deepcopy(self.conf_default)

        return default

    def _node_conf_validate(self, payload):
        """Validate config against schema

        This function will only works if:
        * self.conf_schema is not None
        * self.conf_schema conatins the "$schema" key
        """

        old_payload = payload

        if self.conf_schema and "$schema" in self.conf_schema:

            try:
                # print (f"Validate config of: {self} WITHY PAYLOAD: {payload}")
                payload = json_validate(self.conf_schema, payload)
            except jsonschema.exceptions.ValidationError as err:

                print("")
                print(f"Error: {err.message} for {self.__dict__}")
                print(f"Value: {err.instance}")
                print(f"Payload: {payload}")
                print("Schema:")
                # print (serialize(self.conf_schema, fmt='yml'))
                print(traceback.format_exc())
                sys.exit(1)

            except jsonschema.exceptions.SchemaError as err:
                print("Bug in schema for ", self)
                print(err)

                print("PAYLOAD")
                pprint(payload)
                print("SCHEMA")
                pprint(self.conf_schema)
                print("BBBUUUUUGGGGGGG on schema !!!")
                print(traceback.format_exc())
                sys.exit(1)

            if old_payload != payload:
                print("OLD CONFIG WITHOUT DEFAULTS", old_payload)
                print("NEW CONFIG WITH DEFAULTS", payload)

        return payload

    # Simple Class implementation
    # -----------------
    def _node_conf_build(self, payload):
        "Just assign the value, thats all"
        self._nodes = payload

    # Misc
    # -----------------

    def from_json(self, payload):
        # payload = json.loads(payload)
        # payload = jsonschema.validate(payload)

        payload = json.loads(payload)
        return self._node_conf_parse(payload)



    # Node management
    # -----------------

    # Methods:
    # value:
    #   - return both node objects and other
    #   - Support recursivity
    # get_nodes
    #   - return only node objects
    #   - support recur
    # get_value
    #   - return ALL but node objects


    def value(self):
        return self._nodes


    def get_children(self, lvl=0, explain=False, leaves=False):
        result = None
        if leaves:
            result = self
        if explain:
            return {
                "obj": self,
                "value": self.get_value(),
                f"subtype (auto:{self._node_autoconf})": self._node_children,
                "children": result,
            }
        return result

    def get_value(self, lvl=0, explain=False):

        return self._nodes




    # def get_children_conf(self, explain=False):
    #     print("get_children_conf is DEPRECATED, use get_config instead")
    #     self.get_config(explain=explain)

    # def get_nodes(self, explain=False):

    #     if explain:
    #         return self.get_config()

    #     return None

    # def get_config(self, explain=False):

    #     children = self._nodes

    #     if isinstance(children, NodeVal):
    #         children = children.get_config(explain=explain)
    #     else:
    #         children = self._nodes

    #     if explain:
    #         children = f"{children}"

    #     return children



    def is_root(self):
        if self._node_parent and self._node_parent == self:
            return True
        return False


    def get_parent(self):
        return self._node_parent or None

    def get_parent_root(self):
        return self._node_root


    def get_parents(self):
        "Return all parent of the object"

        parents = []
        current = self
        parent = self._node_parent or None
        while parent is not None and parent != current:
            if not parent in parents:
                parents.append(parent)
                current = parent
                parent = getattr(current, "_node_parent")

        return parents


    # Dumper
    # -----------------
    def dump(self, explain=True, all=False, **kwargs):

        super(NodeVal, self).dump(**kwargs)

        _node_conf_parsed = self._node_conf_parsed
        _node_conf_current = self._node_conf_current

        if all and _node_conf_parsed is not None:
            msg = "(same as Raw Config)"
            if _node_conf_current != _node_conf_parsed:
                msg = "(different from Raw Config)"

                print("  Raw Config:")
                print("  -----------------")
                out = serialize(_node_conf_current, fmt="yaml")
                print(textwrap.indent(out, "    "))

            print("  Parsed Config:", msg)
            print("  -----------------")
            out = serialize(_node_conf_parsed, fmt="yaml")
            print(textwrap.indent(out, "    "))

        if all:
            print("  Children:")
            print("  -----------------")
            children = self.get_children(lvl=-1, explain=False, leaves=True)
            out = serialize(children)
            #out = pformat(children, indent=2, width=5)
            print(textwrap.indent(out, "    "))

        print("  Config:")
        print("  -----------------")
        children = self.get_value(explain=explain)
        out = serialize(children, fmt="yaml")
        print(textwrap.indent(out, "    "))

        # out = pformat(children)
        # print (textwrap.indent(out, '    '))

        print("\n")


# Legacy Support
#Conf = NodeVal















# Test Class Data
# =====================================



class NodeListIterator:
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

    _nodes = []

    # Internal methods

    def _node_conf_defaults(self, payload):
        result = super(NodeList, self)._node_conf_defaults(payload)
        if not result:
            result = []
        return result

    def _node_conf_build(self, payload):
        "Just assign the value, thats all NodeList"

        if not payload:
            return []

        cls = self._node_children

        result = []
        count = 0
        for item in payload:

            # TOFIX: ident = item_def.ident
            ident = f"Item{count}"

            if self._node_autoconf != 0:
                cls = cls or map_all_class(item)

            if cls:
                assert inspect.isclass(cls), "conf_struct must be a class"

                # ident = f"{cls.__name__}_{count}"
                ident = f"{self.ident}_{count}"

                if issubclass(cls, NodeVal):
                    item = cls(parent=self, ident=ident, payload=item)
                elif cls:
                    item = cls(item)

            result.append(item)
            count = +1

        self._nodes = result



    def __iter__(self):
        return NodeListIterator(self)

    # def items(self):
    #     return self._nodes


    def get_children(self, lvl=0, explain=False, leaves=False):
        "Return NodeList childs"
        result = []
        for child in self._nodes:
            if isinstance(child, NodeVal):
                if lvl != 0:
                    value = child.get_children(lvl=lvl-1, explain=explain, leaves=leaves)
                else:
                    value = child

                if leaves:
                    value = value or child

                result.append(value)
                
        
        # if explain:
        #     cls = self._node_children or "*"
        #     return {
        #         f"<{self}/{cls}>": result
        #     }

        if explain:
            return {
                "obj": self,
                "value": self.get_value(),
                f"subtype (auto:{self._node_autoconf})": self._node_children,
                "children": result,
            }

        return result


    def get_value(self, lvl=0, explain=False):
        "Return NodeList value"
        result = []
        for child in self._nodes:
            if not isinstance(child, NodeVal):
                result.append(child)
            else:
                if lvl != 0:
                    result.append(child.get_value(lvl=lvl-1, explain=explain))
        
        return result



    # def get_config(self, explain=False):

    #     result = []
    #     children = self._nodes or []

    #     if not isinstance(children, list):
    #         self.log.warning(
    #             "Developper must call node_hook_pre() first if data are not list"
    #         )
    #         raise ListExpected(
    #             f"A list was expected for {self}, got {type(children).__name__}: {children}"
    #         )

    #     for child in children:
    #         if hasattr(child, "get_config"):
    #             children = child.get_config(explain=explain)
    #         else:

    #             children = child
    #         result.append(children)

    #     return result

        # if explain:
        #     return {
        #         f"<{self}>": result
        #         # "obj": str(self),
        #         # "children": result,
        #     }
        # else:
        #     return result



    # def get_nodes(self, explain=False):
    #     """For NodeList"""

    #     result = []
    #     # if explain:
    #     #     result = {}

    #     for value in self._nodes:

    #         if isinstance(value, NodeVal):
    #             children = value.get_nodes(explain=explain)
    #             print ("APPEND", children)
    #             result.append(children)

    #     # cls = getattr(self, "_node_children", None)

    #     # if explain:
    #     #     result = {
    #     #         f"Items: ({cls.__name__}:)": result,
    #     #         }

    #     if explain:
    #         return result or self.get_config()
    #     return result #or self.get_config()

















# Test Class Data
# =====================================



class NodeDictItem:
    def __init__(self, *args, key=None, cls=None, default=None, attr=None, **kwargs):

        self.key = key
        self.attr = attr or None
        self._ident = None

        self.cls = cls or None
        self.default = default or None

    @property
    def ident(self) -> str:
        return self.attr or self.key

    def __repr__(self):
        result = [f"{key}={val}" for key, val in self.__dict__.items() if val]
        result = ",".join(result)
        return f"Remap:{result}"


class NodeDict(NodeVal):

    _nodes = {}

    _node_children = None

    def __init__(self, *args, **kwargs):

        if isinstance(self._node_children, list):
            self._node_children = [NodeDictItem(**conf) for conf in self._node_children]

        super(NodeDict, self).__init__(*args, **kwargs)

    # # TODO: https://www.pythonlikeyoumeanit.com/Module4_OOP/Special_Methods.html
    # __len__
    # __getitem__(self, key)
    # __setitem__(self, key, item)
    # __contains__(self, item)
    # __iter__(self)
    # __next__(self)



    def get_children(self, lvl=0, explain=False, leaves=False):
        "Return NodeDict childs"
        result = {}
        for name, child in self._nodes.items():
            if isinstance(child, NodeVal):
                if lvl != 0:
                    value = child.get_children(lvl=lvl-1, explain=explain, leaves=leaves)
                else:
                    value = child

                if leaves:
                    value = value or child

                result[name] = value
        
        if explain:
            return {
                "obj": self,
                f"subtype (auto:{self._node_autoconf})": self._node_children,
                "value": self.get_value(),
                "children": result,
            }
        return result

    def get_value(self, lvl=0, explain=False):
        "Return NodeDict value"
        result = {}
        for name, child in self._nodes.items():
            if not isinstance(child, NodeVal):
                result[name] = child
            else:
                if lvl != 0:
                    result[name] = child.get_value(lvl=lvl-1)
        
        return result






    def _node_conf_build(self, payload):
        "For NodeDict"

        result = {}
        payload = payload or {}

        if not isinstance(payload, dict):
            # self._nodes = payload
            # return
            self.log.warning(
                "Developper must call node_hook_pre() first if data are not dict"
            )
            raise DictExpected(
                f"A dictionnary was expected for {self}, got {type(payload).__name__}: {payload}"
            )

        # Check the mapping structure
        conf_struct = self._node_children

        # print ("BUILD DIIIICCCTTTT")
        # pprint (self.__dict__)

        # Direct generrate
        if inspect.isclass(conf_struct):
            # print ("Create autofilter for class:", conf_struct)
            conf_struct = [
                {"key": key, "default": val, "cls": conf_struct}
                for key, val in payload.items()
            ]
            conf_struct = [NodeDictItem(**conf) for conf in conf_struct]

        # Auto guess from payload
        elif conf_struct == {}:
            conf_struct = [
                {"key": key, "default": val, "cls": type(val)}
                for key, val in payload.items()
            ]
            conf_struct = [NodeDictItem(**conf) for conf in conf_struct]

        # Leave as is
        elif isinstance(conf_struct, list):
            pass

        # Auto generate
        elif self._node_autoconf != 0:
            # print (f"Auto generate attr: {self}")
            conf_struct = [
                {"key": key, "default": val, "cls": map_node_class(val)}
                for key, val in payload.items()
            ]
            conf_struct = [NodeDictItem(**conf) for conf in conf_struct]

        # Simply forward dict
        elif conf_struct is None or conf_struct == []:
            self._nodes = payload
            return

        if not isinstance(conf_struct, list):
            raise ListExpected(
                f"A list was expected for conf_struct, got : {conf_struct}"
            )

        # print ("Filters: ", conf_struct)

        # Process each children
        for item_def in conf_struct:

            key = item_def.key
            attr = item_def.attr or key
            cls = item_def.cls

            # assert isinstance(attr, str), f"Attribute is not string, got: {attr}"
            # assert isinstance(key, str), f"Key is not string, got: {attr}"

            # Check value
            if item_def.ident is None:
                # print (f"    > Skip item: nokey/noattr {item_def.ident}=unset")
                continue
            elif key:
                value = copy.deepcopy(payload.get(key, item_def.default))
                # print (f"  > Process item: {item_def}:{key} with value={value}")
            else:
                value = copy.deepcopy(item_def.default)
                # print (f"  > Process internal item: {item_def}:{attr} with value={value}")

            # Create children
            if value == drop or item_def.default == drop:
                # print (f"    > Skip dropped nested item: {attr}={cls}({value})")
                continue
            elif value == unset:
                value = None
                # print (f"    > Instanciate unset key item object: {attr}={value}")
            else:

                if cls:
                    if issubclass(cls, NodeVal):
                        #print (f"    > Instanciate Node object: {attr}={cls}(payload={value})")
                        value = cls(parent=self, ident=item_def.ident, payload=value)
                    else:
                        if not value:
                            # print (f"    > Instanciate null child object: {attr}={cls}()")
                            value = cls()
                        elif isinstance(value, cls):
                            # print (f"    > Instanciate child object: {attr}={cls}({value})")
                            value = cls(value)
                        else:
                            # print (f"    > Instanciate empty child object: {attr}={cls}()")
                            try:
                                value = cls(value)
                            except Exception as err:
                                self.log.critical(
                                    f"Type mismatch between: {cls} and {value}"
                                )
                                raise NotExpectedType(err)
                else:
                    # print (f"    > Instanciate direct assignment: {attr}={value}")
                    value = value

            result[attr] = value

        # Happend other keys
        done_keys = [remap.key for remap in conf_struct if remap.ident]
        for key, val in payload.items():
            if key not in done_keys:
                result[key] = val

        # Create children
        assert isinstance(result, dict)
        self._nodes = result

    def add_child(self, ident, obj):
        self._nodes[ident] = obj

    def _node_conf_defaults(self, payload):
        "For NodeDict"

        # TEMP
        return payload

        # TOFIX: To be reenabled
        result = super(NodeDict, self)._node_conf_defaults(payload)
        if not result:
            result = {}

        # Overrides dict defaults
        if isinstance(payload, dict):
            result.update(payload)

        return result




    # def get_nodes(self, explain=False):
    #     "For NodeDict"
    #     result = {}
    #     for name, value in self._nodes.items():

    #         if isinstance(value, NodeVal):

    #             if explain:
    #                 item_cls = getattr(value, "_node_children", None)
    #                 if item_cls and inspect.isclass(item_cls):
    #                     item_cls = "/" + item_cls.__name__
    #                 elif item_cls:
    #                     item_cls = "/*"
    #                 else:
    #                     item_cls = ""
    #                 name = f"{name} ({value}{item_cls})"

    #             result[name] = value.get_nodes(explain=explain)

    #     if explain:
    #         return result or self.get_config()
    #     else:
    #         return result

    # def get_config(self, explain=False):
    #     "For NodeDict"

    #     result = {}
    #     children = self._nodes

    #     # if not isinstance(children, dict):
    #     #     return children

    #     for key, child in children.items():

    #         if isinstance(child, NodeVal):
    #             children = child.get_config(explain=explain)
    #             if explain:
    #                 key = f"{key} ({child})"
    #         else:

    #             children = child

    #         result[key] = children

    #     return result
    #     # if explain:
    #     #     #return str(self), result
    #     #     return {
    #     #         f"{self} <NodeDict>": result
    #     #         #"children|": result,
    #     #     }
    #     # else:
    #     #     return result

    # def items(self):
    #     return self._nodes.items()























class NodeMap(NodeDict):
    def add_child(self, ident, obj):
        super(NodeMap, self).add_child(ident, obj)
        setattr(self, ident, obj)

    def __getattr__(self, key):

        if key in self._nodes:
            # print (f"Get value: {key} for {id(self)}")
            return self._nodes[key]

        # Todo: Implement nice warning for dropped cghildrens !!!
        # if self._node_children:
        #     matches = [ remap.attr for remap in self._node_children if remap.attr]
        #     self._node_children
        #     print ("NodeDict Struct2")
        #     return self._node_conf_build_future(payload)

        raise AttributeError(f"Missing attribute: {key} in {self}")

    def __setattr__(self, key, value):

        if key in self._nodes:
            # Set attribute if in _nodes
            # print (f"Set node value: {key}={value} for {self}")
            self._nodes[key] = value
            self.__dict__[key] = value
        else:
            # or just set regular attribute
            # print (f"Set attr value: {key}={value} for {self}")
            super(NodeMap, self).__setattr__(key, value)


    # def _node_conf_build(self, payload):
    #     "Just assign the value, thats all"

    #     super(NodeMap, self)._node_conf_build(payload)

    # for key, val in self._nodes.items():
    #     self.__dict__[key] = val

    # def _node_conf_build_V1(self, payload):
    #     "Just assign the value, thats all"

    #     super(NodeMap, self)._node_conf_build(payload)

    #     for attr, item in self._nodes.items():
    #         print (f"  > Set obj atribute '{self}': {attr}={item}")
    #         setattr(self, attr, item)

    #     #return value

    # def _node_conf_build_V2_broken(self, payload):
    #     "Just assign the value, thats all"

    #     super(NodeMap, self)._node_conf_build(payload)

    #     for attr, item in self._nodes.items():
    #         print (f"  > Set obj atribute '{self}': {attr}={item}  ----------")

    #         def getx(self):
    #             return self._nodes[attr]

    #         def setx(self, value):
    #             self._nodes[attr] = value

    #         def delx(self):
    #             del self._nodes[attr]

    #         x = property(getx, setx, delx, "Link to config")
    #         setattr(self, attr, x)

    # def __setattr__(self, key, value):
    #     print (f"Set value: {key}={value} for {id(self)}")
    #     pprint (list(self.__class__.__dict__.keys()))
    #     self._nodes[key] = value

    # def _node_conf_build(self, payload):
    #     "Just assign the value, thats all"

    #     super(NodeMap, self)._node_conf_build(payload)

    #     for attr, item in self._nodes.items():
    #         print (f"  > Set obj atribute '{self}': {attr}={item}  ----------")

    #         def getx(self):
    #             return self._nodes[attr]

    #         def setx(self, value):
    #             self._nodes[attr] = value

    #         def delx(self):
    #             del self._nodes[attr]

    #         x = property(getx, setx, delx, "Link to config")
    #         setattr(self, attr, x)





# Test decorators
# =====================================


def makemap(cls):
    class Class(cls, NodeMap):
        pass

    return Class









# Test Class Data
# =====================================

class NodeAuto():
    """
    Autoconfiguration Configuration

    This class will autodetermine what kind of object and apply magically
    the associated classe upon is source object type.
    """

    def __init__(self, *args, ident=None, payload=None, autoconf=-1, **kwargs):

        

        self.__class__ = map_all_class(payload)
        #print ("Found class", self.__class__, payload)
        # # classes = "-> ".join([x.__name__ for x in self.__class__.__mro__])
        # # print(f"    MRO: {classes}")
        # print ("INIT AUTO", args, ident, payload, autoconf, kwargs)

        self.__init__(*args, ident=ident, payload=payload, autoconf=autoconf, **kwargs)

        # super(self.__class__, self).__init__(
        #     *args, ident=ident, payload=payload, autoconf=autoconf, **kwargs
        # )


        # super(self.__class__, self).__init__(
        #     *args, ident=ident, payload=payload, autoconf=autoconf, **kwargs
        # )


#def confauto()