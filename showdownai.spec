# -*- mode: python -*-
a = Analysis(['server/showdownbot.py'],
             pathex=['/home/vasu/Work/pokemon_ai'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='showdownbot',
          debug=False,
          strip=None,
          upx=True,
          console=True )
dict_tree = Tree("data/", prefix="data")
static_tree = Tree("server/static/", prefix="static")
template_tree = Tree("server/templates/", prefix="templates")
selenium_tree = Tree("venv/lib/python2.7/site-packages/selenium-2.44.0-py2.7.egg/selenium/", prefix="selenium")
teams_tree = Tree("empty_teams/", prefix="teams")
lib_tree = Tree("lib/", prefix="lib")
coll = COLLECT(exe,
               a.binaries,
               dict_tree,
               static_tree,
               template_tree,
               selenium_tree,
               teams_tree,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='showdownai')
