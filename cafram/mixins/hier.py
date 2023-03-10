"""
Tree mixins
"""

# Imports
################################################################
import copy

# from ..nodes import Node
from ..nodes2 import Node

# from .. import errors

from . import BaseMixin

# from .base import PayloadMixin, NodePayload


# Hier mixins
################################################################


class HierMixinGroup(BaseMixin):
    "Hier mixin that group all HierMixins"


class HierParentMixin(HierMixinGroup):
    "Hier mixin that manage parent relationships"

    _parent = None
    _param__parent = "parent"

    def get_parent(self, ctrl=True):
        "Return direct parent"

        if self._parent:
            if ctrl:
                return self._parent.node_ctrl
            return self._parent
        return None

    # def get_parents2(self, select=None, level=-1, value=None):
    #     "Return first parent that match criteria"
    #     assert False, "TODO: Make tests"
    #     value = value or HierParentMixin
    #     pass

    def get_parents(self, ctrl=True, level=-1):
        "Return all parents"

        parents = []

        parent = self.get_parent(ctrl=False)
        while level != 0:

            if parent:
                parents.append(parent)

            # Prepare next iteration
            if isinstance(parent, HierParentMixin):
                parent = parent.get_parent(ctrl=False)
            else:
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

        return parents

    def get_child_level(self):
        "Return the node deepness from root node"
        # assert False, "TODO: Make tests"
        parents = self.get_parents(ctrl=False, level=-1)
        return len(parents)


class HierChildrenMixin(HierMixinGroup):
    "Hier mixin that manage children relationships"

    # Overrides
    # -----------------

    # This hold the children configuration
    children = {}

    # In which param to look the children conf
    _param__children = "children"

    # This hold the internal children state
    _children = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
