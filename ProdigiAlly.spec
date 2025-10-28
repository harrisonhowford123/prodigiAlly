# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files
import sys

block_cipher = None

# === Include all image assets and icon ===
datas = collect_data_files('.', includes=['images/*'])
datas += [('MyAppIcon.ico', '.')]

# === Request admin privileges on Windows ===
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
    with open("admin.manifest", "w", encoding="utf-8") as f:
        f.write(manifest)
else:
    manifest = None

# === Force working directory to your real script folder ===
# When running from the frozen app, this ensures all relative paths (like images/, logs/) still work.
runtime_hook_code = r"""
import os, sys
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Enable console-style logging for debugging compiled builds
import datetime, sys
log_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'ProdigiDebug.log')
sys.stdout = open(log_path, 'w', buffering=1)
sys.stderr = sys.stdout
print(f"[DEBUG] Application started at {datetime.datetime.now()}")
"""

hook_file = "runtime_hook_force_dir.py"
with open(hook_file, "w", encoding="utf-8") as f:
    f.write(runtime_hook_code)

# === Main build definition ===
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=['pynput.keyboard', 'PIL._tkinter_finder'],
    hookspath=[],
    runtime_hooks=[hook_file],  # Force correct working dir & logging
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Use console=True for debugging (shows terminal output)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ProdigiAlly',
    debug=True,  # more detailed logs
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # <<-- keeps the console visible so you can see debug prints
    icon='MyAppIcon.ico',
    uac_admin=True if sys.platform == 'win32' else False,
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
