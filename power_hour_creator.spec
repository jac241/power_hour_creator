# -*- mode: python -*-

block_cipher = None


a = Analysis(['power_hour_creator-runner.py'],
             pathex=['C:\\Users\\jac24\\git\\jac241\\power_hour_creator'],
             binaries=[],
             datas=[
                ('ext', 'ext'),
                ('power_hour_creator/db', 'power_hour_creator/db')],
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
