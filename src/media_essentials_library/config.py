from __future__ import annotations

import json
from pathlib import Path

from media_essentials_library.models.config import PlexServerConfig
from media_essentials_library.paths import get_app_config_dir
from media_essentials_library.services.secrets import (
    SecretStorageError,
    load_plex_token,
    save_plex_token,
)

CONFIG_FILE_NAME = "config.json"


def get_config_path(config_dir: Path | None = None) -> Path:
    if config_dir is None:
        config_dir = get_app_config_dir()
    return config_dir / CONFIG_FILE_NAME


def load_config(config_dir: Path | None = None) -> PlexServerConfig:
    config_path = get_config_path(config_dir)
    if not config_path.exists():
        return PlexServerConfig(token=_load_plex_token_or_empty())

    with config_path.open(encoding="utf-8") as config_file:
        data = json.load(config_file)

    return PlexServerConfig(
        server_url=str(data.get("server_url", "")),
        token=_load_plex_token_or_empty() or str(data.get("token", "")),
        date_format=str(data.get("date_format", PlexServerConfig.date_format)),
        language=str(data.get("language", PlexServerConfig.language)),
    )


def save_config(config: PlexServerConfig, config_dir: Path | None = None) -> Path:
    config_path = get_config_path(config_dir)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    save_plex_token(config.token)

    with config_path.open("w", encoding="utf-8") as config_file:
        json.dump(
            {
                "server_url": config.server_url,
                "date_format": config.date_format,
                "language": config.language,
            },
            config_file,
            indent=2,
        )

    return config_path


def _load_plex_token_or_empty() -> str:
    try:
        return load_plex_token()
    except SecretStorageError:
        return ""
