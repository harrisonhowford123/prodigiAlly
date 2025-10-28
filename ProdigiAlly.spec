# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files
import sys

block_cipher = None

# === Include image assets and icon ===
datas = collect_data_files('.', includes=['images/*'])
datas += [('MyAppIcon.ico', '.')]

# === Administrator privilege manifest (Windows only) ===
if sys.platform == "win32":
    manifest = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
        <security>
            <requestedPrivileges>
                <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
            </requestedPrivileges>
        </security>
    </trustInfo>
</assembly>"""
    # Also save manifest to file for reference
    with open("admin.manifest", "w", encoding="utf-8") as f:
        f.write(manifest)
else:
    manifest = None

# === Core build configuration ===
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pynput.keyboard',     # For barcode listener
        'PIL._tkinter_finder', # Pillow + Tkinter integration
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ProdigiAlly',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app (no terminal)
    icon='MyAppIcon.ico',
    uac_admin=True if sys.platform == 'win32' else False,  # Request admin privileges
    manifest=manifest,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='ProdigiAlly'
)
