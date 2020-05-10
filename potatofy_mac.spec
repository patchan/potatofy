# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
from os.path import expanduser
import os
import zipfile
os.path.expanduser


def zipdir(path, ziph, sub_folder=""):
    length = len(path)
    print(os.listdir(path))
    for root, dirs, files in os.walk(path):
        folder = root[length:] # path without "parent"
        if sub_folder != "":
            print(f"before{folder}")
            folder = sub_folder + folder
            print(f"after{folder}")
        for file in files:
            ziph.write(os.path.join(root, file), os.path.join(folder, file))


a = Analysis(['potatofy.py'],
             pathex=['.'],
             binaries=[('/System/Library/Frameworks/Tk.framework/Tk', 'tk'), ('/System/Library/Frameworks/Tcl.framework/Tcl', 'tcl')],
             datas=[('icons/Questrade.png', 'icons')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='potatofy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='potatofy')
app = BUNDLE(coll,
               name='potatofy.app',
               icon=None,
               bundle_identifier=None,
               info_plist={
                 'NSPrincipalClass': 'NSApplication'
               })


print("Creating zip")
zipf = zipfile.ZipFile('./Circleguard_osx.app.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('./dist/Circleguard.app', zipf, "./Circleguard.app")
zipf.close()
print("Moving zip")
os.rename("./Circleguard_osx.app.zip", "./dist/Circleguard_osx.app.zip")
print("Finished zip")