"""Make review-sized images from a rendered PNG.

Usage:
  uv run python view.py <file.png> full            -> <file>.view.png  (<=1900px wide)
  uv run python view.py <file.png> grid 2 2        -> tiles <file>.r0c0.png ...
  uv run python view.py <file.png> crop x y w h    -> <file>.crop.png (source px)
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

MAX = 1900


def fit(im: Image.Image, cap: int = MAX) -> Image.Image:
    if max(im.size) <= cap:
        return im
    r = cap / max(im.size)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)


def main() -> None:
    src = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    im = Image.open(src).convert("RGB")
    print(f"source {im.width}x{im.height}")

    if mode == "full":
        out = src.with_suffix(".view.png")
        fit(im).save(out)
        print(out, Image.open(out).size)

    elif mode == "grid":
        rows, cols = int(sys.argv[3]), int(sys.argv[4])
        ow, oh = im.width // cols, im.height // rows
        pad = 40
        for r in range(rows):
            for c in range(cols):
                box = (
                    max(0, c * ow - pad), max(0, r * oh - pad),
                    min(im.width, (c + 1) * ow + pad),
                    min(im.height, (r + 1) * oh + pad),
                )
                out = src.with_suffix(f".r{r}c{c}.png")
                fit(im.crop(box)).save(out)
                print(out, Image.open(out).size)

    elif mode == "crop":
        x, y, w, h = (int(v) for v in sys.argv[3:7])
        out = src.with_suffix(".crop.png")
        fit(im.crop((x, y, x + w, y + h))).save(out)
        print(out, Image.open(out).size)


if __name__ == "__main__":
    main()
