from functools import cache

from plexapi.server import PlexServer

from media_essentials_library.config import load_config
from media_essentials_library.models.plex import PlexEpisode, PlexLibrary, PlexShow


@cache
def get_plex_server() -> PlexServer:
    config = load_config()
    return PlexServer(config.server_url, config.token)


def reset_plex_server() -> None:
    get_plex_server.cache_clear()


def get_tv_show_libraries() -> list[PlexLibrary]:
    """
    Return all available tv show libraries.
    """
    libraries = []
    for section in get_plex_server().library.sections():
        section_type = getattr(section, "type", None)
        if section_type == "show":
            libraries.append(PlexLibrary(key=str(section.key), title=section.title))
    return sorted(libraries, key=lambda library: library.title.casefold())


def get_tv_shows(library_key: str) -> list[PlexShow]:
    """
    Return all shows in a selected Plex TV library.
    """
    library = get_plex_server().library.sectionByID(int(library_key))

    shows = []
    for show in library.all():
        shows.append(
            PlexShow(
                key=str(show.ratingKey),
                title=str(show.title),
                year=getattr(show, "year", None),
                season_count=int(getattr(show, "childCount", 0) or 0),
                episode_count=int(getattr(show, "leafCount", 0) or 0),
            )
        )

    return sorted(shows, key=lambda show: show.title.casefold())


def get_show_episodes(show_key: str) -> list[PlexEpisode]:
    """
    Return all episodes in a selected Plex show.
    """
    show = get_plex_server().fetchItem(int(show_key))

    episodes = []
    for episode in show.episodes():
        episodes.append(
            PlexEpisode(
                key=str(episode.ratingKey),
                season_number=getattr(episode, "seasonNumber", None),
                episode_number=getattr(episode, "episodeNumber", None),
                title=str(episode.title),
            )
        )

    return episodes
