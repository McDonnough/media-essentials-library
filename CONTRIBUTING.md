# Contributing

Thanks for taking a look at Media Essentials Library. The project is small, so focused changes are
the easiest to review and merge.

## Development setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run the checks before opening a pull request:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

## Pull requests

- Keep changes focused on one bug, feature, or cleanup.
- Add or update tests for behavior changes.
- Update `README.md` when user-facing behavior changes.
- Avoid committing generated files from `build/`, `dist/`, caches, or virtual environments.
- Do not include tokens, server credentials, private URLs, or personal library data in commits,
  screenshots, logs, issues, or pull requests.

## Translations

Bundled translations live in `src/media_essentials_library/locales`. External translation files are
also supported for local customization; see `README.md` for the expected JSON structure.
