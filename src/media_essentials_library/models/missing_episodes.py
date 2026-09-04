from dataclasses import dataclass
from datetime import date

from media_essentials_library.models.metadata import MetadataSource
from media_essentials_library.models.plex import PlexShow


@dataclass(frozen=True)
class MissingEpisode:
    key: str
    season_number: int | None
    episode_number: int | None
    title: str
    airdate: date | None
    is_unaired: bool
    metadata_source: MetadataSource | None = None


@dataclass(frozen=True)
class ShowMissingEpisodes:
    show: PlexShow
    missing_episodes: list[MissingEpisode]
    metadata_source: MetadataSource | None = None
