import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    # '--onefile',
    '--add-data=./assets:./assets',
    '--hide-console=hide-early',
    '--clean',
    '--workpath=./build/temp',
    '--distpath=./build',
    '--noconfirm',
    '-n=waterconsumption-calc',
    '-i=./icon.ico',
])