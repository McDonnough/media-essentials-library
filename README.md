# Media Essentials Library

[![CI](https://github.com/McDonnough/media-essentials-library/actions/workflows/ci.yml/badge.svg)](https://github.com/McDonnough/media-essentials-library/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/McDonnough/media-essentials-library)](https://github.com/McDonnough/media-essentials-library/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-46a2f1.svg)](https://docs.astral.sh/ruff/)

A terminal UI for media library administration tasks.

Media Essentials Library is a keyboard-first toolbox for small, repeatable media-library
maintenance tasks. It is intended to collect practical workflows that are easier to run from a
focused terminal interface than from a mix of scripts, spreadsheets, and manual checks.

## Status

This project is early and currently focused on personal media administration workflows. It is
usable, but the feature set is intentionally small:

- run focused media-library checks from a terminal UI
- find missing episodes in a TV library
- save non-secret preferences such as date format and language
- switch between bundled English and German translations
- load custom external translations

Running from source should work on platforms supported by Python, Textual, and keyring. Automated
release builds currently produce a Windows executable.

## Features

### Missing Episode Finder

Missing Episode Finder compares the episodes in a TV library with external metadata and reports
episodes that appear to be absent from the library. It also marks future or unknown-airdate episodes
as unaired, so they can be distinguished from episodes that should already be available.

The current implementation reads TV libraries from Plex and compares them against TVMaze metadata.
To use it, configure:

- a Plex server URL, for example `http://127.0.0.1:32400`
- a Plex token

The app can then connect to the configured Plex server, list TV libraries and shows, and scan a
selected library for missing episodes.

Do not paste Plex tokens into bug reports, screenshots, logs, commits, or pull requests. If a token is
accidentally exposed, revoke or rotate it before sharing anything publicly.

## Download and Installation

Windows release builds are published on the
[GitHub Releases page](https://github.com/McDonnough/media-essentials-library/releases). Download
the latest `media-essentials-library-*-windows.exe` asset from the newest release and run it from a
terminal.

You can also install and run the project from source.

Requirements:

- Python 3.11 or newer

Create a virtual environment and install the project:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

On Unix-like shells, use the virtual environment commands for your platform and install with:

```sh
python -m pip install -e .
```

Run the terminal UI:

```powershell
.\.venv\Scripts\media-essentials-library.exe
```

Or, on Unix-like shells:

```sh
media-essentials-library
```

## Configuration

Use the Settings screen in the app to configure available workflows and preferences. Secret values
are stored through the operating system secret store with `keyring`; regular config files store
non-secret preferences such as date format and language.

## Customization

Translations are loaded from bundled locale files first, then from external locale files in the
application config directory. On Windows, the external translations folder is usually at:

```text
%LOCALAPPDATA%\Media Essentials Library\locales
```

Create that `locales` folder if it does not exist, then add one JSON file per locale. The file name
is the locale tag that will be stored in settings, for example:

```text
gsw.json
```

Locale tags may contain letters, numbers, underscores, or hyphens. New valid locale files are
discovered automatically when the Settings screen is opened or reopened. The tags are not checked
against a locale standard, so custom or uncommon tags can be used too.

Each locale file must include a display name and a `translations` object:

```json
{
  "language_name": "Schwiizerduetsch",
  "fallback": "de",
  "translations": {
    "action.back": "Zrugg",
    "action.save": "Speichere",
    "status.ready": "Bereit"
  }
}
```

| Key | Required | Example | Description |
| --- | --- | --- | --- |
| `language_name` | Yes | `"Schwiizerduetsch"` | Display name shown in the Settings language selector. |
| `fallback` | No | `"de"` | Locale to use when this file does not define a translation key. |
| `translations` | Yes | `{ "action.save": "Speichere" }` | Translation keys and their translated text. |

## Project Maintenance

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and
[SECURITY.md](SECURITY.md) for security reporting.

### Development

Install development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run checks:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

The project currently uses the `pushingkarmaorg/python-plexapi` GitHub fork of `plexapi`. That keeps
the dependency source visible, but it also means installs need GitHub access. If this fork is no
longer required, prefer a normal PyPI dependency or pin the Git dependency to a commit/tag before a
public release.

### Build

Build a standalone Windows executable with PyInstaller:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller .\packaging\media-essentials-library.spec --clean --noconfirm
```

The executable is written to:

```text
dist\media-essentials-library.exe
```

### Release

Releases are tag-driven. Update the project version in `pyproject.toml`, commit the change, then
create and push a matching semantic version tag:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

The GitHub workflow builds the Windows executable and creates a release only when a tag like
`v1.2.3` is pushed. The tag version must match the `pyproject.toml` version.
