# Media Essentials Library

A terminal UI for media library administration tasks.

## Build

Build a standalone Windows executable with PyInstaller:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller .\packaging\media-essentials-library.spec --clean --noconfirm
```

The executable is written to:

```text
dist\media-essentials-library.exe
```
