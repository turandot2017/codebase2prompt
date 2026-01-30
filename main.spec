# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# 根据平台选择图标
if sys.platform == 'darwin':  # macOS
    icon_file = None  # macOS 使用 .icns，如果有可以指定
elif sys.platform == 'win32':  # Windows
    # 检查 logo.ico 是否存在
    if os.path.exists('logo.ico'):
        icon_file = 'logo.ico'
    else:
        icon_file = None
else:  # Linux
    icon_file = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='main',
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
    icon=icon_file,
)
