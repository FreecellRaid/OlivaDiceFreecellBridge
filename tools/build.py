"""Build a standard OlivOS OPK (ZIP containing the plugin package)."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / 'dist' / 'OlivaDiceFreecellBridge.opk'
output.parent.mkdir(exist_ok=True)
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for file in sorted((root / 'OlivaDiceFreecellBridge').glob('*')):
        if file.is_file():
            archive.write(file, file.relative_to(root))
print(output)
