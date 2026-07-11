from datetime import date

from media_essentials_library.formatting import format_date


def test_format_date_supports_known_formats():
    value = date(2026, 7, 11)

    assert format_date(value, "iso") == "2026-07-11"
    assert format_date(value, "de") == "11.07.2026"


def test_format_date_handles_empty_and_unknown_format():
    assert format_date(None, "iso") == ""
    assert format_date(date(2026, 7, 11), "unknown") == "2026-07-11"
