import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name', 'pyinstaller_build.exe',
    '--onefile',
    '--add-data', 'assets;assets'
])
