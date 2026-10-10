"""Build an OlivOS OPK and a versioned forum release ZIP."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / 'dist' / 'OlivaDiceFreecellBridge.opk'
output.parent.mkdir(exist_ok=True)
package = root / 'OlivaDiceFreecellBridge'
version = json.loads((package / 'app.json').read_text(encoding='utf-8'))['version']
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for file in sorted((root / 'OlivaDiceFreecellBridge').glob('*')):
        if file.is_file():
            archive.write(file, file.relative_to(root))
    archive.write(root / 'LICENSE', 'OlivaDiceFreecellBridge/LICENSE')
print(output)
release = output.parent / ('OlivaDiceFreecellBridge-%s.zip' % version)
with ZipFile(release, 'w', ZIP_DEFLATED) as archive:
    archive.write(output, output.name)
    for name in ['README.md', 'config.example.json', 'LICENSE']:
        archive.write(root / name, name)
print(release)
