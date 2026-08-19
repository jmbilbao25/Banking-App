/**
 * TechStart (EastWest ITG) slide theme.
 *
 * Palette and motif taken from the TechStart Program banner: magenta-to-purple
 * diagonal ribbon, lime wordmark accent, gold dot texture, EastWest diamond mark.
 * No confidentiality sidebar.
 */

const fs = require("fs");
const path = require("path");

const MAGENTA = "C2007B";
const MAGENTA_DK = "9C0062";
const PURPLE = "6B1F7C";
const PURPLE_DK = "4E1259";
const LIME = "C4D82E";
const GOLD = "C9A227";

const INK = "231F20";
const MUTED = "6B6B6B";
const HAIR = "C9C9C9";
const ALT = "F6F3F8";
const HDR = "EDE4F1";

const RED = "C62828";
const AMBER = "E07C00";
const GREEN = "2E7D32";

const FONT = "Arial";

const W = 13.333;
const H = 7.5;

const CX = 0.55;
const CW = 12.23;
const CY = 1.18;

/* ── EastWest logo ──────────────────────────────────────────────────────
 * Drop the official artwork at generator/assets/eastwest-logo.png and it is
 * used verbatim. Without it, a close native approximation is drawn: two-tone
 * diamond mark with a lime core, and the "east"/"west" split wordmark.
 * ---------------------------------------------------------------------- */
const LOGO_PNG = path.join(__dirname, "assets", "eastwest-logo.png");
const LOGO_WHITE_PNG = path.join(__dirname, "assets", "eastwest-logo-white.png");

/** The banner lives in the repo already; don't duplicate it into assets/. */
function resolveBanner() {
  const candidates = [
    path.join(__dirname, "assets", "techstart-banner.png"),
    path.join(__dirname, "..", "..", "..", "LinkedInBanner_Revised (2).png"),
    "/projects/sandbox/Banking-App/docs/LinkedInBanner_Revised (2).png",
  ];
  return candidates.find((p) => fs.existsSync(p)) || candidates[0];
}
const BANNER_PNG = resolveBanner();

function ewLogo(slide, x, y, h, opts = {}) {
  const white = !!opts.white;
  const asset = white ? LOGO_WHITE_PNG : LOGO_PNG;

  if (fs.existsSync(asset)) {
    const { w: iw, h: ih } = pngSize(asset);
    slide.addImage({ path: asset, x, y, w: h * (iw / ih), h });
    return;
  }

  const d = h * 1.18; // mark is slightly taller than the wordmark x-height

  // two-tone diamond: purple upper half, magenta lower half
  slide.addShape("triangle", {
    x, y, w: d, h: d / 2,
    fill: { color: white ? "FFFFFF" : PURPLE },
    line: { type: "none" },
  });
  slide.addShape("triangle", {
    x, y: y + d / 2, w: d, h: d / 2, rotate: 180,
    fill: { color: white ? "FFFFFF" : MAGENTA },
    line: { type: "none" },
  });
  // lime core
  slide.addShape("diamond", {
    x: x + d * 0.3, y: y + d * 0.3, w: d * 0.4, h: d * 0.4,
    fill: { color: white ? MAGENTA : LIME },
    line: { type: "none" },
  });

  slide.addText(
    [
      { text: "east", options: { color: white ? "FFFFFF" : PURPLE } },
      { text: "west", options: { color: white ? "FFFFFF" : MAGENTA } },
    ],
    {
      x: x + d * 1.1,
      y: y - h * 0.04,
      w: h * 4.6,
      h: d,
      fontFace: FONT,
      fontSize: opts.fontSize || h * 27,
      bold: true,
      valign: "middle",
      margin: 0,
      charSpacing: -0.3,
    }
  );
}

/* ── gold dot texture block (banner motif) ─────────────────────────────── */
function dotField(slide, x, y, cols, rows, gap, size, color, transparency) {
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      slide.addShape("ellipse", {
        x: x + c * gap,
        y: y + r * gap,
        w: size,
        h: size,
        fill: { color, transparency: transparency == null ? 45 : transparency },
        line: { type: "none" },
      });
    }
  }
}

/* ── title-slide ribbon: layered rotated bands, no gradient needed ─────── */
function ribbon(slide) {
  slide.addShape("rect", {
    x: 6.2, y: -2.6, w: 5.4, h: 13.0, rotate: 20,
    fill: { color: PURPLE }, line: { type: "none" },
  });
  slide.addShape("rect", {
    x: 9.1, y: -2.6, w: 3.0, h: 13.0, rotate: 20,
    fill: { color: PURPLE_DK }, line: { type: "none" },
  });
  slide.addShape("rect", {
    x: 5.0, y: -2.6, w: 1.9, h: 13.0, rotate: 20,
    fill: { color: MAGENTA }, line: { type: "none" },
  });
  slide.addShape("rect", {
    x: 4.68, y: -2.6, w: 0.1, h: 13.0, rotate: 20,
    fill: { color: LIME }, line: { type: "none" },
  });
  dotField(slide, 11.15, 5.55, 9, 6, 0.2, 0.075, GOLD, 35);
}

