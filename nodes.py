# Pshiiit' Knackie ! Library

import sys
import logging
import json
import io
import textwrap
import inspect
import copy


from pprint import pprint, pformat
import traceback

from cafram.utils import serialize, flatten, json_validate
import jsonschema

log = logging.getLogger(__name__)


# See: https://stackoverflow.com/questions/328851/printing-all-instances-of-a-class



# =====================================================================
# Exceptions
# =====================================================================



class CaframException(Exception):
    """Generic cafram exception"""


class DictExpected(CaframException):
    """Raised a dict was expected"""

class ListExpected(CaframException):
    """Raised a list was expected"""

class MissingIdent(CaframException):
    """Raised ident is not set"""

class NotImplemented(CaframException):
    """Raised when missing features"""

class NotExpectedType(CaframException):
    """Raised when types mismatchs"""


# =====================================================================
# Class helpers
# =====================================================================


class Base():

    # Public attributes
    # ---------------------

    # Current library name
    _app = "cafram"

    # Objects can have names
    ident = None

    # Object kind, nice name to replace raw class name, should be a string
    kind = None

    # Define live runtime data
    # To be renamed: shared
    #runtime = {}

    # Optional attributes
    # ---------------------

    # Object shortcut to logger
    log = log

    def __init__(self, *args, **kwargs):
        self.log.debug(f"__init__: Base/{self} => {[ x.__name__ for x in  self.__class__.__mro__]}")

        #print ("INIT Base", self)

        #print ("init base")
        self.kind = kwargs.get("kind") or self.kind or self.__class__.__name__
        
        # Ident management
        if "ident" in kwargs:
            self.ident = kwargs.get("ident")
        if self.ident is None:
            raise MissingIdent(f"Missing 'ident' for __init__: {self}")

        self.ident = self.ident or kwargs.get("ident") or self.ident or self.kind
        
        self.log = kwargs.get("log") or self.log
        #print ("Update in INIT BASE", self.ident, id(self))
        
        self.shared = kwargs.get("shared") or {}
        # if "runtime" in kwargs:
        #     self.runtime = kwargs.get("runtime") or {}


        #print ("OVER Base")
        


    def __str__(self):
        return f"{self.__class__.__name__}:{self.ident}"

    def __repr__(self):
        #return self._nodes
        return f"{self.__class__.__name__}.{id(self)} {self.ident}"
        return f"Instance {id(self)}: {self.__class__.__name__}:{self.ident}"

    def dump2(self, format='json', filter=None, **kwargs):

        print ("\n===================================================================")
        print (f"== Dump of {self._app}.{self.kind}.{self.ident} {id(self)}")
        print ("===================================================================\n")

        print ("  Infos:")
        print (f"    ID: {id(self)}")
        print (f"    Kind: {self.kind}")
        print (f"    Ident: {self.ident}")
        print (f"    Repr: {self.__repr__()}")
        print (f"    String: {self.__str__()}")
        classes = '-> '.join([x.__name__ for x in self.__class__.__mro__])
        print (f"    MRO: {classes}")
        

        # cls = self.__class__.__bases__
        # cls = inspect.getmro(self.__class__)
        # data = serialize(cls, fmt="yaml")
        # print ("  Features:")
        # print (textwrap.indent(data, '    '))

        # print ("  Runtime config:")
        # print (serialize(list(self.runtime.keys())))

        print ("")


# =====================================================================
# Pre Base Class helpers
# =====================================================================


# Logging
# --------------------------

class Log(Base):

    log = log

    def __init__(self, *args, **kwargs):

        self.log.debug(f"__init__: Log/{self}")

        log = kwargs.get("log")
        if log is None:
            log_name = f"{self._app}.{self.kind}.{self.ident}"
        elif isinstance(log, str):
            log_name = f"{self._app}.{log}"
            log = None
        elif log.__class__.__name__ == 'Logger':
            pass
        else:
            raise Exception ("Log not allowed here")

        if not log:
            log = logging.getLogger(log_name)

        self.log = log

        super(Log, self).__init__(*args, **kwargs)



# =====================================================================
# Post Base Class helpers
# =====================================================================


