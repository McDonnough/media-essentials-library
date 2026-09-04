from datetime import date

from media_essentials_library.features import missing_episodes as missing_episodes_module
from media_essentials_library.models.metadata import MetadataEpisode, MetadataSource
from media_essentials_library.models.plex import PlexEpisode, PlexShow


def test_find_missing_episodes_ignores_existing_episodes(monkeypatch):
    monkeypatch.setattr(
        missing_episodes_module,
        "get_expected_episodes",
        lambda show_title: [
            MetadataEpisode("1", 1, 1, "Pilot", date(2026, 1, 1)),
            MetadataEpisode("2", 1, 2, "Second", date(2026, 1, 8)),
        ],
    )

    missing = missing_episodes_module.find_missing_episodes(
        "Example Show",
        [PlexEpisode("plex-1", 1, 1, "Pilot")],
        today=date(2026, 7, 11),
    )

    assert [episode.title for episode in missing] == ["Second"]
    assert missing[0].is_unaired is False


def test_find_missing_episodes_marks_future_and_unknown_airdates_as_unaired(monkeypatch):
    monkeypatch.setattr(
        missing_episodes_module,
        "get_expected_episodes",
        lambda show_title: [
            MetadataEpisode("1", 1, 1, "Future", date(2026, 7, 12)),
            MetadataEpisode("2", 1, 2, "Unknown", None),
        ],
    )

    missing = missing_episodes_module.find_missing_episodes(
        "Example Show",
        [],
        today=date(2026, 7, 11),
    )

    assert [episode.is_unaired for episode in missing] == [True, True]


def test_find_missing_episodes_preserves_metadata_source(monkeypatch):
    source = MetadataSource("Example provider", "https://metadata.example/shows/123")
    monkeypatch.setattr(
        missing_episodes_module,
        "get_expected_episodes",
        lambda show_title: [
            MetadataEpisode(
                "1",
                1,
                1,
                "Pilot",
                date(2026, 1, 1),
                source,
            )
        ],
    )

    missing = missing_episodes_module.find_missing_episodes("Example Show", [])

    assert missing[0].metadata_source == source


def test_scan_exposes_metadata_source_for_show(monkeypatch):
    show = PlexShow("plex-show", "Example Show", 2026, 1, 0)
    source = MetadataSource("Example provider", "https://metadata.example/shows/123")
    monkeypatch.setattr(missing_episodes_module, "get_tv_shows", lambda library_key: [show])
    monkeypatch.setattr(missing_episodes_module, "get_show_episodes", lambda show_key: [])
    monkeypatch.setattr(
        missing_episodes_module,
        "get_expected_episodes",
        lambda show_title: [MetadataEpisode("1", 1, 1, "Pilot", date(2026, 1, 1), source)],
    )

    results = missing_episodes_module.scan_library_for_missing_episodes("library")

    assert results[0].metadata_source == source
