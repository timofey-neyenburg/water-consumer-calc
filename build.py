import PyInstaller.__main__

with open(".env", "w") as f:
    f.write("MODE=build")

PyInstaller.__main__.run([
    'main.py',
    '--add-data=./water-calc-assets:./assets',
    '--add-data=./.env:.',
    '--hide-console=hide-early',
    '--clean',
    '--workpath=./build/temp',
    '--distpath=./build',
    '--noconfirm',
    '-n=waterconsumption-calc',
    '-i=./icon.ico',
])