# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['server.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        # 包含 ckjm jar 文件
        ('ckjm-1.9.jar', '.'),
        # 包含 skill 文件
        ('debt-visualizer', 'debt-visualizer'),
    ],
    hiddenimports=[
        'mcp',
        'mcp.server',
        'mcp.server.stdio',
        'mcp.types',
        'lizard',
        'radon',
        'radon.complexity',
        'git',
        'git.repo',
        'requests',
        'xml.etree.ElementTree',
        # 本地模块
        'models',
        'utils',
        'tools.complexity',
        'tools.smells',
        'tools.coverage',
        'tools.prioritize',
        'tools.roadmap',
        'tools.sonarqube',
        'tools.ai_suggestions',
        'analyzers.git_analyzer',
        'analyzers.generic_lizard',
        'analyzers.python_radon',
        'analyzers.java_ckjm',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tech-debt-mcp',
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