/* ── standard content-slide chrome ─────────────────────────────────────── */
function chrome(slide, pageNum, opts = {}) {
  const { title, subtitle, kicker } = opts;

  // footer band
  slide.addShape("rect", {
    x: 0, y: 6.94, w: W, h: 0.56,
    fill: { color: PURPLE }, line: { type: "none" },
  });
  slide.addShape("rect", {
    x: 0, y: 6.94, w: W, h: 0.045,
    fill: { color: LIME }, line: { type: "none" },
  });
  slide.addShape("rect", {
    x: 0, y: 6.94, w: 2.5, h: 0.045,
    fill: { color: MAGENTA }, line: { type: "none" },
  });

  ewLogo(slide, 0.55, 7.05, 0.32, { white: true, fontSize: 11.5 });

  slide.addText("TechStart", {
    x: 10.2, y: 7.02, w: 2.35, h: 0.4,
    fontFace: FONT, fontSize: 9.5, color: "FFFFFF",
    align: "right", valign: "middle", margin: 0,
  });

  if (pageNum != null) {
    slide.addShape("ellipse", {
      x: 12.68, y: 7.06, w: 0.32, h: 0.32,
      fill: { color: LIME }, line: { type: "none" },
    });
    slide.addText(String(pageNum), {
      x: 12.68, y: 7.06, w: 0.32, h: 0.32,
      fontFace: FONT, fontSize: 10, bold: true, color: PURPLE_DK,
      align: "center", valign: "middle", margin: 0,
    });
  }

  let ty = 0.34;
  if (kicker) {
    slide.addText(kicker.toUpperCase(), {
      x: CX, y: 0.26, w: CW, h: 0.24,
      fontFace: FONT, fontSize: 9, bold: true, color: MAGENTA,
      margin: 0, valign: "middle", charSpacing: 1.4,
    });
    ty = 0.52;
  }

  if (title) {
    slide.addText(title, {
      x: CX, y: ty, w: CW, h: 0.46,
      fontFace: FONT, fontSize: 26, bold: true, color: PURPLE_DK,
      margin: 0, valign: "middle",
    });
  }

  if (subtitle) {
    slide.addText(subtitle, {
      x: CX, y: ty + 0.46, w: CW, h: 0.3,
      fontFace: FONT, fontSize: 12.5, color: MUTED,
      margin: 0, valign: "middle",
    });
  }

  // short lime rule under the title block
  if (title) {
    slide.addShape("rect", {
      x: CX, y: subtitle ? ty + 0.8 : ty + 0.5, w: 0.62, h: 0.05,
      fill: { color: LIME }, line: { type: "none" },
    });
  }
}

/* ── image placement that never distorts ───────────────────────────────── */
function pngSize(file) {
  const b = fs.readFileSync(file);
  if (b.readUInt32BE(12) !== 0x49484452) throw new Error(`not a PNG IHDR: ${file}`);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

/** Fit `file` inside the box, preserving aspect ratio, centred. */
function fit(file, bx, by, bw, bh) {
  const { w, h } = pngSize(file);
  const s = Math.min(bw / w, bh / h);
  const iw = w * s;
  const ih = h * s;
  return { path: file, x: bx + (bw - iw) / 2, y: by + (bh - ih) / 2, w: iw, h: ih };
}

/** Place an image aspect-correct, with an optional hairline frame. */
function image(slide, file, bx, by, bw, bh, opts = {}) {
  const g = fit(file, bx, by, bw, bh);
  if (opts.valign === "top") g.y = by;
  if (opts.frame !== false) {
    slide.addShape("rect", {
      x: g.x - 0.02, y: g.y - 0.02, w: g.w + 0.04, h: g.h + 0.04,
      fill: { color: "FFFFFF" },
      line: { color: opts.frameColor || HAIR, width: 0.75 },
    });
  }
  slide.addImage(g);
  return g;
}

/* ── content primitives ───────────────────────────────────────────────── */

/** Coloured card with a heading and short body lines. */
function card(slide, o) {
  const {
    x, y, w, h, title, lines = [], accent = PURPLE, fill = "FFFFFF",
    titleSize = 12, bodySize = 10, num,
  } = o;

  slide.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.05,
    fill: { color: fill }, line: { color: accent, width: 1.15 },
  });
  slide.addShape("rect", {
    x, y, w, h: 0.055,
    fill: { color: accent }, line: { type: "none" },
  });

  let tx = x + 0.16;
  let tw = w - 0.32;
  if (num != null) {
    slide.addShape("ellipse", {
      x: x + 0.16, y: y + 0.18, w: 0.3, h: 0.3,
      fill: { color: accent }, line: { type: "none" },
    });
    slide.addText(String(num), {
      x: x + 0.16, y: y + 0.18, w: 0.3, h: 0.3,
      fontFace: FONT, fontSize: 10, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0,
    });
    tx = x + 0.56;
    tw = w - 0.72;
  }

  slide.addText(title, {
    x: tx, y: y + 0.16, w: tw, h: 0.34,
    fontFace: FONT, fontSize: titleSize, bold: true, color: PURPLE_DK,
    margin: 0, valign: "middle",
  });

  if (lines.length) {
    slide.addText(
      lines.map((l, i) => {
        const isObj = typeof l === "object";
        return {
          text: isObj ? l.text : l,
          options: {
            bullet: o.bullets !== false,
            breakLine: true,
            paraSpaceAfter: o.spaceAfter != null ? o.spaceAfter : 5,
            color: isObj && l.color ? l.color : INK,
            bold: isObj ? !!l.bold : false,
          },
        };
      }),
      {
        x: x + 0.18, y: y + 0.54, w: w - 0.36, h: h - 0.7,
        fontFace: FONT, fontSize: bodySize, color: INK,
        margin: 0, valign: "top", lineSpacingMultiple: 1.05,
      }
    );
  }
}

