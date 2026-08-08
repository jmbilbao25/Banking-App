"""Geometry lint for the generated .excalidraw pages.

Catches the defect classes that are invisible in JSON but obvious once rendered:

  TEXT_OVERLAP   two text blocks sitting on top of each other
  ARROW_THRU_TEXT   an arrow segment crossing a label it does not belong to
  ARROW_THRU_CARD   an arrow segment cutting through a card it does not connect
  CARD_OVERLAP   two cards overlapping
  OUT_OF_ZONE    a card that escaped the zone it visually belongs to

Usage: python3 lint.py [file.excalidraw ...]
"""
from __future__ import annotations

import glob
import json
import os
import sys

from exlib import text_width, LH, OUT_DIR

HERE = os.path.dirname(os.path.abspath(__file__))

# text roles that are *expected* to sit on top of their own card / panel
OWNED = {"cardtext", "codetext"}
PAD = 1.5  # shrink boxes slightly so touching edges are not flagged


def role(el):
    cd = el.get("customData") or {}
    return cd.get("role")


def tbox(el):
    """Actual ink box of a text element (not the layout box)."""
    lines = el["text"].split("\n")
    size = el["fontSize"]
    wmax = max((text_width(ln, size) for ln in lines), default=0)
    w = el["width"]
    align = el.get("textAlign", "left")
    if align == "center":
        x = el["x"] + (w - wmax) / 2
    elif align == "right":
        x = el["x"] + w - wmax
    else:
        x = el["x"]
    return (x, el["y"], x + wmax, el["y"] + len(lines) * size * LH)


def rbox(el):
    return (el["x"], el["y"], el["x"] + el["width"], el["y"] + el["height"])


def inter(a, b, pad=PAD):
    return (a[0] + pad < b[2] - pad and b[0] + pad < a[2] - pad
            and a[1] + pad < b[3] - pad and b[1] + pad < a[3] - pad)


def seg_box(p, q, box):
    """Does segment p-q intersect axis-aligned box (x0,y0,x1,y1)?"""
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = x0 + PAD, y0 + PAD, x1 - PAD, y1 - PAD
    if x1 <= x0 or y1 <= y0:
        return False
    (px, py), (qx, qy) = p, q
    if max(px, qx) < x0 or min(px, qx) > x1:
        return False
    if max(py, qy) < y0 or min(py, qy) > y1:
        return False
    # Liang-Barsky
    dx, dy = qx - px, qy - py
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, px - x0), (dx, x1 - px), (-dy, py - y0), (dy, y1 - py)):
        if pp == 0:
            if qq < 0:
                return False
            continue
        t = qq / pp
        if pp < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return False
    return True


def arrow_segments(el):
    ox, oy = el["x"], el["y"]
    pts = [(ox + px, oy + py) for px, py in el["points"]]
    return list(zip(pts, pts[1:]))


def check(path):
    doc = json.loads(open(path, encoding="utf-8").read())
    els = [e for e in doc["elements"] if not e.get("isDeleted")]
    by_id = {e["id"]: e for e in els}

    texts = [e for e in els if e["type"] == "text"]
    cards = [e for e in els if e["type"] == "rectangle" and role(e) == "card"]
    zones = [e for e in els if e["type"] == "rectangle" and role(e) == "zone"]
    panels = [e for e in els if e["type"] == "rectangle" and role(e) == "code"]
    arrows = [e for e in els if e["type"] == "arrow"]

    issues = []

    # ---- text vs text
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            if inter(tbox(a), tbox(b)):
                issues.append(
                    f"TEXT_OVERLAP    {a['text'].splitlines()[0][:38]!r} "
                    f"<-> {b['text'].splitlines()[0][:38]!r}")

    # ---- card vs card
    for i, a in enumerate(cards):
        for b in cards[i + 1:]:
            if inter(rbox(a), rbox(b)):
                issues.append(f"CARD_OVERLAP    {a['id']} <-> {b['id']}")

    # ---- text vs card it does not own
    owners = {}
    for c in cards + panels:
        for t in texts:
            if role(t) in OWNED and inter(tbox(t), rbox(c), pad=-2):
                owners[t["id"]] = c["id"]
    for t in texts:
        if role(t) in ("header", "zonelabel", "badge"):
            continue
        for c in cards + panels:
            if owners.get(t["id"]) == c["id"]:
                continue
            if role(t) in OWNED:
                continue
            if inter(tbox(t), rbox(c)):
                issues.append(
                    f"TEXT_ON_CARD    {t['text'].splitlines()[0][:38]!r} "
                    f"sits on {c['id']}")

    # ---- arrows
    for ar in arrows:
        connected = set()
        for key in ("startBinding", "endBinding"):
            b = ar.get(key)
            if b:
                connected.add(b["elementId"])
        # a bound icon lives inside a card -> treat that card as connected too
        for cid in list(connected):
            el = by_id.get(cid)
            if el is not None and el["type"] == "image":
                for c in cards:
                    if inter(rbox(el), rbox(c), pad=-2):
                        connected.add(c["id"])

        segs = arrow_segments(ar)
        for t in texts:
            if role(t) in ("header",):
                continue
            box = tbox(t)
            if any(seg_box(p, q, box) for p, q in segs):
                issues.append(
                    f"ARROW_THRU_TEXT {ar['id']} crosses "
                    f"{t['text'].splitlines()[0][:38]!r}")
        for c in cards + panels:
            if c["id"] in connected:
                continue
            box = rbox(c)
            if any(seg_box(p, q, box) for p, q in segs):
                issues.append(f"ARROW_THRU_CARD {ar['id']} crosses {c['id']}")

    # ---- code panels / text escaping the bottom of their zone
    for z in zones:
        zb = rbox(z)
        for e in panels + cards + texts:
            if e is z:
                continue
            eb = tbox(e) if e["type"] == "text" else rbox(e)
            if role(e) in ("zonelabel", "header"):
                continue
            # only consider things that clearly live inside this zone
            if not (eb[0] >= zb[0] - 2 and eb[2] <= zb[2] + 2):
                continue
            # must genuinely start inside this zone, then spill out the bottom
            if zb[1] - 2 <= eb[1] < zb[3] - 2 and eb[3] > zb[3] + 2:
                lbl = ((e.get("text") or "").splitlines() or [e["type"]])[0]
                issues.append(
                    f"ESCAPES_ZONE    {e.get('id')} ({lbl[:28]!r}) "
                    f"bottom {eb[3]:.0f} > zone {z['id']} bottom {zb[3]:.0f}")

    # ---- cards escaping every zone (loose cards are fine, flag partial escapes)
    for c in cards:
        cb = rbox(c)
        for z in zones:
            zb = rbox(z)
            if inter(cb, zb) and not (
                cb[0] >= zb[0] - 2 and cb[2] <= zb[2] + 2
                and cb[1] >= zb[1] - 2 and cb[3] <= zb[3] + 2
            ):
                issues.append(f"OUT_OF_ZONE     {c['id']} straddles {z['id']}")

    return issues


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(OUT_DIR, "*.excalidraw")))
    total = 0
    for p in paths:
        issues = check(p)
        name = os.path.basename(p)
        if issues:
            print(f"\n=== {name}: {len(issues)} issue(s) ===")
            seen = set()
            for it in issues:
                if it in seen:
                    continue
                seen.add(it)
                print("  " + it)
            total += len(issues)
        else:
            print(f"OK  {name}")
    print(f"\ntotal issues: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
