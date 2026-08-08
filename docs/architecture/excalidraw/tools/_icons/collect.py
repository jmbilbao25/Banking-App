"""Fetch every icon the diagrams need into ./flat/<key>.svg.

Self-contained: downloads the official Microsoft Azure architecture icon set if
it is not already present, then pulls the CNCF/vendor marks. Exits non-zero if
anything cannot be resolved -- a diagram should fail to build rather than fall
back to a placeholder.
"""
import io
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import AZURE, EXTERNAL, BRAND

HERE = os.path.dirname(os.path.abspath(__file__))
FLAT = os.path.join(HERE, "flat")
AZURE_ROOT = os.path.join(HERE, "Azure_Public_Service_Icons")

# Official set, linked from https://learn.microsoft.com/en-us/azure/architecture/icons/
AZURE_ZIP_URL = "https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V24.zip"

os.makedirs(FLAT, exist_ok=True)


def ensure_azure_set() -> None:
    if os.path.isdir(AZURE_ROOT):
        return
    print(f"downloading official Azure icon set\n  {AZURE_ZIP_URL}")
    try:
        with urllib.request.urlopen(AZURE_ZIP_URL, timeout=180) as resp:
            blob = resp.read()
    except Exception as exc:
        sys.exit(f"ERROR: could not download the Azure icon set: {exc}\n"
                 f"Download it manually from "
                 f"https://learn.microsoft.com/en-us/azure/architecture/icons/ "
                 f"and extract it into {HERE}")
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        zf.extractall(HERE)
    print(f"  extracted {len(blob) // 1024} KB")


ensure_azure_set()

# index every svg in the extracted Azure set by basename
index = {}
for root, _dirs, files in os.walk(AZURE_ROOT):
    for fn in files:
        if fn.endswith(".svg"):
            index.setdefault(fn, os.path.join(root, fn))

missing_azure = []
for key, fname in AZURE.items():
    src = index.get(fname)
    if not src:
        missing_azure.append((key, fname))
        continue
    shutil.copyfile(src, os.path.join(FLAT, key + ".svg"))

missing_ext = []
for key, url in EXTERNAL.items():
    dest = os.path.join(FLAT, key + ".svg")
    if os.path.exists(dest) and os.path.getsize(dest) > 80:
        continue
    r = subprocess.run(["curl", "-sfL", "--max-time", "40", "-o", dest, url],
                       capture_output=True)
    if r.returncode != 0 or not os.path.exists(dest) or os.path.getsize(dest) < 80:
        missing_ext.append((key, url))
        if os.path.exists(dest):
            os.remove(dest)

# colourise monochrome simple-icons marks to their documented brand colour
for key, colour in BRAND.items():
    fp = os.path.join(FLAT, key + ".svg")
    if not os.path.exists(fp):
        continue
    with open(fp, "r", encoding="utf-8") as fh:
        svg = fh.read()
    if 'fill="' + colour + '"' in svg:
        continue
    svg = svg.replace("<svg ", '<svg fill="%s" ' % colour, 1)
    with open(fp, "w", encoding="utf-8") as fh:
        fh.write(svg)

print(f"AZURE    {len(AZURE) - len(missing_azure)} / {len(AZURE)}")
for k, f in missing_azure:
    print("   MISSING AZURE:", k, "->", f)
print(f"EXTERNAL {len(EXTERNAL) - len(missing_ext)} / {len(EXTERNAL)}")
for k, u in missing_ext:
    print("   MISSING EXT:", k, "->", u)

have = sorted(f[:-4] for f in os.listdir(FLAT) if f.endswith(".svg"))
print(f"\nTOTAL {len(have)} icons in {FLAT}")

if missing_azure or missing_ext:
    sys.exit("ERROR: unresolved icons -- refusing to continue with placeholders")
