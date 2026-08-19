"""
Pull brand assets out of the TechStart LinkedIn banner committed to the repo.

The banner background is pale grey network art; the EastWest lockup is the only
strongly saturated thing in the top-left. So we threshold on saturation to find
the lockup's true bounding box rather than guessing pixel coordinates.
"""
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/projects/sandbox/Banking-App/docs/LinkedInBanner_Revised (2).png")
OUT = Path("/projects/sandbox/deckbuild/assets")
OUT.mkdir(parents=True, exist_ok=True)

banner = Image.open(SRC).convert("RGB")
print(f"banner: {banner.size}")

# full banner, kept as-is for use as a title hero
banner.save(OUT / "techstart-banner.png", optimize=True)

# ── locate the lockup in the top-left ──
search = banner.crop((0, 0, 1500, 620))
hsv = np.asarray(search.convert("HSV")).astype(np.int16)
sat = hsv[:, :, 1]
val = hsv[:, :, 2]

mask = (sat > 90) & (val > 45)
ys, xs = np.where(mask)
if len(xs) == 0:
    raise SystemExit("no saturated pixels found — check the crop window")

pad = 10
x0 = max(int(xs.min()) - pad, 0)
x1 = min(int(xs.max()) + pad, search.width)
y0 = max(int(ys.min()) - pad, 0)
y1 = min(int(ys.max()) + pad, search.height)
print(f"lockup bbox: ({x0}, {y0}) -> ({x1}, {y1})  size={x1-x0}x{y1-y0}  ratio={(x1-x0)/(y1-y0):.3f}")

logo = banner.crop((x0, y0, x1, y1))

# drop the faint network lines behind the lockup: anything low-saturation
# becomes pure white, so the logo sits cleanly on a white slide
arr = np.asarray(logo.convert("RGB")).astype(np.int16)
lhsv = np.asarray(logo.convert("HSV")).astype(np.int16)
flat = (lhsv[:, :, 1] < 60) & (lhsv[:, :, 2] > 150)
arr[flat] = [255, 255, 255]
Image.fromarray(arr.astype(np.uint8)).save(OUT / "eastwest-logo.png", optimize=True)

# white knockout of the same lockup, for use on the purple footer
w = np.asarray(logo.convert("HSV")).astype(np.int16)
solid = (w[:, :, 1] > 90) & (w[:, :, 2] > 45)
rgba = np.zeros((logo.height, logo.width, 4), dtype=np.uint8)
rgba[solid] = [255, 255, 255, 255]
Image.fromarray(rgba, mode="RGBA").save(OUT / "eastwest-logo-white.png", optimize=True)

for f in sorted(OUT.glob("*.png")):
    im = Image.open(f)
    print(f"  {f.name:28s} {im.size[0]}x{im.size[1]}  ratio={im.size[0]/im.size[1]:.3f}")
