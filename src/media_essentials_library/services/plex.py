from functools import cache

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

from media_essentials_library.config import load_config
from media_essentials_library.models.plex import (
    PlexEpisode,
    PlexLibrary,
    PlexMediaItem,
    PlexServerResource,
    PlexShow,
)


@cache
def get_plex_server() -> PlexServer:
    config = load_config()
    return PlexServer(config.server_url, config.token)


def reset_plex_server() -> None:
    get_plex_server.cache_clear()


def connect_plex_server(server_url: str, token: str) -> PlexServer:
    """Connect to an explicitly configured Plex server."""
    return PlexServer(server_url, token)


def get_accessible_server_resources(
    token: str,
) -> tuple[dict[str, object], list[PlexServerResource]]:
    """Return Plex servers available to the account represented by ``token``.

    Resource objects retain the server-specific access token Plex issues for owned and shared
    servers. Calling their ``connect`` method is therefore preferable to sending the account token
    to a manually entered server URL.
    """
    account = MyPlexAccount(token=token)
    resource_objects = {
        str(resource.clientIdentifier): resource
        for resource in account.resources()
        if "server" in (getattr(resource, "provides", "") or "")
    }
    resources = [
        PlexServerResource(
            key=key,
            title=str(resource.name),
            owned=bool(getattr(resource, "owned", False)),
        )
        for key, resource in resource_objects.items()
    ]
    return resource_objects, sorted(
        resources,
        key=lambda resource: (not resource.owned, resource.title.casefold()),
    )


def connect_plex_resource(resource: object) -> PlexServer:
    """Connect to a discovered Plex resource using its resource-specific token."""
    return resource.connect()


def get_media_libraries(server: PlexServer) -> list[PlexLibrary]:
    """Return movie and TV libraries available on a Plex server."""
    libraries = [
        PlexLibrary(key=str(section.key), title=str(section.title), media_type=section.type)
        for section in server.library.sections()
        if getattr(section, "type", None) in {"movie", "show"}
    ]
    return sorted(libraries, key=lambda library: (library.media_type, library.title.casefold()))


def get_library_items(server: PlexServer, library_key: str) -> list[PlexMediaItem]:
    """Return matchable movie or show records from a Plex library."""
    section = server.library.sectionByID(int(library_key))
    media_type = str(section.type)
    items = []
    for item in section.all():
        guids = tuple(
            sorted(
                str(guid.id).casefold()
                for guid in (getattr(item, "guids", None) or [])
                if getattr(guid, "id", None)
            )
        )
        items.append(
            PlexMediaItem(
                key=str(item.ratingKey),
                title=str(item.title),
                year=getattr(item, "year", None),
                media_type=media_type,
                guids=guids,
                web_url=str(item.getWebURL()),
            )
        )
    return sorted(items, key=lambda item: (item.title.casefold(), item.year or 0))


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
