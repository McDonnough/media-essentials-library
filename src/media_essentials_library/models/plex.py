from dataclasses import dataclass


@dataclass(frozen=True)
class PlexLibrary:
    key: str
    title: str
    media_type: str = "show"


@dataclass(frozen=True)
class PlexMediaItem:
    key: str
    title: str
    year: int | None
    media_type: str
    guids: tuple[str, ...] = ()
    web_url: str = ""


@dataclass(frozen=True)
class PlexServerResource:
    key: str
    title: str
    owned: bool


@dataclass(frozen=True)
class PlexShow:
    key: str
    title: str
    year: int | None
    season_count: int
    episode_count: int


@dataclass(frozen=True)
class PlexEpisode:
    key: str
    season_number: int | None
    episode_number: int | None
    title: str
