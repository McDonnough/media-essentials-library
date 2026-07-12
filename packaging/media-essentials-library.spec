# -*- mode: python ; coding: utf-8 -*-

import re
import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

PACKAGE_NAME = "media-essentials-library"


def get_build_version(project_root):
    try:
        from setuptools_scm import get_version

        return get_version(root=project_root, tag_regex=r"^v(?P<version>.*)$")
    except (ImportError, LookupError):
        pass

    try:
        description = subprocess.check_output(
            ["git", "describe", "--tags", "--long", "--dirty", "--abbrev=7"],
            cwd=project_root,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        try:
            return version(PACKAGE_NAME)
        except PackageNotFoundError:
            raise RuntimeError("Could not resolve build version.") from None
    else:
        description_match = re.fullmatch(
            r"(?P<tag>.+)-(?P<distance>\d+)-g(?P<commit>[0-9a-f]+)(?P<dirty>-dirty)?",
            description,
        )
        if description_match is None:
            raise RuntimeError(f"Could not parse Git version description: {description}")

        tag = description_match.group("tag")
        distance = description_match.group("distance")
        commit = f"g{description_match.group('commit')}"
        base_version = tag.removeprefix("v")
        if distance == "0":
            return base_version

        dirty_suffix = ".dirty" if description_match.group("dirty") else ""
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", base_version)
        if match is None:
            return f"{base_version}.dev{distance}+{commit}{dirty_suffix}"

        major, minor, patch = match.groups()
        next_patch_version = f"{major}.{minor}.{int(patch) + 1}"
        return f"{next_patch_version}.dev{distance}+{commit}{dirty_suffix}"


spec_path = Path(SPECPATH).resolve()
project_root = spec_path if (spec_path / "src").exists() else spec_path.parent
src_path = project_root / "src"
generated_dir = project_root / "build" / "generated"
generated_dir.mkdir(parents=True, exist_ok=True)
version_file = generated_dir / "version.txt"
version_file.write_text(get_build_version(project_root), encoding="utf-8")

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
    datas += copy_metadata(PACKAGE_NAME)
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
