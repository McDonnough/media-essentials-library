from media_essentials_library.services import plex as plex_module


class Resource:
    def __init__(self, key, name, owned, provides="server"):
        self.clientIdentifier = key
        self.name = name
        self.owned = owned
        self.provides = provides


class Account:
    def resources(self):
        return [
            Resource("shared", "Shared server", False),
            Resource("client", "TV", True, "player"),
            Resource("owned", "My server", True),
        ]


def test_accessible_servers_uses_account_resources(monkeypatch):
    monkeypatch.setattr(plex_module, "MyPlexAccount", lambda token: Account())

    objects, resources = plex_module.get_accessible_server_resources("account-token")

    assert list(objects) == ["shared", "owned"]
    assert [(resource.key, resource.owned) for resource in resources] == [
        ("owned", True),
        ("shared", False),
    ]
