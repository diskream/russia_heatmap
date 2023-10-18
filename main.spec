# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('app\\map_data\\russia_regions.parquet', 'app\\map_data'), ('app\\map_data\\russia_regions.geojson', 'app\\map_data')],
    hiddenimports=['fiona._shim', 'pyarrow.vendored.version'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='russia_heatmap',
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
