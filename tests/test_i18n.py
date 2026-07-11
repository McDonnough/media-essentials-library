from media_essentials_library.i18n import (
    Locale,
    find_translation,
    get_language_chain,
    merge_locale_files,
    normalize_locale_tag,
)


def test_normalize_locale_tag_accepts_safe_custom_tags():
    assert normalize_locale_tag("GSW_CH") == "gsw-ch"
    assert normalize_locale_tag("de-CH") == "de-ch"


def test_normalize_locale_tag_rejects_empty_or_unsafe_tags():
    assert normalize_locale_tag("") is None
    assert normalize_locale_tag("../secret") is None
    assert normalize_locale_tag("de.ch") is None


def test_find_translation_uses_explicit_and_regional_fallbacks():
    locales = {
        "en": Locale("English", translations={"action.save": "Save"}),
        "de": Locale("Deutsch", translations={"action.save": "Speichern"}),
        "de-ch": Locale("Schwiizerduetsch", fallback="de", translations={}),
    }

    assert get_language_chain("de-ch", locales) == ["de-ch", "de", "en"]
    assert find_translation("action.save", "de-ch", locales) == "Speichern"
    assert find_translation("missing.key", "de-ch", locales) == "missing.key"


def test_merge_locale_files_ignores_invalid_files_and_merges_existing_locale(tmp_path):
    locales = {
        "en": Locale("English", translations={"action.save": "Save"}),
    }
    (tmp_path / "en.json").write_text(
        """
{
  "language_name": "English Custom",
  "translations": {
    "action.save": "Save now",
    "ignored": 123
  }
}
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "bad.name.json").write_text(
        """{"language_name": "Bad", "translations": {"x": "y"}}""",
        encoding="utf-8",
    )
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")

    merge_locale_files(locales, tmp_path.glob("*.json"))

    assert locales["en"].language_name == "English Custom"
    assert locales["en"].translations == {"action.save": "Save now"}
    assert "bad.name" not in locales
    assert "broken" not in locales
