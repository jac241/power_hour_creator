# -*- mode: python -*-

block_cipher = None

import os
import platform
from distutils.sysconfig import get_python_lib

pathex = [os.getcwd()]

options = {
  'Windows': 'ffmpeg-3.2.2-win32-static',
  'Darwin': 'mac'
}
ext_dir = 'ext/' + options.get(platform.system())

if platform.system() == 'Windows':
    pathex = pathex + [
        get_python_lib() + '\\PyQt5\\Qt\\bin',
        "C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86"
    ]

a = Analysis(['power_hour_creator-runner.py'],
             pathex=pathex,
             binaries=[],
             datas=[
                (ext_dir, ext_dir),
                ('power_hour_creator/db', 'power_hour_creator/db'),
                ('assets', 'assets')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='power_hour_creator',
          debug=False,
          strip=False,
          upx=True,
          console=False )

app = BUNDLE(exe,
             name='Power Hour Creator.app',
             icon=None,
             bundle_identifier=None)

folder_exe = EXE(pyz,
                 a.scripts,
                 exclude_binaries=True,
                 name='power_hour_creator',
                 debug=False,
                 strip=False,
                 upx=True,
                 console=False )

coll = COLLECT(folder_exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Power Hour Creator')
