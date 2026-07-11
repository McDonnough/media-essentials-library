# Media Essentials Library

A terminal UI for media library administration tasks.

## External translations

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

## Build

Build a standalone Windows executable with PyInstaller:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller .\packaging\media-essentials-library.spec --clean --noconfirm
```

The executable is written to:

```text
dist\media-essentials-library.exe
```
