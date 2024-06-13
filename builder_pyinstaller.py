import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name', 'EyeFit.exe',
    '--onefile',
    '--add-data', 'assets;assets'
])
