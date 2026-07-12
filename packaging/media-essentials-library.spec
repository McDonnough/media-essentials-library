# -*- mode: python ; coding: utf-8 -*-

import tomllib
from importlib.metadata import PackageNotFoundError
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

spec_path = Path(SPECPATH).resolve()
project_root = spec_path if (spec_path / "src").exists() else spec_path.parent
src_path = project_root / "src"
generated_dir = project_root / "build" / "generated"
generated_dir.mkdir(parents=True, exist_ok=True)
version_file = generated_dir / "version.txt"
project_metadata = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
version_file.write_text(project_metadata["project"]["version"], encoding="utf-8")

datas = [
    (
        str(src_path / "media_essentials_library" / "assets" / "logo.txt"),
        "media_essentials_library/assets",
    ),
    (
        str(src_path / "media_essentials_library" / "locales"),
        "media_essentials_library/locales",
    ),
    (
        str(version_file),
        "media_essentials_library",
    ),
]
try:
    datas += copy_metadata("media-essentials-library")
except PackageNotFoundError:
    pass
hiddenimports = collect_submodules("keyring.backends")

a = Analysis(
    [str(project_root / "packaging" / "pyinstaller_entry.py")],
    pathex=[str(src_path)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="media-essentials-library",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
