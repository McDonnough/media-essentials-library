import re
import unicodedata

from media_essentials_library.models.library_comparison import LibraryDuplicate
from media_essentials_library.models.plex import PlexMediaItem


def _normalized_title(title: str) -> str:
    value = unicodedata.normalize("NFKD", title).casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def find_library_duplicates(
    first_items: list[PlexMediaItem],
    second_items: list[PlexMediaItem],
) -> list[LibraryDuplicate]:
    """Find the same movies or shows in two inventories.

    Provider GUIDs are authoritative. Items without a shared GUID fall back to an exact
    normalized title, year, and media-type match. A year is required for the fallback to avoid
    false positives between remakes and shows with reused names.
    """
    second_by_guid: dict[tuple[str, str], list[PlexMediaItem]] = {}
    second_by_metadata: dict[tuple[str, str, int], list[PlexMediaItem]] = {}
    for item in second_items:
        for guid in item.guids:
            second_by_guid.setdefault((item.media_type, guid), []).append(item)
        if item.year is not None:
            key = (item.media_type, _normalized_title(item.title), item.year)
            second_by_metadata.setdefault(key, []).append(item)

    duplicates = []
    seen_pairs: set[tuple[str, str]] = set()
    for first in first_items:
        guid_matches = {
            item
            for guid in first.guids
            for item in second_by_guid.get((first.media_type, guid), [])
        }
        if guid_matches:
            candidates = ((item, "GUID") for item in guid_matches)
        elif first.year is not None:
            key = (first.media_type, _normalized_title(first.title), first.year)
            candidates = ((item, "title + year") for item in second_by_metadata.get(key, []))
        else:
            candidates = iter(())

        for second, matched_by in candidates:
            pair = (first.key, second.key)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                duplicates.append(LibraryDuplicate(first, second, matched_by))

    return sorted(
        duplicates,
        key=lambda duplicate: (duplicate.first.title.casefold(), duplicate.first.year or 0),
    )