# Family
# --------------------------

class Family(Base):

    root = None
    parent = None
    children = []

    def __init__(self, *args, **kwargs):

        super(Family, self).__init__(*args, **kwargs)

        self.log.debug(f"__init__: Family/{self}")

        # Init family
        #print ("init family")
        parent = kwargs.get("parent") or self.parent
        
        # Register parent
        if parent and parent != self:
            self.parent = parent
            self.root = parent.root
        else:
            self.parent = self
            self.root = self

        # Register children
        self.children = []
        if self.has_parents():
            self.parent.children.append(self)

    def get_children_tree(self):
        
        result = []
        children = self.children or []
        for child in children:
            children = child.get_children_tree()
            result.append({ str(child): children or None })

        return result

    def has_parents(self):
        return True if self.parent and self.parent != self else False

    def get_parent(self):
        return self.parent or None

    def get_parents(self):
        "Return all parent of the object"

        parents = []
        current = self
        parent = self.parent or None
        while parent is not None and parent != current:
            if not parent in parents:
                parents.append(parent)
                current = parent
                parent = getattr(current, "parent")

        return parents

    # def get_parents(self):
    #     "Return all parent of the object"

    #     parents = []
    #     parent = getattr(self, "parent") or None
    #     while parent is not None and parent != self:
    #         #print (parent, "VS", self)
    #         parent = parent.get_parent()
    #         if parent:
    #             #pprint (parent)
    #             parents.append(parent)

    #     return parents

    # def get_parents2(self):
    #     "Return all parent of the object"

    #     parent = self.parent
    #     while parent is not None and parent != self:
    #         return flatten([self, parent.get_parents2()])

    #     return [self]

    def dump2(self, **kwargs):
        super(Family, self).dump2(**kwargs)

        parents = self.get_parents()
        children = self.get_children_tree()

        if parents or children:
            print ("  Family:")
            print ("  -----------------")
            print (f"    Parents/Children: {len(parents)}/{len(children)}")

        if parents:
            print ("    Parents:")
            #print ("    -----------------")
            parents.reverse()
            parents = serialize(parents, fmt='yaml')
            print (textwrap.indent(parents, '      '))

        if children:
            print ("    Children:")
            #print ("    -----------------")
            children = serialize(children, fmt='yaml')
            print (textwrap.indent(children, '      '))

        print ("\n")


# Conf
# --------------------------

class unset:
    "Represent an unset attribute"
    def __repr__(self):
        return unset

class drop:
    "Represent an dropped attribute"
    def __repr__(self):
        return drop



