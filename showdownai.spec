# -*- mode: python -*-
a = Analysis(['server/showdownai.py'],
             pathex=['/home/vasu/Work/pokemon_ai'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='showdownai',
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
               name='showdownai')
