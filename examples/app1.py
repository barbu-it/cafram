from cafram.mixins.tree import ConfDictMixin, NodeConfDict
from cafram.nodes2 import Node

app_config = {
        "namespace": "username",        
        "config": {
            "enabled": True,
            "desc": "This is a description",
            "remote": "http://gitlab.com/",
            "branches": [
                    "main"
                ],
            "var_files": [
                "first.env",
                "second.env",
            ],
        },
        "repos": [
            {
                "name": "my_repo1.git",
            },
            {
                "name": "my_repo2.git",
                "branches": [
                    "main",
                    "develop"
                ],
                "enabled": False,
            },
            "my_repo3.git",
        ],
           
    }

# You can either configure manually your class
class MyApp(Node):
    _node_conf = [
        {
            "mixin": ConfDictMixin,
        }
    ]

# Or use the preset Node class NodeConfDict
class MyApp(NodeConfDict):
    pass


if __name__ == "__main__":
    # Start app this way:
    app = MyApp(payload=app_config)

    app._node.dump(details=True)
