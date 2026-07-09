from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import keyring


SERVICE_NAME = "Media Essentials Library"
PLEX_TOKEN_KEY = "plex_token"


class SecretStorageError(OSError):
    """Raised when the OS secret store cannot be used."""


def load_plex_token() -> str:
    keyring_module = _load_keyring()
    try:
        return keyring_module.get_password(SERVICE_NAME, PLEX_TOKEN_KEY) or ""
    except Exception as error:
        raise SecretStorageError(
            f"Could not load Plex token from secure storage: {error}"
        ) from error


def save_plex_token(token: str) -> None:
    keyring_module = _load_keyring()
    try:
        if token:
            keyring_module.set_password(SERVICE_NAME, PLEX_TOKEN_KEY, token)
        else:
            delete_plex_token()
    except Exception as error:
        raise SecretStorageError(f"Could not save Plex token to secure storage: {error}") from error


def delete_plex_token() -> None:
    keyring_module = _load_keyring()
    try:
        keyring_module.delete_password(SERVICE_NAME, PLEX_TOKEN_KEY)
    except Exception as error:
        if error.__class__.__name__ == "PasswordDeleteError":
            return
        raise SecretStorageError(
            f"Could not delete Plex token from secure storage: {error}"
        ) from error


def _load_keyring() -> keyring:
    try:
        import keyring
    except ImportError as error:
        raise SecretStorageError(
            "The keyring package is not installed. Run `pip install -e .` or install keyring."
        ) from error

    return keyring
