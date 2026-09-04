from collections.abc import Callable
from datetime import date

from media_essentials_library.models.missing_episodes import MissingEpisode, ShowMissingEpisodes
from media_essentials_library.models.plex import PlexEpisode, PlexShow
from media_essentials_library.services.metadata import get_expected_episodes
from media_essentials_library.services.plex import get_show_episodes, get_tv_shows

ScanProgressCallback = Callable[[int, int, PlexShow], None]


def find_missing_episodes(
    show_title: str,
    plex_episodes: list[PlexEpisode],
    today: date | None = None,
) -> list[MissingEpisode]:
    """
    Compare Plex episodes with metadata provider episodes and return episodes absent from Plex.
    """
    if today is None:
        today = date.today()

    existing_episode_numbers = {
        (episode.season_number, episode.episode_number)
        for episode in plex_episodes
        if episode.season_number is not None and episode.episode_number is not None
    }

    missing_episodes = []
    for expected_episode in get_expected_episodes(show_title):
        episode_number = (expected_episode.season_number, expected_episode.episode_number)
        if episode_number in existing_episode_numbers:
            continue

        missing_episodes.append(
            MissingEpisode(
                key=expected_episode.key,
                season_number=expected_episode.season_number,
                episode_number=expected_episode.episode_number,
                title=expected_episode.title,
                airdate=expected_episode.airdate,
                is_unaired=expected_episode.airdate is None or expected_episode.airdate > today,
                metadata_source=expected_episode.source,
            )
        )

    return missing_episodes


def scan_library_for_missing_episodes(
    library_key: str,
    progress_callback: ScanProgressCallback | None = None,
) -> list[ShowMissingEpisodes]:
    """
    Scan a Plex library and return only shows that have missing episodes.
    """
    results = []
    shows = get_tv_shows(library_key)
    total_shows = len(shows)

    for scanned_count, show in enumerate(shows, start=1):        
        if progress_callback is not None:
            progress_callback(scanned_count, total_shows, show)
        plex_episodes = get_show_episodes(show.key)
        missing_episodes = find_missing_episodes(show.title, plex_episodes)
        if not missing_episodes:
            continue

        metadata_source = next(
            (
                episode.metadata_source
                for episode in missing_episodes
                if episode.metadata_source
            ),
            None,
        )
        results.append(
            ShowMissingEpisodes(
                show=show,
                missing_episodes=missing_episodes,
                metadata_source=metadata_source,
            )
        )

    return results
