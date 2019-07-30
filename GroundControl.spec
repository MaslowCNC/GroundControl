# -*- mode: python -*-

from kivy.deps import sdl2, glew

block_cipher = None


a = Analysis(['C:\\Users\\Jesse.Wortman\\Documents\\Maslow\\Holey Calibration_v1.26\\GroundControl-master\\main.py'],
             pathex=['C:\\Users\\Jesse.Wortman\\Documents\\Maslow\\Holey Calibration_v1.26\\GroundControl-master'],
             binaries=None,
             datas=None,
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
          exclude_binaries=True,
          name='GroundControl',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe, Tree('C:\\Users\\Jesse.Wortman\\Documents\\Maslow\\Holey Calibration_v1.26\\GroundControl-master'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='GroundControl')
