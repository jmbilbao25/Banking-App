"""exlib -- a small, explicit Excalidraw scene builder.

Design notes
------------
* Layout is authored by hand in the page scripts (explicit x/y on a coarse grid).
  This module only handles Excalidraw boilerplate, icon embedding and text boxes,
  so the JSON stays valid and the coordinates stay readable.
* Text is never measured. Every text element is given an explicit box width and
  `textAlign`, so Excalidraw centres/aligns the glyphs inside that box itself.
  This makes the output font-metric independent -- nothing can drift.
* Icons are real official Azure V24 / CNCF SVGs, embedded as base64 data URLs in
  the `files` map and referenced by `image` elements.
"""

from __future__ import annotations

import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(HERE, "_icons", "flat")


def _default_out_dir() -> str:
    """Where finished .excalidraw files land.

    When exlib lives in a `tools/` directory the diagrams belong one level up,
    beside the README; otherwise they sit next to exlib itself. Override with
    the EX_OUT_DIR environment variable.
    """
    env = os.environ.get("EX_OUT_DIR")
    if env:
        return env
    if os.path.basename(HERE) == "tools":
        return os.path.dirname(HERE)
    return HERE


OUT_DIR = _default_out_dir()

# --------------------------------------------------------------------------
# Design system
# --------------------------------------------------------------------------

STAMP = 1735689600000   # 2025-01-01T00:00:00Z -- deterministic build output

FONT = 6          # Nunito -- clean sans, high legibility
LH = 1.25         # Excalidraw line height for this family

VERSION = "2.0"
UPDATED = "2026-08-08"

# One taxonomy, six meanings, applied identically on every page. Kept
# deliberately small: colour is reinforcement, and the icon plus the label
# always carry the meaning on their own so the set stays readable without it.
SEM = {
    "edge":     ("#FFEDD5", "#C2410C"),   # public entry point
    "platform": ("#DBEAFE", "#1D4ED8"),   # Azure service on the request path
    "data":     ("#EDE9FE", "#6D28D9"),   # holds state
    "security": ("#FEF3C7", "#B45309"),   # identity, keys, confidential compute
    "ops":      ("#D1FAE5", "#047857"),   # build, deploy, observe, govern
    "external": ("#F1F5F9", "#475569"),   # outside our control -- NOT standby
}

# The one authoritative wording for each colour. Pages name the keys they use
# and never their own labels, so a colour cannot come to mean two things in two
# places -- which is the failure mode when a diagram set grows.
#
# The wording is chosen to be *decidable*: for any element there is exactly one
# key that fits, so the same component cannot drift colour between pages.
#   edge      the public entry point
#   platform  an Azure service ON the request path
#   data      anything that holds state
#   security  identity, keys, confidential compute
#   ops       used to build, deploy, observe or govern -- off the request path
#   external  outside our control (actors, third parties, on-premises)
LEGEND = {
    "edge":     "Internet edge",
    "platform": "Azure service on the request path",
    "data":     "Data and state",
    "security": "Identity, keys, confidential compute",
    "ops":      "Build, deploy, observe, govern",
    "external": "Outside our control",
}

# Zone (container) tints -- lighter than card fills so cards read on top.
ZONE = {
    "edge":     ("#FFF7ED", "#EA580C"),
    "platform": ("#EFF6FF", "#2563EB"),
    "data":     ("#F5F3FF", "#7C3AED"),
    "security": ("#FFFBEB", "#D97706"),
    "ops":      ("#ECFDF5", "#059669"),
    "external": ("#F8FAFC", "#64748B"),
    "plain":    ("transparent", "#94A3B8"),
}

TITLE = "#0F172A"
SUBTLE = "#334155"
BODY = "#64748B"
INK = "#1E293B"

CODE_BG = "#0F172A"
CODE_FG = "#7DD3FC"
CODE_ACCENT = "#34D399"
CODE_DIM = "#94A3B8"



# The bundled Nunito subset has no arrows/box-drawing glyphs -- they render as
# blank gaps. Fail loudly at build time instead of shipping an invisible glyph.
BAD_GLYPHS = {
    "\u2192": '"->" or a word', "\u2190": '"<-"', "\u2191": "", "\u2193": "",
    "\u21d2": '"=>"', "\u2194": '"<->"', "\u2500": "", "\u2502": "",
    "\u251c": "", "\u2514": "", "\u2265": '">="', "\u2264": '"<="',
    "\u2713": '"ok"', "\u2717": '"x"', "\u26a0": '"!"',
}

