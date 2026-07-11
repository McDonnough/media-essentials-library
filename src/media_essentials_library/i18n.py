from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Any

from media_essentials_library.paths import get_app_config_dir

DEFAULT_LANGUAGE = "en"
LOCALES_DIR_NAME = "locales"
LOCALE_TAG_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


@dataclass
class Locale:
    language_name: str
    fallback: str | None = None
    translations: dict[str, str] = field(default_factory=dict)


def get_external_locales_dir() -> Path:
    return get_app_config_dir() / LOCALES_DIR_NAME


def get_language(language: str | None) -> str:
    normalized_language = normalize_locale_tag(language)
    if normalized_language in load_locales():
        return normalized_language
    return DEFAULT_LANGUAGE


def get_language_options() -> list[tuple[str, str]]:
    locales = load_locales()
    options = [
        (locale.language_name, language)
        for language, locale in locales.items()
        if language != DEFAULT_LANGUAGE
    ]
    return [(locales[DEFAULT_LANGUAGE].language_name, DEFAULT_LANGUAGE), *sorted(options)]


def t(key: str, language: str | None = None, **kwargs: object) -> str:
    locales = load_locales()
    selected_language = get_language(language)
    text = find_translation(key, selected_language, locales)
    if kwargs:
        return text.format(**kwargs)
    return text


def load_locales() -> dict[str, Locale]:
    locales = load_bundled_locales()
    external_locales_dir = get_external_locales_dir()
    if external_locales_dir.exists():
        merge_locale_files(locales, external_locales_dir.glob("*.json"))

    if DEFAULT_LANGUAGE not in locales:
        raise RuntimeError(f"Default locale {DEFAULT_LANGUAGE!r} is not available.")
    return locales


def load_bundled_locales() -> dict[str, Locale]:
    locales: dict[str, Locale] = {}
    bundled_locales = files("media_essentials_library").joinpath(LOCALES_DIR_NAME)
    merge_locale_files(locales, bundled_locales.iterdir())
    return locales


def merge_locale_files(locales: dict[str, Locale], locale_files: Any) -> None:
    for locale_file in locale_files:
        locale_file_name = getattr(locale_file, "name", Path(str(locale_file)).name)
        locale_path = Path(locale_file_name)
        if locale_path.suffix != ".json":
            continue

        language = normalize_locale_tag(locale_path.stem)
        if language is None:
            continue

        locale = parse_locale_file(locale_file)
        if locale is None:
            continue

        existing_locale = locales.get(language)
        if existing_locale is None:
            locales[language] = locale
            continue

        if locale.language_name:
            existing_locale.language_name = locale.language_name
        if locale.fallback:
            existing_locale.fallback = locale.fallback
        existing_locale.translations.update(locale.translations)


def parse_locale_file(locale_file: Any) -> Locale | None:
    try:
        data = json.loads(locale_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    language_name = data.get("language_name")
    translations = data.get("translations")
    if not isinstance(language_name, str) or not isinstance(translations, dict):
        return None

    fallback = normalize_locale_tag(data.get("fallback"))
    return Locale(
        language_name=language_name,
        fallback=fallback,
        translations={
            str(key): value
            for key, value in translations.items()
            if isinstance(value, str)
        },
    )


def find_translation(key: str, language: str, locales: dict[str, Locale]) -> str:
    for candidate_language in get_language_chain(language, locales):
        locale = locales[candidate_language]
        if key in locale.translations:
            return locale.translations[key]
    return key


def get_language_chain(language: str, locales: dict[str, Locale]) -> list[str]:
    chain = []
    seen = set()
    current_language: str | None = language

    while current_language and current_language in locales and current_language not in seen:
        chain.append(current_language)
        seen.add(current_language)

        fallback = locales[current_language].fallback
        if fallback:
            current_language = fallback
        elif "-" in current_language:
            current_language = current_language.rsplit("-", 1)[0]
        else:
            current_language = None

    if DEFAULT_LANGUAGE not in seen:
        chain.append(DEFAULT_LANGUAGE)
    return chain


def normalize_locale_tag(language: object) -> str | None:
    if not isinstance(language, str) or not language:
        return None
    if not LOCALE_TAG_PATTERN.fullmatch(language):
        return None
    return language.replace("_", "-").lower()
