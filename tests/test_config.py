from media_essentials_library import config as config_module
from media_essentials_library.models.config import PlexServerConfig


def test_save_config_keeps_token_out_of_config_file(tmp_path, monkeypatch):
    saved_tokens = []
    monkeypatch.setattr(config_module, "save_plex_token", saved_tokens.append)

    config_path = config_module.save_config(
        PlexServerConfig(
            server_url="http://plex.local:32400",
            token="secret-token",
            date_format="de",
            language="de",
        ),
        tmp_path,
    )

    assert saved_tokens == ["secret-token"]
    assert "secret-token" not in config_path.read_text(encoding="utf-8")


def test_load_config_prefers_keyring_token_over_legacy_file_token(tmp_path, monkeypatch):
    config_path = config_module.get_config_path(tmp_path)
    config_path.write_text(
        """
{
  "server_url": "http://plex.local:32400",
  "token": "legacy-token",
  "date_format": "de",
  "language": "de"
}
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "load_plex_token", lambda: "keyring-token")

    config = config_module.load_config(tmp_path)

    assert config.server_url == "http://plex.local:32400"
    assert config.token == "keyring-token"
    assert config.date_format == "de"
    assert config.language == "de"