class ConfVal(Base):
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
    #conf_struct = None
    conf_ident = None

    _conf_raw = None
    _conf_parsed = None

    _conf_auto = 0

    # Beta: conf_struct2
    conf_struct2 = None

    def __init__(self, *args, parent=None, payload=None, autoconf=None, **kwargs):

        if hasattr(self, 'conf_struct'):
            pprint (self)
            pprint (dir(self))
            pprint (self.__dict__)
            raise Exception(f"Please migrate '{self}' object to conf_struct2")

        # Call parents
        super(Conf, self).__init__(*args, **kwargs)
        #print ("INIT Conf")

        self.log.debug(f"__init__: Conf/{self}")

        # Register structure
        self._nodes = copy.deepcopy(self._nodes)

        # Register parent
        self._node_parent = parent or self
        self._node_root = getattr(parent, "_node_root", None) or self

        # Manage autoconf levels
        if autoconf is None:
            autoconf = getattr(self._node_parent, "_conf_auto", 0)
        self._conf_auto = (autoconf - 1) if autoconf > 0 else autoconf


        #self.runtime = ConfAttr(payload=runtime or {})
        self._conf_raw = None
        self._conf_parsed = None
        self._conf_current = None

        # Auto init object
        self.deserialize(payload)


    def is_root(self):
        if self._node_parent and self._node_parent == self:
            return True
        return False

    def get_nodes(self, explain=False):
        if explain:
            return self.get_config()
            
        return self

    # def get_children_conf_V1(self):
    #     #print ("OKK DEFAULT", self._nodes)
    #     return self._nodes

    def get_children_conf(self, explain=False):
        print ("get_children_conf is DEPRECATED")
        self.get_config(explain=explain)

    def get_config(self, explain=False):

        children = self._nodes

        if isinstance(children, Conf):
            children = children.get_config(explain=explain)
        else:
            children = self._nodes

        if explain:
            children = f"{children}"
            # children = {
            #         f"({self})": children,
            #         # "obj|||":  str(self),
            #         # "children|||":children,
            #     }

        return children


    def get_parent(self):
        return self._node_parent or None

    def get_parent_root(self):
        return self._node_root
        # OLD WAY return self.get_parents()[-1]
        # Buggy :,( 
        #return self._node_root

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



    # Serialization
    # -----------------

    def deserialize(self, payload):
        "Transform json to object"

        self._conf_current = {}
        self._conf_raw = payload
        conf = self.conf_parse(payload)
        self._conf_parsed = conf

        self.conf_build(conf)

        try:
            self.conf_post_build()
        except Exception as err:
            self.dump2()
            raise err

        if self.conf_ident:
            self.ident = self.conf_ident.format(**locals())


    def serialize(self, mode='parsed'):
        "Transform object to json"

        if mode == 'raw':
            return self._conf_raw
        elif mode == 'current':
            return self._conf_current
        elif mode == 'parsed':
            return self._conf_parsed
        else:
            raise NotImplemented("Unknown mode '{mode}' for serialize()")




    # User hooks
    # -----------------

    def conf_transform(self, payload):
        "Placeholder to transform config"
        return payload

    def conf_post_build(self):
        "Placeholder to transform object once onfig has been done"
        pass


    # Configuration parser
    # -----------------

    def conf_parse(self, payload, mode='input'):
        "Transform json to valid json config"

        # Parse config
        payload1 = self.conf_make_defaults(payload)
        payload2 = self.conf_validate(payload1)
        payload3 = self.conf_transform(payload2)
        
        if payload1 != payload3:
            self.log.debug(f"Payload transformation for: {self}\nFrom: {payload1}\nTo: {payload3}")
            #print (f"Payload transformation for: {self}\nFrom: {payload1}\nTo: {payload3}")

        return payload3

    def conf_make_defaults(self, payload):

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


    def conf_validate(self, payload):
        """Validate config against schema
        
        This function will only works if:
        * self.conf_schema is not None
        * self.conf_schema conatins the "$schema" key
        """

        old_payload = payload

        if self.conf_schema and "$schema" in self.conf_schema:

            try:
                print (f"Validate config of: {self} WITHY PAYLOAD: {payload}")
                payload = json_validate(self.conf_schema, payload)
            except jsonschema.exceptions.ValidationError as err:

                print ("")
                print(f"Error: {err.message} for {self.__dict__}")
                print(f"Value: {err.instance}")
                print (f"Payload: {payload}")
                print ("Schema:")
                #print (serialize(self.conf_schema, fmt='yml'))
                print(traceback.format_exc())
                sys.exit(1)

            except jsonschema.exceptions.SchemaError as err:
                print ("Bug in schema for ", self)
                print (err)

                print ("PAYLOAD")
                pprint (payload)
                print ("SCHEMA")
                pprint (self.conf_schema)
                print ("BBBUUUUUGGGGGGG on schema !!!")
                print(traceback.format_exc())
                sys.exit(1)

            if old_payload != payload:
                print ("OLD CONFIG WITHOUT DEFAULTS", old_payload)
                print ("NEW CONFIG WITH DEFAULTS", payload)

        return payload


    # Simple Class implementation
    # -----------------
    def conf_build(self, payload):
        "Just assign the value, thats all"
        self._nodes = payload


    # Misc
    # -----------------

    def from_json(self, payload):
        #payload = json.loads(payload)
        #payload = jsonschema.validate(payload)

        payload = json.loads(payload)
        return self.conf_parse(payload)

    def items(self):
        return self._nodes

    @property
    def value(self):
        return self._nodes

    # Dumper
    # -----------------
    def dump2(self, explain=True, all=False, **kwargs):

        super(Conf, self).dump2(**kwargs)

        _conf_parsed = self._conf_parsed
        _conf_raw = self._conf_raw

        if all and _conf_parsed is not None:
            msg = '(same as Raw Config)'
            if _conf_raw != _conf_parsed:
                msg = '(different from Raw Config)'

                print ("  Raw Config:")
                print ("  -----------------")
                out = serialize(_conf_raw, fmt='yaml')
                print (textwrap.indent(out, '    '))

            
            print ("  Parsed Config:", msg)
            print ("  -----------------")
            out = serialize(_conf_parsed, fmt='yaml')
            print (textwrap.indent(out, '    '))


        if all:
            print ("  Children:")
            print ("  -----------------")
            children = self.get_nodes(explain=False)
            out = pformat(children, indent=2, width=5)
            print (textwrap.indent(out, '    '))

        print ("  Config:")
        print ("  -----------------")
        children = self.get_config(explain=explain)
        out = serialize(children, fmt='yaml')
        print (textwrap.indent(out, '    '))

        # out = pformat(children)
        # print (textwrap.indent(out, '    '))

        print ("\n")
        

