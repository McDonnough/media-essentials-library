from __future__ import annotations

from datetime import date

DATE_FORMAT_OPTIONS = {
    "iso": ("YYYY-MM-DD", "%Y-%m-%d"),
    "de": ("DD.MM.YYYY", "%d.%m.%Y")
}

DEFAULT_DATE_FORMAT = "iso"


def format_date(value: date | None, date_format: str) -> str:
    if value is None:
        return ""

    _, strftime_format = DATE_FORMAT_OPTIONS.get(
        date_format,
        DATE_FORMAT_OPTIONS[DEFAULT_DATE_FORMAT],
    )
    return value.strftime(strftime_format)

