# -*- mode: python -*-

block_cipher = None

import os
import platform

pathex = os.getcwd()

options = {
  'Windows': 'ffmpeg-3.2.2-win32-static',
  'Darwin': 'mac'
}
ext_dir = 'ext/' + options.get(platform.system())

a = Analysis(['power_hour_creator-runner.py'],
             pathex=[pathex],
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
             name='power_hour_creator.app',
             icon=None,
             bundle_identifier=None)
