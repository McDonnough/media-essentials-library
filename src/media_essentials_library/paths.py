from pathlib import Path

from platformdirs import user_config_dir

APP_NAME = "Media Essentials Library"


def get_app_config_dir() -> Path:
    return Path(user_config_dir(APP_NAME, appauthor=False))

