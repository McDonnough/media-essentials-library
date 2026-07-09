from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MetadataEpisode:
    key: str
    season_number: int | None
    episode_number: int | None
    title: str
    airdate: date | None

