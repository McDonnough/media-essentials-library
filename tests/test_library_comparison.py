from media_essentials_library.features.library_comparison import find_library_duplicates
from media_essentials_library.models.plex import PlexMediaItem
from media_essentials_library.screens.library_comparison import LibraryComparisonScreen


def item(key, title, year, media_type="movie", guids=(), web_url=""):
    return PlexMediaItem(key, title, year, media_type, guids, web_url)


def test_matches_items_by_provider_guid_even_when_titles_differ():
    duplicates = find_library_duplicates(
        [item("a", "Localized title", 1999, guids=("imdb://tt123",))],
        [item("b", "Original title", 1999, guids=("imdb://tt123",))],
    )

    assert [(match.first.key, match.second.key, match.matched_by) for match in duplicates] == [
        ("a", "b", "GUID")
    ]


def test_falls_back_to_normalized_title_year_and_type():
    duplicates = find_library_duplicates(
        [item("a", "Spider-Man", 2002)],
        [item("b", "spider man", 2002)],
    )

    assert len(duplicates) == 1
    assert duplicates[0].matched_by == "title + year"


def test_does_not_match_remakes_or_different_media_types():
    first = [item("a", "The Thing", 1982), item("s", "Fargo", 2014, "show")]
    second = [item("b", "The Thing", 2011), item("m", "Fargo", 2014, "movie")]

    assert find_library_duplicates(first, second) == []


def test_does_not_use_title_fallback_when_year_is_unknown():
    assert find_library_duplicates(
        [item("a", "Ambiguous", None)],
        [item("b", "Ambiguous", None)],
    ) == []


def test_friendly_error_strips_plex_html_response():
    error = RuntimeError("(401) unauthorized; <html><body>Unauthorized</body></html>")

    assert LibraryComparisonScreen._friendly_error(error) == "(401) unauthorized"


def test_item_link_contains_plex_web_url():
    media = item("a", "Example", 2026, web_url="https://app.plex.tv/details/example")

    link = LibraryComparisonScreen._item_link(media)

    assert str(link) == "Example"
    assert "https://app.plex.tv/details/example" in str(link.style)


def test_match_labels_are_localized_in_german():
    screen = LibraryComparisonScreen()
    screen.language = "de"

    assert screen._match_label("GUID") == "GUID"
    assert screen._match_label("title + year") == "Titel + Jahr"
