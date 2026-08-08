"""Measure per-character advance widths for the Excalidraw Nunito font.

Writes ../metrics.json = {"family": 6, "unitsPerSize": {char: advance/fontSize}}
so exlib can estimate any string width to within a couple of percent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render import serve, WEB  # noqa: E402

CHARS = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
    "\u00b7\u2014\u2013\u2019\u00e9\u00f1\u00b0\u00ae\u2122\u20ac\u00a3"
)
SIZE = 100
REPEAT = 20  # measure a run so per-glyph advance averages out kerning noise


def main() -> None:
    from playwright.sync_api import sync_playwright

    els = []
    for i, ch in enumerate(CHARS):
        txt = ch * REPEAT
        els.append({
            "id": f"c{i}", "type": "text",
            "x": 0, "y": i * 160, "width": 20000, "height": SIZE * 1.25,
            "angle": 0, "strokeColor": "#000000",
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 0,
            "opacity": 100, "groupIds": [], "frameId": None, "index": None,
            "roundness": None, "seed": 1, "version": 1, "versionNonce": 1,
            "isDeleted": False, "boundElements": None, "updated": 1,
            "link": None, "locked": False,
            "text": txt, "originalText": txt, "fontSize": SIZE,
            "fontFamily": 6, "textAlign": "left", "verticalAlign": "top",
            "containerId": None, "lineHeight": 1.25, "autoResize": False,
        })

    doc = {"type": "excalidraw", "version": 2, "source": "x", "elements": els,
           "appState": {"viewBackgroundColor": "#ffffff"}, "files": {}}

    with serve(WEB) as port, sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1200, "height": 900})
        pg.goto(f"http://127.0.0.1:{port}/index.html")
        pg.wait_for_function("window.__moduleReady === true", timeout=60000)
        pg.evaluate("window.__renderComplete=false")
        pg.evaluate("(d) => window.renderDiagram(d)", doc)
        pg.wait_for_function("window.__renderComplete === true", timeout=60000)
        pg.wait_for_timeout(1000)
        widths = pg.evaluate(
            "Array.from(document.querySelectorAll('#root svg text'))"
            ".map(t => t.getComputedTextLength())"
        )
        b.close()

    if len(widths) != len(CHARS):
        print(f"ERROR: got {len(widths)} nodes, expected {len(CHARS)}",
              file=sys.stderr)
        sys.exit(1)

    table = {}
    for ch, w in zip(CHARS, widths):
        table[ch] = round(w / REPEAT / SIZE, 5)

    out = Path(__file__).parent.parent / "metrics.json"
    out.write_text(json.dumps(
        {"family": 6, "note": "advance width / fontSize, Excalidraw Nunito",
         "default": round(max(table.values()), 5),
         "unitsPerSize": table}, indent=1), encoding="utf-8")
    print("wrote", out, f"({len(table)} glyphs)")
    print("space:", table[" "], " M:", table["M"], " i:", table["i"],
          " widest:", max(table, key=table.get), max(table.values()))


if __name__ == "__main__":
    main()
