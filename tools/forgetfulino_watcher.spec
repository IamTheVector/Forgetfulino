# PyInstaller spec for Forgetfulino Watcher & Decoder
# Build from library root: pyinstaller tools/forgetfulino_watcher.spec
# Output: dist/ForgetfulinoWatcher/ with .exe + DLLs (onedir = no "ordinale 380" / DLL errors)

import os

block_cipher = None
spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(spec_dir, 'forgetfulino_watcher_app.py')],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        (os.path.join(spec_dir, 'forgetfulino_generator.py'), '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'runpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ForgetfulinoWatcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ForgetfulinoWatcher',
)
