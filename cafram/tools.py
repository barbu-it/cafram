
from cafram2.nodes import Node2
from cafram2.mixins import BaseMixin


class MixinLoader():

    def __init__(self, mixin):

        # Prepare mixin
        self._mixin_src = mixin or BaseMixin
        self._mixin_src_name = self._mixin_src.name
        #self._mixin_src.name = "debug"

        class MixinLoaderInst(self._mixin_src):
            name = "debug"

        # Instanciate empty node
        self._mixin = Node2(node_conf=[MixinLoaderInst])
        self.ctrl = self._mixin._node


    def dump(self, **kwargs):
        self._mixin.debug.dump(**kwargs)

    def doc(self, **kwargs):
        print (f"Default mixin name: {self._mixin_src_name} (instead of debug)\n")
        self._mixin.debug.doc(**kwargs)
