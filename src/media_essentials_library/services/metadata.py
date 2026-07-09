from __future__ import annotations

import json
import time
from datetime import date
from functools import cache
from threading import Lock
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from media_essentials_library.models.metadata import MetadataEpisode

TVMAZE_API_BASE_URL = "https://api.tvmaze.com"
TVMAZE_MAX_RETRIES = 4
TVMAZE_MIN_INTERVAL_SECONDS = 0.55
TVMAZE_RETRY_BACKOFF_SECONDS = 2.0

_last_tvmaze_request_at = 0.0
_tvmaze_throttle_lock = Lock()


@cache
def get_expected_episodes(show_title: str) -> list[MetadataEpisode]:
    """
    Return expected episodes for a show from TVMaze.
    """
    for attempt in range(TVMAZE_MAX_RETRIES):
        try:
            return _fetch_expected_episodes(show_title)
        except HTTPError as error:
            if error.code == 404:
                return []
            if error.code != 429 or attempt == TVMAZE_MAX_RETRIES - 1:
                raise

            time.sleep(TVMAZE_RETRY_BACKOFF_SECONDS * (attempt + 1))

    return []


def _fetch_expected_episodes(show_title: str) -> list[MetadataEpisode]:
    query = urlencode({"q": show_title, "embed": "episodes"})
    url = f"{TVMAZE_API_BASE_URL}/singlesearch/shows?{query}"

    _wait_for_tvmaze_slot()
    with urlopen(url, timeout=10) as response:
        data = json.load(response)

    episodes = data.get("_embedded", {}).get("episodes", [])
    return [_parse_tvmaze_episode(episode) for episode in episodes]


def _wait_for_tvmaze_slot() -> None:
    global _last_tvmaze_request_at

    with _tvmaze_throttle_lock:
        elapsed = time.monotonic() - _last_tvmaze_request_at
        remaining = TVMAZE_MIN_INTERVAL_SECONDS - elapsed
        if remaining > 0:
            time.sleep(remaining)

        _last_tvmaze_request_at = time.monotonic()


def _parse_tvmaze_episode(episode: dict) -> MetadataEpisode:
    airdate = _parse_airdate(episode.get("airdate"))
    return MetadataEpisode(
        key=str(episode.get("id", "")),
        season_number=episode.get("season"),
        episode_number=episode.get("number"),
        title=str(episode.get("name") or ""),
        airdate=airdate,
    )


def _parse_airdate(value: str | None) -> date | None:
    if not value:
        return None

    return date.fromisoformat(value)