# Legacy Support
Conf = ConfVal

class ConfListIterator:
    
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


class ConfList(ConfVal):

    _nodes = []

    def conf_make_defaults(self, payload):
        result = super(ConfList, self).conf_make_defaults(payload)
        if not result:
            result = []
        return result

    def __iter__(self):
        return ConfListIterator(self)


    def items(self):
        return self._nodes

    def get_config(self, explain=False):
        
        result = []
        children = self._nodes or []

        if not isinstance(children, list):
            self.log.warning("Developper must call conf_transform() first if data are not list")
            raise ListExpected(f"A list was expected for {self}, got {type(children).__name__}: {children}")

        for child in children:
            if hasattr(child, 'get_config'):
                children = child.get_config(explain=explain)
            else:
                
                children = child
            result.append(children)

        return result

        # if explain:
        #     return {
        #         f"<{self}>": result
        #         # "obj": str(self),
        #         # "children": result,
        #     }
        # else:
        #     return result


    def conf_build(self, payload):
        "Just assign the value, thats all ConfList"

        if not payload:
            return []

        cls = self.conf_struct2

        
        result = []
        count = 0
        for item in payload:

            # TOFIX: ident = item_def.ident
            ident = f"Item{count}"

            if self._conf_auto != 0:
                cls = cls or map_node_class(item)
            
            if cls:
                assert inspect.isclass(cls), "conf_struct must be a class"

                #ident = f"{cls.__name__}_{count}"
                ident = f"{self.ident}_{count}"

                if issubclass(cls, Conf):
                    #print (f" Instanciate list item object: {cls} with {item}, payload: {payload}")
                    item = cls(parent=self, ident=ident, payload=item)
                elif cls:
                    item = cls(item)

            result.append(item)
            count =+ 1

        self._nodes =  result

    def get_nodes(self, explain=False):
        """For ConfList
        
        """
        
        result = []
        # if explain:
        #     result = {}
        
        for value in self._nodes:
            if isinstance(value, Conf):
                children = value.get_nodes(explain=explain)
                result.append(children)


        # cls = getattr(self, "conf_struct2", None)

        # if explain:
        #     result = {
        #         f"Items: ({cls.__name__}:)": result,
        #         }

        return result or self.get_config()

class ConfDictItem():

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
        result = [ f"{key}={val}" for key, val in self.__dict__.items() if val ]
        result = ','.join(result)
        return f"Remap:{result}"




