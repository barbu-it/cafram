

# Values/Containers mixins
################################################################

# import json
# import yaml # pyyaml

from cafram2.utils import to_json, from_json, to_yaml, from_yaml

from pprint import pformat
from typing import MutableSequence, MutableSet, MutableMapping

from pprint import pprint
from cafram2.mixins import BaseMixin
from cafram2.common import CaframMixin, CaframNode
from cafram2.nodes import Node2
import cafram2.errors as errors

import json
import logging
log = logging.getLogger(__name__)

from cafram2.mixins.base import MapAttrMixin

# Payload mixins
################################################################


class PayloadMixin(BaseMixin):

    name = "payload"
    name_param = "payload"
    value_alias = "value"

    payload_schema = False
    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: PayloadMixin",
        "description": "PayloadMixin Configuration",
        "default": {},
        "properties": {
            "name": {
                "title": "Mixin name",
                "description": "Name of the mixin. Does not keep alias if name is set to `None` or starting with a `.` (dot)",
                "default": name,
                "oneOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
            "name_param": {
                "title": "Mixin name parameter",
                "description": "Name of the parameter to load name from",
                "default":name_param,
            },
            "value_alias": {
                "title": "Value alias name",
                "description": "Name of the alias to retrieve value. Absent if set to None",
                "default": value_alias,
                "oneOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
            "payload_schema": {
                "title": "Payload schema",
                "description": "Json schema that must validate payload",
                "default": payload_schema,
                "oneOf": [
                    {
                        "title": "JSONschema definition",
                        "type": "dict",
                    },
                    {
                        "title": "Disabled",
                        "type": "null",
                    },
                ],
            },
        },
    }


    def _init(self, **kwargs):

        super()._init(**kwargs)
        
        self._value = None
        self._payload = kwargs.get(self.name_param, None)
        self.set_value(self._payload)
        self._register_alias()


    def _register_alias(self):
        if self.value_alias:
            self.node_ctrl.alias_register(self.value_alias, self.value)


    # Generic value handler
    # ---------------------
    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, value):
        self.set_value(value)

    @value.deleter
    def value(self):
        self.set_value(None)
    

    def get_value(self):
        "Get a value"
        return self._value
    
    def set_value(self, value):
        "Set a value"
        conf = self.transform(value)
        conf = self.validate(conf)
        self._value = conf
        return self._value


    # Transformers/Validators
    # ---------------------

    def transform(self, payload):
        "Transform payload before"
        return payload


    def validate(self, payload):
        "Validate config against json schema"
        
        schema = self.payload_schema
        if isinstance(schema, dict):
            valid = True
            if not valid:
                raise errors.CaframException(f"Can't validate: {payload}")    

        return payload

    def schema(self):
        "Return json schema for payload"
        return self.payload_schema




# Hier mixins
################################################################

class HierParentMixin(BaseMixin):
    "Hier mixin that manage parent relationships"

    _parent = None
    parent_param = "parent"

    def _init(self, **kwargs):

        super()._init(**kwargs)
        self._parent = kwargs.get(self.parent_param, None) or self._parent

        # print ("INIT PARENT", self._parent)


    def get_parent(self, ctrl=True):
        "Return direct parent"

        if self._parent:
            if ctrl:
                return self._parent.node_ctrl
            else:
                return self._parent
        
        return None

    def get_parents(self, ctrl=True, level=-1):
        "Return all parents"

        parents = []

        parent = self.get_parent(ctrl=False)
        while level != 0:
            
            if parent:
                parents.append(parent)

            # Prepare next iteration
            #if isinstance(parent, self.__class__):
            if isinstance(parent, HierParentMixin):
                parent = parent.get_parent(ctrl=False)
            else:
                # print ("SKIP", parent)
                break
            level -= 1

        # Return values
        if ctrl:
            ret = []
            for parent in parents:

                ctrl = None
                if hasattr(parent, "node_ctrl"):
                    ctrl = parent.node_ctrl

                ret.append(ctrl)
            return ret
        else:
            return parents


