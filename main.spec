# -*- mode: python -*-
a = Analysis(['server/main.py'],
             pathex=['/home/vasu/Work/pokemon_ai'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='main',
          debug=False,
          strip=None,
          upx=True,
          console=True )
dict_tree = Tree("data/", prefix="data")
coll = COLLECT(exe,
               a.binaries,
               dict_tree,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='main')
