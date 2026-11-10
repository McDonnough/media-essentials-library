from dataclasses import dataclass

from media_essentials_library.models.plex import PlexMediaItem


@dataclass(frozen=True)
class LibraryDuplicate:
    first: PlexMediaItem
    second: PlexMediaItem
    matched_by: str
