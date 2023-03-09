"""
Cafram tools
"""

from .nodes2 import Node
from .mixins import BaseMixin


class MixinLoader:
    "Helper class to instanciate a Mixin class"

    def __init__(self, mixin):

        # Prepare mixin
        self._mixin_src = mixin or BaseMixin
        self._mixin_src_name = self._mixin_src.name

        class MixinLoaderInst(self._mixin_src):
            name = "debug"

        # Instanciate empty node
        self._mixin = Node(node_conf=[MixinLoaderInst])
        self.ctrl = self._mixin._node

    def dump(self, **kwargs):
        "Execute mixin dump method"
        self._mixin.debug.dump(**kwargs)

    def doc(self, **kwargs):
        "Display mixin documentation"
        print(f"Default mixin name: {self._mixin_src_name} (instead of debug)\n")
        self._mixin.debug.doc(**kwargs)
