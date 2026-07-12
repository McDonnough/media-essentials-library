from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GITHUB_REPOSITORY = "McDonnough/media-essentials-library"
LATEST_RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"
RELEASES_URL = f"https://github.com/{GITHUB_REPOSITORY}/releases"
PACKAGE_NAME = "media-essentials-library"
REQUEST_TIMEOUT_SECONDS = 3
VERSION_RESOURCE = "version.txt"


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    url: str


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    url: str


def get_current_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return get_bundled_version()


def get_bundled_version() -> str:
    try:
        return (
            files("media_essentials_library")
            .joinpath(VERSION_RESOURCE)
            .read_text(encoding="utf-8")
            .strip()
        )
    except (FileNotFoundError, ModuleNotFoundError):
        return "0.0.0"


def check_for_update(
    current_version: str | None = None,
    latest_release: ReleaseInfo | None = None,
) -> UpdateInfo | None:
    if current_version is None:
        current_version = get_current_version()
    if latest_release is None:
        latest_release = fetch_latest_release()

    if latest_release is None:
        return None

    if is_newer_version(latest_release.version, current_version):
        return UpdateInfo(
            current_version=current_version,
            latest_version=latest_release.version,
            url=latest_release.url,
        )
    return None


def fetch_latest_release() -> ReleaseInfo | None:
    request = Request(
        LATEST_RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{PACKAGE_NAME}/update-check",
        },
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None

    tag_name = data.get("tag_name")
    release_url = data.get("html_url", RELEASES_URL)
    if not isinstance(tag_name, str) or not isinstance(release_url, str):
        return None

    return ReleaseInfo(version=tag_name, url=release_url)


def is_newer_version(candidate: str, current: str) -> bool:
    candidate_parts = parse_release_version(candidate)
    current_parts = parse_release_version(current)
    if candidate_parts is None or current_parts is None:
        return False
    return candidate_parts > current_parts


def parse_release_version(value: str) -> tuple[int, int, int] | None:
    version_value = value.strip()
    if version_value.startswith("v"):
        version_value = version_value[1:]

    core_version = version_value.split("-", 1)[0]
    parts = core_version.split(".")
    if not 1 <= len(parts) <= 3:
        return None
    if any(not part.isdecimal() for part in parts):
        return None

    padded_parts = [int(part) for part in parts]
    padded_parts.extend([0] * (3 - len(padded_parts)))
    return tuple(padded_parts)