# Per-glyph advance widths (advance / fontSize), measured from the real
# Excalidraw Nunito face by _render/charmetrics.py. Lets us pack text tightly
# and still know for certain whether a line fits its box.
with open(os.path.join(HERE, "metrics.json"), encoding="utf-8") as _fh:
    _M = json.load(_fh)
_ADV_TABLE = _M["unitsPerSize"]
_ADV_DEFAULT = _M["default"]


def text_width(s: str, size: float) -> float:
    """Estimated rendered width of a single line, in px."""
    return sum(_ADV_TABLE.get(ch, _ADV_DEFAULT) for ch in s) * size


def _check_glyphs(s: str) -> None:
    for ch in s:
        if ch in BAD_GLYPHS:
            hint = BAD_GLYPHS[ch]
            raise ValueError(
                f"glyph U+{ord(ch):04X} ({ch!r}) is not in the Nunito subset and "
                f"will render blank; use {hint or 'plain ASCII'} instead. text={s!r}"
            )


def _check_fit(s: str, w: float, size: float) -> None:
    for line in s.split("\n"):
        est = text_width(line, size)
        if est > w + 1:
            raise ValueError(
                f"text overflows its {w:.0f}px box by {est - w:.0f}px "
                f"(needs {est:.0f}px at {size}px): {line!r}"
            )


