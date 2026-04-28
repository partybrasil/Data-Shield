# PyInstaller spec file for Data-Shield
# Build with: pyinstaller datashield.spec

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

a = Analysis(
    ["src/datashield/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("src/datashield/patterns/yara_rules", "datashield/patterns/yara_rules"),
        ("src/datashield/gui/resources", "datashield/gui/resources"),
        ("src/datashield/i18n", "datashield/i18n"),
    ],
    hiddenimports=[
        "PySide6",
        "cryptography",
        "bcrypt",
        "sqlalchemy",
        "watchdog",
        "yara",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="datashield",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="src/datashield/gui/resources/icons/app.ico" if Path("src/datashield/gui/resources/icons/app.ico").exists() else None,
)

# For console version (CLI):
# exe_console = EXE(...)  # Same as above but with console=True