/** Big number / metric callout. */
function stat(slide, x, y, w, value, label, color = MAGENTA) {
  slide.addText(value, {
    x, y, w, h: 0.52,
    fontFace: FONT, fontSize: 30, bold: true, color,
    align: "center", valign: "middle", margin: 0,
  });
  slide.addText(label, {
    x, y: y + 0.5, w, h: 0.34,
    fontFace: FONT, fontSize: 9, color: MUTED,
    align: "center", valign: "top", margin: 0, lineSpacingMultiple: 0.95,
  });
}

/** Table with the TechStart header treatment. */
function table(slide, rows, opts = {}) {
  const head = rows[0].map((c) => ({
    text: typeof c === "object" ? c.text : c,
    options: {
      bold: true,
      fill: { color: PURPLE },
      color: "FFFFFF",
      fontSize: opts.headFontSize || opts.fontSize || 10,
      valign: "middle",
      align: typeof c === "object" && c.align ? c.align : "left",
    },
  }));

  const body = rows.slice(1).map((r, ri) =>
    r.map((c) => {
      const isObj = typeof c === "object" && c !== null;
      return {
        text: isObj ? String(c.text) : String(c),
        options: {
          fill: { color: ri % 2 === 1 ? ALT : "FFFFFF" },
          color: isObj && c.color ? c.color : INK,
          bold: isObj ? !!c.bold : false,
          fontSize: opts.fontSize || 10,
          valign: "middle",
          align: isObj && c.align ? c.align : "left",
        },
      };
    })
  );

  slide.addTable([head, ...body], {
    x: opts.x != null ? opts.x : CX,
    y: opts.y,
    w: opts.w || CW,
    colW: opts.colW,
    rowH: opts.rowH,
    border: { type: "solid", pt: 0.5, color: HAIR },
    fontFace: FONT,
    autoPage: false,
    margin: opts.cellMargin != null ? opts.cellMargin : 5,
  });
}

/** Status pill. */
function pill(slide, x, y, w, text, color) {
  slide.addShape("roundRect", {
    x, y, w, h: 0.26, rectRadius: 0.13,
    fill: { color }, line: { type: "none" },
  });
  slide.addText(text, {
    x, y, w, h: 0.26,
    fontFace: FONT, fontSize: 8, bold: true, color: "FFFFFF",
    align: "center", valign: "middle", margin: 0,
  });
}

function footnote(slide, text, y) {
  slide.addText(text, {
    x: CX, y: y == null ? 6.62 : y, w: CW, h: 0.26,
    fontFace: FONT, fontSize: 8, italic: true, color: MUTED,
    margin: 0, valign: "middle",
  });
}

module.exports = {
  MAGENTA, MAGENTA_DK, PURPLE, PURPLE_DK, LIME, GOLD,
  INK, MUTED, HAIR, ALT, HDR, RED, AMBER, GREEN,
  FONT, W, H, CX, CW, CY,
  BANNER_PNG, LOGO_PNG, LOGO_WHITE_PNG,
  chrome, ribbon, ewLogo, dotField,
  pngSize, fit, image,
  card, stat, table, pill, footnote,
};
