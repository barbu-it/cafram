from pprint import pprint

import cafram.nodes.errors as errors
from cafram.nodes.comp import BaseMixin
from cafram.nodes.ctrl import NodeCtrl

# ===================================================
# Basics
# ===================================================


def test_nodecomp__basic():
    "Test if a simple class instanciation works correclty"

    class TestCls:
        "My Test Class"

    _obj = TestCls()

    class ExampleMixin(BaseMixin):
        "My Example Mixin"

    _obj_mixins = {
        "key": {
            "mixin": ExampleMixin,
        }
    }
    node = NodeCtrl(_obj, obj_mixins=_obj_mixins, blih="BLIHH")

    mixin = node.mixin_get("key")

    assert mixin.mixin == ExampleMixin
    assert isinstance(mixin.mixin_conf, dict)
    assert isinstance(mixin.node_ctrl, NodeCtrl)
    pprint(mixin.__dict__)
    assert mixin.mixin_init_kwargs == {"blih": "BLIHH"}

    for attr in ["mixin", "mixin_conf", "mixin_key", "mixin_order"]:
        assert hasattr(mixin, attr)


def test_nodecomp__with_kwargs():
    "Test if a simple class instanciation works correclty"

    class TestCls:
        "My Test Class"

    _obj = TestCls()

    class ExampleMixin(BaseMixin):
        "My Example Mixin"

        mixin_param__my_Param = "my_param"

        my_Param = None

    _obj_mixins = {
        "key": {
            "mixin": ExampleMixin,
        }
    }

    node = NodeCtrl(_obj, obj_mixins=_obj_mixins, other_param="BLOH")

    assert node.mixin_get("key").my_Param is None
    assert not hasattr(node.mixin_get("key"), "other_param")
    assert "other_param" in node.mixin_get("key").mixin_init_kwargs

    assert node.mixin_get("key").mixin_init_kwargs == {"other_param": "BLOH"}

    node = NodeCtrl(_obj, obj_mixins=_obj_mixins, my_param="BLIHH", other_param="BLOH")
    assert node.mixin_get("key").my_Param == "BLIHH"
    assert not hasattr(node.mixin_get("key"), "other_param")
    assert "other_param" in node.mixin_get("key").mixin_init_kwargs


def test_nodecomp__with_kwargs_custom():
    "Test if a simple class instanciation works correclty"

    class TestCls:
        "My Test Class"

    _obj = TestCls()

    class ExampleMixin(BaseMixin):
        "My Example Mixin"

        # my_param = None
        my_Param = None

    _obj_mixins = {"key": {"mixin": ExampleMixin, "mixin_param__my_Param": "my_param"}}

    node = NodeCtrl(_obj, obj_mixins=_obj_mixins, other_param="BLOH")

    pprint(node.mixin_get("key").__dict__)

    assert node.mixin_get("key").my_Param is None
    assert not hasattr(node.mixin_get("key"), "other_param")
    assert "other_param" in node.mixin_get("key").mixin_init_kwargs

    assert node.mixin_get("key").mixin_init_kwargs == {"other_param": "BLOH"}

    node = NodeCtrl(_obj, obj_mixins=_obj_mixins, my_param="BLIHH", other_param="BLOH")
    assert node.mixin_get("key").my_Param == "BLIHH"
    assert not hasattr(node.mixin_get("key"), "other_param")
    assert "other_param" in node.mixin_get("key").mixin_init_kwargs


def test_nodecomp__with_aliases():
    "Test if a mixin aliases works correctly"


# ===================================================
# Other
# ===================================================