class HierChildrenMixin(BaseMixin):
    "Hier mixin that manage children relationships"

    # Overrides
    # -----------------
    
    children = {}
    children_param = "children"
    
    def _init(self, **kwargs):

        super()._init(**kwargs)
        self.children = kwargs.get(self.children_param, None) or self.children
        self._parse_children()

    # Additional methods
    # -----------------

    def _parse_children(self):
        "Add children from config"

        for index, child in self.children.items():
            self.add_child(child, index=index)


    def add_child(self, child, index=None, alias=True):
        "Add a new child to mixin"

        children = self._children

        if isinstance(children, dict):
            ret = {}
            index = index or getattr(child, "name", None)
            assert index, "Index is required when children are dict"
            self._children[index] = child

        elif isinstance(children, list):
            index = index or len(children)
            self._children.insert(index, child)
            
        if alias:
            self.node_ctrl.alias_register(index, child)



    def get_children(self, level=0):
        children = self._children

        if level == 0:
            return children

        level -= 1
        if isinstance(children, dict):
            ret = {}

            for child_index, child in children.items():
                children_ = child
                if isinstance(child, NodePayload):
                    children_ = child.conf.get_children(level=level)

                ret[child_index] = children_

            return ret

        elif isinstance(children, list):
            ret = []

            for child_index, child in enumerate(children):
                children_ = child
                if isinstance(child, NodePayload):
                    children_ = child.conf.get_children(level=level)

                ret.append(children_)

            return ret


class HierMixin(HierParentMixin, HierChildrenMixin):
    "Hier mixin that manage parent and children relationships"








# Conf mixins (Composed classes)
################################################################

        