class ConfDict(ConfVal):

    _nodes = {}

    conf_struct2 = None

    def __init__(self, *args, **kwargs):

        if isinstance(self.conf_struct2, list):
            self.conf_struct2 = [ConfDictItem(**conf) for conf in self.conf_struct2]

        super(ConfDict, self).__init__(*args, **kwargs)

    # # TODO: https://www.pythonlikeyoumeanit.com/Module4_OOP/Special_Methods.html
    # __len__
    # __getitem__(self, key)
    # __setitem__(self, key, item)
    # __contains__(self, item)
    # __iter__(self)
    # __next__(self)

    def conf_build(self, payload):
        "For ConfDict"

        result = {}
        payload = payload or {}

        if not isinstance(payload, dict):
            #self._nodes = payload
            #return 
            self.log.warning("Developper must call conf_transform() first if data are not dict")
            raise DictExpected(f"A dictionnary was expected for {self}, got {type(payload).__name__}: {payload}")

        # Check the mapping structure
        conf_struct = self.conf_struct2
        
        # Direct generrate
        if inspect.isclass(conf_struct):
            #print ("Create autofilter for class:", conf_struct)
            conf_struct = [ {"key": key, "default": val, "cls": conf_struct} for key, val in payload.items() ]
            conf_struct = [ConfDictItem(**conf) for conf in conf_struct]
        
        # Auto guess from payload
        elif conf_struct == {}:
            conf_struct = [ {"key": key, "default": val, "cls": type(val)} for key, val in payload.items() ]
            conf_struct = [ConfDictItem(**conf) for conf in conf_struct]
        
        # Leave as is
        elif isinstance(conf_struct, list):
            pass

        # Auto generate
        elif self._conf_auto != 0:
            #print (f"Auto generate attr: {self}")
            conf_struct = [ {"key": key, "default": val, "cls": map_node_class(val)} for key, val in payload.items() ]
            conf_struct = [ConfDictItem(**conf) for conf in conf_struct]

        # Simply forward dict
        elif conf_struct is None or conf_struct == []:
            self._nodes = payload
            return

                
        
        if not isinstance(conf_struct, list):
            raise ListExpected(f"A list was expected for conf_struct, got : {conf_struct}")

        #print ("Filters: ", conf_struct)

        # Process each children
        for item_def in conf_struct:
            
            key = item_def.key
            attr = item_def.attr or key
            cls = item_def.cls

            # assert isinstance(attr, str), f"Attribute is not string, got: {attr}"
            # assert isinstance(key, str), f"Key is not string, got: {attr}"

            # Check value
            if item_def.ident is None:
                #print (f"    > Skip item: nokey/noattr {item_def.ident}=unset")
                continue
            elif key:
                value = copy.deepcopy(payload.get(key, item_def.default))
                #print (f"  > Process item: {item_def}:{key} with value={value}")
            else:
                value = copy.deepcopy(item_def.default)
                #print (f"  > Process internal item: {item_def}:{attr} with value={value}")

            # Create children
            if value == drop or item_def.default == drop:
                #print (f"    > Skip dropped nested item: {attr}={cls}({value})")
                continue            
            elif value == unset:
                value = None
                #print (f"    > Instanciate unset key item object: {attr}={value}")
            else:

                if cls:
                    if issubclass(cls, Conf):
                        #print (f"    > Instanciate Node object: {attr}={cls}(payload={value})")
                        value = cls(parent=self, ident=item_def.ident, payload=value)
                    else:
                        if not value:
                            #print (f"    > Instanciate null child object: {attr}={cls}()")
                            value = cls()
                        elif isinstance(value, cls):
                            #print (f"    > Instanciate child object: {attr}={cls}({value})")
                            value = cls(value)
                        else:
                            #print (f"    > Instanciate empty child object: {attr}={cls}()")
                            try:
                                value = cls(value)
                            except Exception as err:
                                self.log.critical (f"Type mismatch between: {cls} and {value}")
                                raise NotExpectedType(err)
                else:
                    #print (f"    > Instanciate direct assignment: {attr}={value}")
                    value = value

            result[attr] = value

        # Happend other keys
        done_keys = [ remap.key for remap in conf_struct if remap.ident]
        for key, val in payload.items():
            if key not in done_keys:
                result[key] = val

        # Create children
        assert isinstance(result, dict)
        self._nodes = result




    def add_child(self, ident, obj):
        self._nodes[ident] = obj

    def conf_make_defaults(self, payload):
        "For ConfDict"

        # TEMP
        return payload

        # TOFIX: To be reenabled
        result = super(ConfDict, self).conf_make_defaults(payload)
        if not result:
            result = {}

        # Overrides dict defaults
        if isinstance(payload, dict):
            result.update(payload)
        
        return result


    def get_nodes(self, explain=False):
        "For ConfDict"
        result = {}
        for name, value in self._nodes.items():

            if isinstance(value, Conf):

                if explain:
                    item_cls = getattr(value, "conf_struct2", None)
                    if item_cls and inspect.isclass(item_cls):
                        item_cls = "/" + item_cls.__name__
                    elif item_cls:
                        item_cls = "/*"
                    else:
                        item_cls = ""
                    name = f"{name} ({value}{item_cls})"

                result[name] = value.get_nodes(explain=explain)

        if explain:
            return result or self.get_config()
        else:
            return result

    def get_config(self, explain=False):
        "For ConfDict"
        
        result = {}
        children = self._nodes

        # if not isinstance(children, dict):
        #     return children

        for key, child in children.items():
            
            if isinstance(child, Conf):
                children = child.get_config(explain=explain)
                if explain:
                    key = f"{key} ({child})"
            else:
                
                children = child

            result[key] = children

        return result
        # if explain:
        #     #return str(self), result
        #     return {
        #         f"{self} <ConfDict>": result
        #         #"children|": result,
        #     }
        # else:
        #     return result


    def items(self):
        return self._nodes.items()


