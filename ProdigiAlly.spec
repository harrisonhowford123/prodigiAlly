# ProdigiAlly.spec — fully functional build
# Run: python -m PyInstaller ProdigiAlly.spec

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

app_name = "Prodigi Ally - Standard Station"
icon_file = "MyAppIcon.ico"
images_dir = "images"

# --- MANIFEST (no leading newline or spaces!) ---
manifest = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity version="1.0.0.0" name="Prodigi Ally - Standard Station" />
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false" />
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>"""

# --- INCLUDE DATA ---
datas = []

# Include entire images directory
if os.path.isdir(images_dir):
    for root, _, files in os.walk(images_dir):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(root, ".")
            datas.append((src, rel))
else:
    print(f"WARNING: '{images_dir}' folder not found")

# Include icon
if os.path.exists(icon_file):
    datas.append((icon_file, "."))

# --- ANALYSIS ---
a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pynput', 'pynput.keyboard', 'pynput.mouse',
        'PIL.ImageTk', 'PIL.ImageFilter', 'PIL._tkinter_finder'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # hide console window
    icon=icon_file,
    manifest=manifest
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name=app_name
)
