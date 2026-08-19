/**
 * EastWest Bank corporate slide chrome + reusable content primitives.
 *
 * Deliberately reproduces the bank's own template furniture (lime footer bar,
 * rotated "Strictly Private and Confidential" sidebar rule, chevron mark,
 * label : value body pattern) so the deck drops straight into their DRB/ARB pack.
 */

const LIME = "C3D600";
const BLACK = "000000";
const INK = "1A1A1A";
const MUTED = "595959";
const HDR_GREY = "D9D9D9";
const ALT_GREY = "F2F2F2";
const LINE_GREY = "808080";

const RED = "C62828";
const AMBER = "EF6C00";
const GREEN = "2E7D32";
const BLUE = "1565C0";

const BAND_BLUE = "E8F0FE";
const BAND_AMBER = "FFF4E5";
const BAND_RED = "FFEBEE";
const BAND_GREEN = "E8F5E9";
const BAND_GREY = "ECEFF1";

const FONT = "Arial";

// LAYOUT_WIDE canvas
const W = 13.333;
const H = 7.5;

// content box
const CX = 0.78; // left content edge
const CW = 12.1; // content width
const CY = 1.12; // top of content
const CB = 6.68; // bottom of content (above footer bar)

/** Draw the standard template furniture on a slide. */
function chrome(slide, pageNum, opts = {}) {
  const { title, subtitle, flag } = opts;

  // vertical lime rule at the far left
  slide.addShape("rect", {
    x: 0.4,
    y: 0.3,
    w: 0.045,
    h: 6.32,
    fill: { color: LIME },
    line: { type: "none" },
  });

  // rotated confidentiality marking
  slide.addText("Strictly Private and Confidential", {
    x: -1.63,
    y: 3.2,
    w: 4.0,
    h: 0.32,
    rotate: 270,
    fontFace: FONT,
    fontSize: 11,
    color: INK,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  // footer bar
  slide.addShape("rect", {
    x: 0,
    y: 6.83,
    w: W,
    h: 0.67,
    fill: { color: LIME },
    line: { type: "none" },
  });

  slide.addText("www.eastwestbanker.com", {
    x: 0.5,
    y: 6.96,
    w: 4.2,
    h: 0.34,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: "FFFFFF",
    charSpacing: 1.6,
    margin: 0,
    valign: "middle",
  });

  // chevron mark
  slide.addText(">", {
    x: 12.5,
    y: 6.74,
    w: 0.8,
    h: 0.74,
    fontFace: FONT,
    fontSize: 44,
    bold: true,
    color: "FFFFFF",
    align: "center",
    valign: "middle",
    margin: 0,
  });

  if (pageNum != null) {
    slide.addText(String(pageNum), {
      x: 11.82,
      y: 6.98,
      w: 0.6,
      h: 0.34,
      fontFace: FONT,
      fontSize: 14,
      color: "FFFFFF",
      align: "right",
      valign: "middle",
      margin: 0,
    });
  }

  if (title) {
    slide.addText(title, {
      x: CX,
      y: 0.24,
      w: 11.4,
      h: 0.52,
      fontFace: FONT,
      fontSize: 27,
      bold: true,
      color: BLACK,
      margin: 0,
      valign: "middle",
    });
  }

  if (subtitle) {
    slide.addText(subtitle, {
      x: CX,
      y: 0.72,
      w: 11.4,
      h: 0.36,
      fontFace: FONT,
      fontSize: 16,
      color: INK,
      margin: 0,
      valign: "middle",
    });
  }

  if (flag) {
    slide.addText(flag, {
      x: 9.75,
      y: 0.12,
      w: 3.2,
      h: 0.42,
      fontFace: FONT,
      fontSize: 10.5,
      italic: true,
      color: "7A5C00",
      fill: { color: "FFF9C4" },
      align: "center",
      valign: "middle",
      margin: 2,
    });
  }
}

/**
 * The template's "Label : value" body row.
 * `value` may be a string or an array of pptxgenjs text objects / bullet lines.
 */
function labelValue(slide, y, label, value, opts = {}) {
  const labelW = opts.labelW || 2.55;
  const size = opts.fontSize || 12;
  const valueX = CX + labelW + 0.42;
  const valueW = opts.valueW || CX + CW - valueX;

  slide.addText(label, {
    x: CX,
    y,
    w: labelW,
    h: opts.labelH || 0.3,
    fontFace: FONT,
    fontSize: size,
    bold: true,
    color: BLACK,
    margin: 0,
    valign: "top",
  });

  slide.addText(":", {
    x: CX + labelW + 0.14,
    y,
    w: 0.2,
    h: 0.3,
    fontFace: FONT,
    fontSize: size,
    bold: true,
    color: BLACK,
    margin: 0,
    valign: "top",
  });

  const body = Array.isArray(value)
    ? value
    : [{ text: value, options: { breakLine: true } }];

  slide.addText(body, {
    x: valueX,
    y,
    w: valueW,
    h: opts.h || 0.3,
    fontFace: FONT,
    fontSize: size,
    italic: opts.italic !== false,
    color: INK,
    margin: 0,
    valign: "top",
    lineSpacingMultiple: opts.lineSpacing || 1.06,
  });
}

/** Bulleted lines for use inside labelValue. */
function bullets(lines, opts = {}) {
  return lines.map((l, i) => {
    const isObj = typeof l === "object";
    return {
      text: isObj ? l.text : l,
      options: {
        bullet: true,
        breakLine: true,
        paraSpaceAfter: opts.spaceAfter != null ? opts.spaceAfter : 4,
        bold: isObj ? !!l.bold : false,
        color: isObj && l.color ? l.color : undefined,
        indentLevel: isObj && l.indent ? l.indent : 0,
      },
    };
  });
}

/** Corporate table: grey header, banded rows, hairline borders. */
function table(slide, rows, opts = {}) {
  const head = rows[0];
  const body = rows.slice(1);

  const headerRow = head.map((c) => ({
    text: typeof c === "object" ? c.text : c,
    options: {
      bold: true,
      fill: { color: opts.headerFill || HDR_GREY },
      color: BLACK,
      fontSize: opts.headFontSize || opts.fontSize || 10,
      valign: "middle",
      align: typeof c === "object" && c.align ? c.align : "left",
    },
  }));

  const bodyRows = body.map((r, ri) =>
    r.map((c) => {
      const isObj = typeof c === "object" && c !== null;
      const txt = isObj ? c.text : c;
      return {
        text: txt == null ? "" : String(txt),
        options: {
          fill: { color: ri % 2 === 1 ? ALT_GREY : "FFFFFF" },
          color: isObj && c.color ? c.color : INK,
          bold: isObj ? !!c.bold : false,
          fontSize: opts.fontSize || 10,
          valign: "middle",
          align: isObj && c.align ? c.align : "left",
        },
      };
    })
  );

  slide.addTable([headerRow, ...bodyRows], {
    x: opts.x != null ? opts.x : CX,
    y: opts.y,
    w: opts.w || CW,
    colW: opts.colW,
    rowH: opts.rowH,
    border: { type: "solid", pt: 0.5, color: opts.borderColor || LINE_GREY },
    fontFace: FONT,
    autoPage: false,
    margin: opts.cellMargin != null ? opts.cellMargin : 4,
  });
}

/** A titled note/callout box. */
function callout(slide, opts) {
  const {
    x,
    y,
    w,
    h,
    title,
    body,
    accent = RED,
    fill = BAND_RED,
    fontSize = 10,
  } = opts;

  slide.addShape("roundRect", {
    x,
    y,
    w,
    h,
    rectRadius: 0.06,
    fill: { color: fill },
    line: { color: accent, width: 1.25 },
  });

  const parts = [];
  if (title) {
    parts.push({
      text: title,
      options: { bold: true, color: accent, breakLine: true, fontSize: fontSize + 0.5 },
    });
  }
  const lines = Array.isArray(body) ? body : [body];
  lines.forEach((l, i) => {
    parts.push({
      text: l,
      options: { color: INK, breakLine: i < lines.length - 1, fontSize },
    });
  });

  slide.addText(parts, {
    x: x + 0.12,
    y: y + 0.06,
    w: w - 0.24,
    h: h - 0.12,
    fontFace: FONT,
    fontSize,
    valign: "middle",
    margin: 0,
    lineSpacingMultiple: 1.05,
  });
}

/** Small pill/legend chip. */
function chip(slide, x, y, w, text, color, fill) {
  slide.addShape("roundRect", {
    x,
    y,
    w,
    h: 0.24,
    rectRadius: 0.12,
    fill: { color: fill },
    line: { color, width: 0.75 },
  });
  slide.addText(text, {
    x,
    y,
    w,
    h: 0.24,
    fontFace: FONT,
    fontSize: 8,
    bold: true,
    color,
    align: "center",
    valign: "middle",
    margin: 0,
  });
}

module.exports = {
  LIME, BLACK, INK, MUTED, HDR_GREY, ALT_GREY, LINE_GREY,
  RED, AMBER, GREEN, BLUE,
  BAND_BLUE, BAND_AMBER, BAND_RED, BAND_GREEN, BAND_GREY,
  FONT, W, H, CX, CW, CY, CB,
  chrome, labelValue, bullets, table, callout, chip,
};
