from media_essentials_library.services.updates import (
    ReleaseInfo,
    check_for_update,
    is_newer_version,
    parse_release_version,
)


def test_parse_release_version_accepts_release_tags():
    assert str(parse_release_version("v1.2.3")) == "1.2.3"
    assert str(parse_release_version("1.2")) == "1.2"
    assert str(parse_release_version("1")) == "1"


def test_parse_release_version_accepts_dynamic_versions():
    assert str(parse_release_version("0.1.1.dev3+g4a73272.dirty")) == (
        "0.1.1.dev3+g4a73272.dirty"
    )


def test_parse_release_version_rejects_unknown_formats():
    assert parse_release_version("release-1.2.3") is None
    assert parse_release_version("1.two.3") is None


def test_is_newer_version_compares_semantic_versions():
    assert is_newer_version("v1.2.4", "1.2.3")
    assert is_newer_version("v1.3.0", "1.2.9")
    assert not is_newer_version("v1.2.3", "1.2.3")
    assert not is_newer_version("v1.2.2", "1.2.3")


def test_is_newer_version_handles_dynamic_versions():
    assert is_newer_version("v0.1.0", "0.1.0.dev3+g4a73272")
    assert not is_newer_version("v0.1.0", "0.1.1.dev3+g4a73272.dirty")


def test_check_for_update_returns_release_when_newer():
    update = check_for_update(
        current_version="1.2.3",
        latest_release=ReleaseInfo(version="v1.3.0", url="https://example.test/release"),
    )

    assert update is not None
    assert update.current_version == "1.2.3"
    assert update.latest_version == "v1.3.0"
    assert update.url == "https://example.test/release"


def test_check_for_update_ignores_current_or_older_release():
    assert (
        check_for_update(
            current_version="1.2.3",
            latest_release=ReleaseInfo(version="v1.2.3", url="https://example.test/release"),
        )
        is None
    )
