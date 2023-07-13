"""
Tree mixins
"""

# Imports
################################################################
import copy
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

# from ..nodes import Node
from ...nodes import Node
from . import BaseMixin

# from .. import errors


# from .base import PayloadMixin, NodePayload


# Hier mixins
################################################################


class HierMixinGroup(BaseMixin):
    "Hier mixin that group all HierMixins"


class HierParentMixin(HierMixinGroup):
    "Hier mixin that manage parent relationships"

    _parent = None
    mixin_param___parent = "parent"

    def get_parent(self, target=None):
        "Return direct parent"

        target = target or "node"
        ret = getattr(self, "_parent", None)

        if target == "mixin":
            return ret

        if target == "ctrl":
            return ret.get_ctrl()

        if target == "node":
            return ret.get_obj()

        assert False, f"Unknown target: {target}, please choose one of: node,ctrl,mixin"

    def get_parent_by_cls(self, cls, target=None, first=True):
        "Return the closest parent having a given class"

        target = target or "node"

        ret = []
        for parent in self.get_parents(target=target):

            if isinstance(parent, cls):
                if first:
                    return parent

                ret.append(parent)

        if first:
            return None
        return ret

    def get_parents(self, target=None, level=-1):
        "Return all parents"

        target = target or "node"
        parents = []

        # Find parents
        parent = self.get_parent(target="mixin")
        while level != 0:

            if parent:
                parents.append(parent)

            # Prepare next iteration
            if isinstance(parent, HierParentMixin):
                parent = parent.get_parent(target="mixin")
            else:
                break
            level -= 1

        # Process output
        if target == "mixin":
            return parents

        if target == "ctrl":
            return [parent.get_ctrl() for parent in parents]

        if target == "node":
            return [parent.get_obj() for parent in parents]

        assert False, f"Unknown target: {target}, please choose one of: node,ctrl,mixin"

    def get_child_level(self):
        "Return the node deepness from root node"
        # assert False, "TODO: Make tests"
        parents = self.get_parents(target="mixin", level=-1)
        return len(parents)


class HierChildrenMixin(HierMixinGroup):
    "Hier mixin that manage children relationships"

    # Overrides
    # -----------------

    # This hold the children configuration
    # children = {}

    # In which param to look the children conf
    mixin_param___children = "children"

    # This hold the internal children state
    _children: Any = []

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # self._super__init__(super(), *args, **kwargs)

        self._children = copy.copy(self._children)
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
            index = index or getattr(child, "mixin_key", None)
            assert index, "Index is required when children are dict"
            self._children[index] = child

        elif isinstance(children, list):
            index = index or len(children)
            self._children.insert(index, child)

        if alias:
            self.node_ctrl.alias_register(index, child)

    def get_children(self, level=0):
        "Get children"

        children = self._children

        if level == 0:
            return children

        level -= 1
        ret = None
        if isinstance(children, dict):
            ret = {}

            for child_index, child in children.items():
                children_ = child
                if isinstance(child, Node):
                    children_ = child.conf.get_children(level=level)

                ret[child_index] = children_

        elif isinstance(children, list):
            ret = []

            for child_index, child in enumerate(children):
                children_ = child
                if isinstance(child, Node):
                    children_ = child.conf.get_children(level=level)

                ret.append(children_)

        return ret


class HierMixin(HierParentMixin, HierChildrenMixin):
    "Hier mixin that manage parent and children relationships"