class Scene:
    def __init__(self, name: str):
        self.name = name
        self.els: list[dict] = []
        self.files: dict[str, dict] = {}
        self._n = 0
        self._seed = 100000

    # -- internals ---------------------------------------------------------
    def _id(self, hint: str) -> str:
        self._n += 1
        return f"{hint}_{self._n}"

    def _seedv(self) -> int:
        self._seed += 7
        return self._seed

    def _base(self, kind: str, x, y, w, h, stroke, fill, **kw) -> dict:
        role = kw.pop("role", None)
        el = {
            "id": kw.pop("id", None) or self._id(kind),
            "type": kind,
            "x": float(x), "y": float(y),
            "width": float(w), "height": float(h),
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": fill,
            "fillStyle": "solid",
            "strokeWidth": kw.pop("strokeWidth", 2),
            "strokeStyle": kw.pop("strokeStyle", "solid"),
            "roughness": 0,
            "opacity": 100,
            "groupIds": kw.pop("groupIds", []),
            "frameId": None,
            "index": None,
            "roundness": kw.pop("roundness", None),
            "seed": self._seedv(),
            "version": 1,
            "versionNonce": self._seedv(),
            "isDeleted": False,
            "boundElements": kw.pop("boundElements", None),
            "updated": 1,
            "link": None,
            "locked": False,
            "customData": {"role": role} if role else None,
        }
        el.update(kw)
        self.els.append(el)
        return el

    # -- primitives --------------------------------------------------------
    def rect(self, x, y, w, h, sem="external", *, radius=8, sw=2, style="solid",
             fill=None, stroke=None, palette=None):
        pal = palette or SEM
        f, s = pal[sem]
        return self._base(
            "rectangle", x, y, w, h,
            stroke or s, fill if fill is not None else f,
            strokeWidth=sw, strokeStyle=style,
            roundness={"type": 3} if radius else None,
        )

    def ellipse(self, x, y, w, h, sem="external", *, sw=2, fill=None, stroke=None):
        f, s = SEM[sem]
        return self._base("ellipse", x, y, w, h, stroke or s,
                          fill if fill is not None else f, strokeWidth=sw)

    def diamond(self, x, y, w, h, sem="security", *, sw=2):
        f, s = SEM[sem]
        return self._base("diamond", x, y, w, h, s, f, strokeWidth=sw)

    def text(self, s: str, x, y, w, size=13, *, color=INK, align="left",
             valign="top", bold=False, role="text"):
        """Text inside an explicit box of width `w`. Alignment is done by
        Excalidraw, so real glyph widths never matter."""
        _check_glyphs(s)
        _check_fit(s, w, size)
        lines = s.split("\n")
        h = len(lines) * size * LH
        return self._base(
            "text", x, y, w, h, color, "transparent",
            strokeWidth=1,
            text=s, originalText=s,
            fontSize=size, fontFamily=FONT,
            textAlign=align, verticalAlign=valign,
            containerId=None, lineHeight=LH,
            autoResize=False, role=role,
        )

    def line(self, pts, *, color="#94A3B8", sw=2, style="solid"):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = xs[0], ys[0]
        rel = [[p[0] - x0, p[1] - y0] for p in pts]
        return self._base(
            "line", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
            color, "transparent", strokeWidth=sw, strokeStyle=style,
            points=rel, lastCommittedPoint=None,
            startBinding=None, endBinding=None,
            startArrowhead=None, endArrowhead=None,
        )

    def arrow(self, pts, *, color="#334155", sw=2, style="solid",
              start=None, end="arrow", src=None, dst=None, gap=4,
              sharp=False):
        """`sharp=True` gives square elbows. Excalidraw's rounded corners bulge
        outward from the declared path, which can reach into a nearby label on a
        long multi-segment route -- and the geometry lint only sees the straight
        segments, so the bulge would not be caught."""
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = xs[0], ys[0]
        rel = [[p[0] - x0, p[1] - y0] for p in pts]
        a = self._base(
            "arrow", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
            color, "transparent", strokeWidth=sw, strokeStyle=style,
            points=rel, lastCommittedPoint=None,
            startBinding={"elementId": src["id"], "focus": 0, "gap": gap} if src else None,
            endBinding={"elementId": dst["id"], "focus": 0, "gap": gap} if dst else None,
            startArrowhead=start, endArrowhead=end,
            elbowed=False,
            roundness=None if sharp else {"type": 2},
        )
        for peer, key in ((src, "src"), (dst, "dst")):
            if peer is not None:
                peer.setdefault("boundElements", None)
                if peer["boundElements"] is None:
                    peer["boundElements"] = []
                peer["boundElements"].append({"id": a["id"], "type": "arrow"})
        return a

    # -- icons -------------------------------------------------------------
    def icon(self, key: str, x, y, size=28):
        path = os.path.join(ICON_DIR, key + ".svg")
        if not os.path.exists(path):
            raise FileNotFoundError(f"icon '{key}' not found at {path}")
        fid = "icon_" + key
        if fid not in self.files:
            with open(path, "rb") as fh:
                raw = fh.read()
            b64 = base64.b64encode(raw).decode("ascii")
            self.files[fid] = {
                "mimeType": "image/svg+xml",
                "id": fid,
                "dataURL": "data:image/svg+xml;base64," + b64,
                # fixed so regenerating produces byte-identical output and git
                # diffs show only real changes
                "created": STAMP,
                "lastRetrieved": STAMP,
            }
        return self._base(
            "image", x, y, size, size, "transparent", "transparent",
            strokeWidth=1,
            fileId=fid, status="saved", scale=[1, 1], crop=None, role="icon",
        )

    # -- composites --------------------------------------------------------
    def zone(self, x, y, w, h, label, sem="plain", *, sub=None, style="solid",
             sw=2, label_size=15, label_align="left"):
        """A labelled grouping region. Label sits above the top edge so it can
        never collide with the contents. `label_align="right"` moves it out of
        the way when arrows need to enter from the top left."""
        f, s = ZONE[sem]
        r = self._base("rectangle", x, y, w, h, s, f,
                       strokeWidth=sw, strokeStyle=style,
                       roundness={"type": 3}, role="zone")
        self.text(label, x + 14, y - label_size * LH - 7, w - 28,
                  label_size, color=s, align=label_align, role="zonelabel")
        if sub:
            self.text(sub, x + 14, y + 10, w - 28, 11, color=BODY, align="left")
        return r

    def card(self, x, y, w, h, icon_key, title, sem="platform", *, sub=None,
             icon_size=26, title_size=14, sub_size=12, sw=2, style="solid"):
        """One discrete thing in the system.

        `icon_key=None` renders the card without an icon. That is reserved for
        services this team builds and runs: an official product icon would
        misrepresent them, and the absence of one is a content-level signal
        rather than a colour-only one.
        """
        f, s = SEM[sem]
        r = self._base("rectangle", x, y, w, h, s, f, strokeWidth=sw,
                       strokeStyle=style, roundness={"type": 3}, role="card")
        if icon_key is None:
            tx = x + 14
        else:
            iy = y + (h - icon_size) / 2
            self.icon(icon_key, x + 11, iy, icon_size)
            tx = x + 11 + icon_size + 10
        tw = w - (tx - x) - 10
        if sub:
            th = title_size * LH
            sh = len(sub.split("\n")) * sub_size * LH
            top = y + (h - (th + sh + 2)) / 2
            self.text(title, tx, top, tw, title_size, color=INK, align="left",
                      role="cardtext")
            self.text(sub, tx, top + th + 2, tw, sub_size, color=BODY,
                      align="left", role="cardtext")
        else:
            nl = len(title.split("\n"))
            th = nl * title_size * LH
            self.text(title, tx, y + (h - th) / 2, tw, title_size,
                      color=INK, align="left", role="cardtext")
        return r

    def stack(self, cx, y, icon_key, label, *, icon_size=30, w=112, size=11,
              color=SUBTLE):
        """Icon with a centred caption underneath. No container -- used for
        rails, legends and tool badges."""
        img = self.icon(icon_key, cx - icon_size / 2, y, icon_size)
        self.text(label, cx - w / 2, y + icon_size + 6, w, size,
                  color=color, align="center", role="stacklabel")
        return img

    def code(self, x, y, w, lines, *, size=11, pad=12, title=None):
        """Evidence artifact: dark panel with monospace-ish content."""
        n = len(lines)
        head = (size * LH + 6) if title else 0
        h = pad * 2 + head + n * size * LH
        self._base("rectangle", x, y, w, h, "#334155", CODE_BG,
                   strokeWidth=1, roundness={"type": 3}, role="code")
        cy = y + pad
        if title:
            self.text(title, x + pad, cy, w - pad * 2, size, color=CODE_DIM,
                      align="left", role="codetext")
            cy += size * LH + 6
        for ln, col in lines:
            self.text(ln, x + pad, cy, w - pad * 2, size, color=col,
                      align="left", role="codetext")
            cy += size * LH
        return h

    # -- page furniture ----------------------------------------------------
    def header(self, x, y, title, subtitle, tag, kind, *, w=1100):
        """Title block with the metadata a reader needs to trust the diagram:
        what it is, which standard diagram type it is, and how fresh it is."""
        self.text(title, x, y, w, 30, color=TITLE, align="left", role="header")
        self.text(subtitle, x, y + 42, w, 14, color=SUBTLE, align="left",
                  role="header")
        self.text(tag, x + w - 520, y + 2, 520, 14, color="#94A3B8",
                  align="right", role="header")
        self.text(f"{kind}  \u00b7  v{VERSION}  \u00b7  updated {UPDATED}",
                  x + w - 520, y + 24, 520, 11, color="#94A3B8",
                  align="right", role="header")
        self.line([(x, y + 74), (x + w, y + 74)], color="#CBD5E1", sw=2)

    def note(self, x, y, w, s, *, size=12, color=BODY, align="left"):
        return self.text(s, x, y, w, size, color=color, align=align)

    def legend(self, x, y, items, *, w=200, gap=26, size=12):
        """Vertical legend. items = [(sem, label)]"""
        for i, (sem, label) in enumerate(items):
            yy = y + i * gap
            f, s = SEM[sem]
            self._base("rectangle", x, yy, 16, 16, s, f, strokeWidth=2,
                       roundness={"type": 3}, role="swatch")
            self.text(label, x + 24, yy + 1, w, size, color=SUBTLE,
                      align="left", role="legendlabel")

    def legend_row(self, x, y, keys, *, size=12, swatch=15, gap=26,
                   lines=True, services=True):
        """Compact single-line legend.

        `keys` are semantic names; the wording comes from LEGEND so it is
        identical on every page. Every page carries one, because the set
        introduces colour and line semantics that a reader should not have to
        infer.
        """
        cx = x
        for sem in keys:
            label = LEGEND[sem]
            f, s = SEM[sem]
            self._base("rectangle", cx, y, swatch, swatch, s, f, strokeWidth=2,
                       roundness={"type": 3}, role="swatch")
            lw = text_width(label, size)
            self.text(label, cx + swatch + 7, y, lw + 4, size, color=SUBTLE,
                      align="left", role="legendlabel")
            cx += swatch + 7 + lw + gap

        if lines:
            for style, label in (("solid", "synchronous call"),
                                 ("dashed", "asynchronous or control")):
                self.arrow([(cx, y + 8), (cx + 32, y + 8)], color=SUBTLE,
                           sw=2, style=style)
                lw = text_width(label, size)
                self.text(label, cx + 40, y, lw + 4, size, color=SUBTLE,
                          align="left", role="legendlabel")
                cx += 40 + lw + gap

        if services:
            label = "no icon = not an Azure service (our code, or a third party)"
            lw = text_width(label, size)
            self.text(label, cx, y, lw + 4, size, color=SUBTLE, align="left",
                      role="legendlabel")
            cx += lw
        return cx

    # -- output ------------------------------------------------------------
    def write(self, filename: str):
        """Save into OUT_DIR and report what was produced."""
        path = os.path.join(OUT_DIR, filename)
        self.save(path)
        print(f"{path}  {len(self.els)} elements, {len(self.files)} icons")
        return path

    def save(self, path: str):
        doc = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.els,
            "appState": {
                "gridSize": 20,
                "gridStep": 5,
                "gridModeEnabled": False,
                "viewBackgroundColor": "#FFFFFF",
            },
            "files": self.files,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
        return path
