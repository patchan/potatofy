# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
from os.path import *
import sys
import win32com.client
import zipfile
import PyInstaller.config
os.path.expanduser

# https://stackoverflow.com/a/42056050
def zipdir(path, ziph):
    length = len(path)

    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        folder = root[length:] # path without "parent"
        for file in files:
            ziph.write(os.path.join(root, file), os.path.join(folder, file))


# pyinstaller build
PyInstaller.config.CONF['distpath'] = "./dist/potatofy_win"
a = Analysis(['potatofy.py'],
             pathex=['C:\\Users\\chanc\\Documents\\Projects\\potatofy'],
             binaries=[],
             datas=[('icons/Questrade.png', 'icons')],
             hiddenimports=['pkg_resources.py2_warn'],
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


# post-build script
shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut("./dist/potatofy_win/potatofy.lnk")
shortcut.Targetpath = abspath(abspath(".\dist\potatofy_win\potatofy\potatofy.exe"))
shortcut.save()

print("Creating zip")
os.chdir("./dist/")
zipf = zipfile.ZipFile('./potatofy.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('./potatofy_win/', zipf)
zipf.close()
print("Finished zip")
