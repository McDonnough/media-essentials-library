from __future__ import annotations

DEFAULT_LANGUAGE = "en"

LANGUAGE_OPTIONS = {
    "en": "English",
    "de": "Deutsch",
}

TRANSLATIONS = {
    "en": {
        "action.back": "Back",
        "action.quit": "Quit",
        "action.save": "Save",
        "action.scan": "Scan",
        "app.subtitle": "Media Essentials Library",
        "config.date_format": "Date Format",
        "config.language": "Language",
        "config.plex_server_settings": "Plex Server Settings",
        "config.plex_server_url_placeholder": "Plex server URL, e.g. http://localhost:32400",
        "config.plex_token_placeholder": "Plex token",
        "config.save_error": "Could not save Plex server settings: {error}",
        "config.saved": "Plex server settings saved to ",
        "config.title": "Media Essentials Library Settings",
        "missing.airdate": "Airdate",
        "missing.currently_scanning": "Currently scanning: {show_title}",
        "missing.episode": "Episode",
        "missing.episodes": "Episodes",
        "missing.found_for_show": "Found {count} missing episodes for {show_title}.",
        "missing.library": "Library",
        "missing.load_libraries_error": "Could not load Plex libraries: {error}",
        "missing.missing": "Missing",
        "missing.no_selected_show": "Could not determine selected show.",
        "missing.prepare_scan": "Preparing scan...",
        "missing.scan_complete": "Scan complete. Found {count} shows with missing episodes.",
        "missing.scan_error": "Could not scan library: {error}",
        "missing.scanned_progress": "Scanned {scanned_count} of {total_shows} shows.",
        "missing.select_library": "Select a library",
        "missing.select_library_before_scan": "Select a library before scanning.",
        "missing.scanning_library": "Scanning library: {library}",
        "missing.season": "Season",
        "missing.seasons": "Seasons",
        "missing.shows": "Shows",
        "missing.status": "Status",
        "missing.title": "Missing Episodes Finder",
        "missing.unaired": "Unaired",
        "missing.year": "Year",
        "start.missing_episode_finder": "Missing Episode Finder",
        "start.settings": "Settings",
        "start.tool_2": "Tool 2",
        "start.tool_3": "Tool 3",
        "start.welcome": (
            "Welcome to Media Essentials Library! Please select a tool to get started."
        ),
        "status.ready": "Ready",
        "table.episodes": "Episodes",
        "table.title": "Title",
    },
    "de": {
        "action.back": "Zurück",
        "action.quit": "Beenden",
        "action.save": "Speichern",
        "action.scan": "Durchsuchen",
        "app.subtitle": "Media Essentials Library",
        "config.date_format": "Datumsformat",
        "config.language": "Sprache",
        "config.plex_server_settings": "Plex-Server-Einstellungen",
        "config.plex_server_url_placeholder": "Plex-Server-URL, z. B. http://localhost:32400",
        "config.plex_token_placeholder": "Plex-Token",
        "config.save_error": "Plex-Server-Einstellungen konnten nicht gespeichert werden: {error}",
        "config.saved": "Plex-Server-Einstellungen gespeichert unter ",
        "config.title": "Media-Essentials-Library-Einstellungen",
        "missing.airdate": "Ausstrahlungsdatum",
        "missing.currently_scanning": "Aktuelle Suche: {show_title}",
        "missing.episode": "Episode",
        "missing.episodes": "Episoden",
        "missing.found_for_show": "{count} fehlende Episoden für {show_title} gefunden.",
        "missing.library": "Mediathek",
        "missing.load_libraries_error": "Plex-Mediatheken konnten nicht geladen werden: {error}",
        "missing.missing": "Fehlt",
        "missing.no_selected_show": "Ausgewählte Serie konnte nicht ermittelt werden.",
        "missing.prepare_scan": "Suche wird vorbereitet...",
        "missing.scan_complete": (
            "Suche abgeschlossen. {count} Serien mit fehlenden Episoden gefunden."
        ),
        "missing.scan_error": "Mediathek konnte nicht durchsucht werden: {error}",
        "missing.scanned_progress": "{scanned_count} von {total_shows} Serien durchsucht.",
        "missing.select_library": "Mediathek auswählen",
        "missing.select_library_before_scan": "Wählen Sie vor dem Scannen eine Mediathek aus.",
        "missing.scanning_library": "Mediathek wird durchsucht: {library}",
        "missing.season": "Staffel",
        "missing.seasons": "Staffeln",
        "missing.shows": "Serien",
        "missing.status": "Status",
        "missing.title": "Finder für fehlende Episoden",
        "missing.unaired": "Nicht ausgestrahlt",
        "missing.year": "Jahr",
        "start.missing_episode_finder": "Finder für fehlende Episoden",
        "start.settings": "Einstellungen",
        "start.tool_2": "Werkzeug 2",
        "start.tool_3": "Werkzeug 3",
        "start.welcome": "Willkommen bei Media Essentials Library! Wählen Sie ein Werkzeug aus.",
        "status.ready": "Bereit",
        "table.episodes": "Episoden",
        "table.title": "Titel",
    },
}


def get_language(language: str | None) -> str:
    if language in TRANSLATIONS:
        return language
    return DEFAULT_LANGUAGE


def t(key: str, language: str | None = None, **kwargs: object) -> str:
    selected_language = get_language(language)
    text = TRANSLATIONS[selected_language].get(key, TRANSLATIONS[DEFAULT_LANGUAGE][key])
    if kwargs:
        return text.format(**kwargs)
    return text
