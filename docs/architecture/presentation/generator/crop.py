"""
Trim dead space from the captured screenshots.

Detects the last row / column that actually contains content by looking at
horizontal (resp. vertical) variance. A row of pure background is flat or a
smooth gradient, so its variance is low; a row with text or a card edge spikes.
Works for both the flat-dark merchant theme and the gradient bank theme.
"""
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/projects/sandbox/deckbuild/shots")
DST = Path("/projects/sandbox/deckbuild/shots_trimmed")
DST.mkdir(parents=True, exist_ok=True)

PAD = 28  # px of breathing room kept after the last content row


def content_extent(arr, axis):
    """Return the last index along `axis` that carries content."""
    # variance along the perpendicular axis, per line
    lines = arr.std(axis=1 - axis).mean(axis=1) if arr.ndim == 3 else arr.std(axis=1 - axis)
    thresh = max(lines.max() * 0.06, 1.5)
    idx = np.where(lines > thresh)[0]
    return int(idx[-1]) if len(idx) else arr.shape[axis] - 1


def main():
    for src in sorted(SRC.glob("*.png")):
        im = Image.open(src).convert("RGB")
        arr = np.asarray(im).astype(np.float32)

        last_row = content_extent(arr, 0)
        last_col = content_extent(arr, 1)

        bottom = min(im.height, last_row + PAD)
        right = min(im.width, last_col + PAD)

        # never crop away more than 55% of either dimension
        bottom = max(bottom, int(im.height * 0.45))
        right = max(right, int(im.width * 0.45))

        out = im.crop((0, 0, right, bottom))
        out.save(DST / src.name, optimize=True)
        print(f"{src.name}: {im.width}x{im.height} -> {out.width}x{out.height}")


if __name__ == "__main__":
    main()