class ConfAttr(ConfDict):

    def add_child(self, ident, obj):
        super(ConfAttr, self).add_child(ident, obj)
        setattr(self, ident, obj)

    def __getattr__(self,key):
        
        if key in self._nodes:
            #print (f"Get value: {key} for {id(self)}")
            return self._nodes[key]

        # Todo: Implement nice warning for dropped cghildrens !!!
        # if self.conf_struct2:
        #     matches = [ remap.attr for remap in self.conf_struct2 if remap.attr]
        #     self.conf_struct2
        #     print ("ConfDict Struct2")
        #     return self.conf_build_future(payload)


        raise AttributeError(f"Missing attribute: {key} in {self}")


    def __setattr__(self, key, value):

        if key in self._nodes:
            # Set attribute if in _nodes
            #print (f"Set node value: {key}={value} for {self}")
            self._nodes[key] = value
            self.__dict__[key] = value
        else:
            # or just set regular attribute
            #print (f"Set attr value: {key}={value} for {self}")
            super(ConfAttr, self).__setattr__(key, value)


    # def conf_build(self, payload):
    #     "Just assign the value, thats all"

    #     super(ConfAttr, self).conf_build(payload)
        
        # for key, val in self._nodes.items():
        #     self.__dict__[key] = val


    # def conf_build_V1(self, payload):
    #     "Just assign the value, thats all"

    #     super(ConfAttr, self).conf_build(payload)

    #     for attr, item in self._nodes.items():
    #         print (f"  > Set obj atribute '{self}': {attr}={item}")
    #         setattr(self, attr, item)

    #     #return value


    # def conf_build_V2_broken(self, payload):
    #     "Just assign the value, thats all"

    #     super(ConfAttr, self).conf_build(payload)

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


    # def conf_build(self, payload):
    #     "Just assign the value, thats all"

    #     super(ConfAttr, self).conf_build(payload)

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



def map_node_class(payload):

    if isinstance(payload, dict):
        return ConfAttr
    elif isinstance(payload, list):
        return ConfList
    else:
        return type(payload)


def map_all_class(payload):
#def map_node_class(payload):

    if isinstance(payload, dict):
        return ConfAttr
    elif isinstance(payload, list):
        return ConfList
    else:
        return ConfVal

class ConfAuto():


    # def __new__(cls, *args, **kwargs):

    #     obj = object.__new__(cls)
    #     return obj

    def __init__(self, *args, ident=None, payload=None, autoconf=-1, **kwargs):

        self.__class__ = map_node_class(payload)

        #print ("YOOOOO", payload , self.__class__)

        super(self.__class__, self).__init__(*args, ident=ident, payload=payload, autoconf=autoconf, **kwargs)

# Hooks
# --------------------------

class Hooks():

    def __init__(self, *args, **kwargs):

        super(Hooks, self).__init__(*args, **kwargs)
        
        self.log.debug(f"__init__: Hooks/{self}")
        if callable(getattr(self, '_init', None)):
            self._init(*args, **kwargs)