class ConfMixin(HierParentMixin, PayloadMixin):
    "Conf mixin that manage a basic serializable value"

    name = "conf"

    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: PayloadMixin",
        "description": "PayloadMixin Configuration",
        "default": {},
        "properties": {
            "name": {
                "title": "Mixin name",
                "description": "Name of the mixin. Does not keep alias if name is set to `None` or starting with a `.` (dot)",
                "default": name,
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

    def _init(self, **kwargs):

        super()._init(**kwargs)

        # Value check
        value = self.get_value()
        valid = (str, bool, dict, list, type(None))
        if not isinstance(value, valid):
            assert False, f"TYPE ERROR, got: {type(value)}"


    # Converter methods
    # -----------------

    # Main methods
    # def to_data(self):
    #     "Export value"
    #     return self.get_value()

    # def from_data(self, payload):
    #     "Import value"
    #     return self.set_value(payload)

    # Format methods
    # def to_json(self):
    #     "Export value from json string"
    #     return json.dumps(self.to_data())

    # def from_json(self, payload):
    #     "Import value from json string"
    #     conf = json.loads(payload)
    #     self.from_data(conf)

    def to_json(self):
        "Export value from json string"
        return to_json(self.get_value())

    def from_json(self, payload):
        "Import value from json string"
        self.set_value(from_json(payload))

    def to_yaml(self):
        "Export value from yaml string"
        return to_yaml(self.get_value())

    def from_yaml(self, payload):
        "Import value from yaml string"
        self.set_value(from_yaml(payload))



    # Additional methods
    # -----------------

    def is_mutable(self):
        "Check if value is mutable or not"
        payload = self._payload
        return issubclass(type(payload), (MutableSequence, MutableSet, MutableMapping))


class ConfContainerMixin(HierChildrenMixin, ConfMixin):
    "Conf mixin that manage a nested serializable values"

    children = True

    _schema = {
        # "$defs": {
        #     "AppProject": PaasifyProject.conf_schema,
        # },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Mixin: PayloadMixin",
        "description": "PayloadMixin Configuration",
        "default": {},
        "properties": {
            "children": {
                "title": "Children configuration",
                "description": "`False` does not generate children, `null` does generate 1 level children, `True` generate recursively all children. A `dict` can also be provided in `ConfDictMixin` case",
                "default": children,
                "oneOf": [
                    {
                        "description": "Generate recursively children containers if set to `True`, does not generate children otherwise",
                        "type": "boolean",
                    },
                    {
                        "description": "Generate only first children level from types",
                        "type": "null",
                    },
                    {
                        "description": "Generate types on attribute (ConfDictMixin only)",
                        "type": "dict",
                    },
                ],
            },
        },
    }


class ConfDictMixin(ConfContainerMixin):
    "Conf mixin that manage a serializable dict of values"
    

    def _parse_children(self):

        # Get data
        value = self.get_value() or {}
        self._children = {}

        # Sanity checks
        assert isinstance(value, dict), f"Got: {value}"

        # Parse children
        children_conf = self.children
        children_map = {}
        if children_conf is True:
            log.info(f"Children configs is automatic")
            for child_key, child_value in value.items():
                child_cls = map_node_class(child_value)
                children_map[child_key] = child_cls
                log.info(f"Child '{child_key}' config is {child_cls}")
        elif children_conf is None:
            log.info(f"Children configs is None")
            for child_key, child_value in value.items():
                children_map[child_key] = None
                log.info(f"Child '{child_key}' config is native {type(child_value)}")
        elif children_conf is False:
            pass
        else:
            msg = f"Invalid configuration for children: {children_conf}"
            raise errors.CaframException(msg)

        # Instanciate children
        name_param = self.name_param
        parent_param = self.parent_param
        for child_key, child_cls in children_map.items():
            
            child_value = value.get(child_key)
            if child_cls is None:
                child = child_value
                msg = f"Create child '{child_key}': {type(child_value).__name__}({child_value})"
                log.info(msg)
                #print (msg)
            else:
                child_args = {
                    name_param: child_value,
                    parent_param: self,
                }
                msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                log.info(msg)
                #print (msg)

                assert issubclass(child_cls, CaframNode)
                child = child_cls(self, **child_args)
                #child = self.create_child(child_cls, child_value, child_key=child_key, **child_args)

            self.add_child(child, index=child_key, alias=True)


class ConfListMixin(ConfContainerMixin):
    """Conf mixin that manage a serializable list of values
    
    Usage:
      ConfListMixin(node_ctrl, mixin_conf=None)
      ConfListMixin(node_ctrl, mixin_conf=[ConfDictMixin])

    """
    def _parse_children(self):

        # Get data
        value = self.get_value() or []
        self._children = []

        # Sanity checks
        assert isinstance(value, list), f"Got: {value}"

        children_conf = self.children
        if children_conf is True:

            name_param = self.name_param
            parent_param = self.parent_param
            
            log.info(f"Children configs is automatic")
            for child_key, child_value in enumerate(value):
                child_cls = map_node_class(child_value)
                if child_cls is None:
                    child = child_value
                else:
                    child_args = {
                        name_param: child_value,
                        parent_param: self,
                    }
                    msg = f"Create child '{child_key}': {child_cls.__name__}({child_args})"
                    log.info(msg)
                    #print (msg)

                    assert issubclass(child_cls, CaframNode)
                    child = child_cls(self, **child_args)

                self.add_child(child_value)
                log.info(f"Child '{child_key}' config is {child_cls}")
        elif children_conf is None:
            log.info(f"Children configs is None")
            for child_key, child_value in enumerate(value):
                #children_map[child_key] = None
                self.add_child(child_value)
                log.info(f"Child '{child_key}' config is native {type(child_value)}")
        elif children_conf is False:
            pass
        else:
            msg = f"Invalid configuration for children: {children_conf}"
            raise errors.CaframException(msg)


# Application helpers
################################################################

class NodePayload(Node2):
    
    _node_conf = [
        {
            "mixin": PayloadMixin
        }
    ]

class NodeConf(NodePayload):
    
    _node_conf = [
        {
            "mixin": ConfMixin
        }
    ]


class NodeConfDict(NodeConf):
    
    _node_conf = [
        {
            "mixin": ConfDictMixin
        }
    ]

class NodeConfList(NodeConf):
    
    _node_conf = [
        {
            "mixin": ConfListMixin
        }
    ]

def map_node_class_full(payload):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        return NodeConfDict
    if isinstance(payload, list):
        #return NodeConf
        # TEMPORARY
        return NodeConfList

    return NodeConf
    
def map_node_class(payload):
    "Map anything to cafram classes"

    if isinstance(payload, dict):
        return NodeConfDict
    if isinstance(payload, list):
        #return None
        return NodeConfList

    return None
