from dataclasses import dataclass
from datetime import date

from media_essentials_library.models.plex import PlexShow


@dataclass(frozen=True)
class MissingEpisode:
    key: str
    season_number: int | None
    episode_number: int | None
    title: str
    airdate: date | None
    is_unaired: bool


@dataclass(frozen=True)
class ShowMissingEpisodes:
    show: PlexShow
    missing_episodes: list[MissingEpisode]
