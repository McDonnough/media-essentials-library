from datetime import date

from media_essentials_library.features import missing_episodes as missing_episodes_module
from media_essentials_library.models.metadata import MetadataEpisode
from media_essentials_library.models.plex import PlexEpisode


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
