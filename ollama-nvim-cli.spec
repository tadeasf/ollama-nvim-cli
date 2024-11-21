# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/tadeasfort/Documents/coding-projects/ollama-nvim-cli/src/ollama_nvim_cli/cli.py'],
    pathex=[],
    binaries=[],
    datas=[('src/ollama_nvim_cli', 'ollama_nvim_cli')],
    hiddenimports=['typer', 'rich', 'prompt_toolkit', 'httpx'],
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
    name='ollama-nvim-cli',
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
