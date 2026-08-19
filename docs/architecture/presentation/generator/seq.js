/**
 * Native-shape UML sequence diagram renderer for pptxgenjs.
 *
 * Everything is emitted as real PowerPoint shapes and connectors, so the
 * diagram stays editable in the deck instead of being a flattened image.
 */

const T = require("./theme");

/**
 * @param {object} slide  pptxgenjs slide
 * @param {object} o
 *   x, y, w, h        bounding box in inches
 *   lanes             [{ label, sub, fill?, color? }]
 *   messages          [{ from, to, text, kind?, note? }]
 *                     kind: 'call' (solid arrow, default) | 'return' (dashed)
 *                         | 'self' (box on its own lifeline)
 *                         | 'db'   (solid arrow, data-tier styling)
 *   bands             [{ from, to, label, fill }]  message indices, inclusive
 *   laneFontSize, msgFontSize
 */
function sequence(slide, o) {
  const {
    x,
    y,
    w,
    h,
    lanes,
    messages,
    bands = [],
    laneFontSize = 8.5,
    msgFontSize = 8,
    headerH = 0.46,
  } = o;

  const n = lanes.length;
  const laneW = w / n;
  const centers = lanes.map((_, i) => x + laneW * i + laneW / 2);

  const lifeTop = y + headerH;
  const lifeBot = y + h;

  // Message rows are spaced in "units". A row that opens a band gets extra
  // units in front of it, reserving a clear strip for that band's caption so
  // it can never sit on top of a message label.
  const BAND_GAP = 0.85;
  const LABEL_STRIP = 0.13;
  const LABEL_CLEAR = 0.045; // gap between a label's baseline and its arrow

  const bandStarts = new Set(bands.map((b) => b.from));
  const units = [];
  let acc = 0;
  for (let i = 0; i < messages.length; i += 1) {
    if (i > 0) acc += 1;
    if (i > 0 && bandStarts.has(i)) acc += BAND_GAP;
    units.push(acc);
  }
  const totalUnits = acc || 1;

  const firstY = lifeTop + 0.46;
  const usable = lifeBot - firstY - 0.05;
  const pitch = usable / totalUnits;
  const msgY = (i) => firstY + units[i] * pitch;

  // vertical room reserved above each arrow for its own label
  const labelSpace = pitch * 0.86;

  // ── stage bands (drawn first so they sit behind everything) ──
  bands.forEach((b) => {
    const top = msgY(b.from) - labelSpace - LABEL_CLEAR - LABEL_STRIP;
    const bot = msgY(b.to) + pitch * 0.34;
    slide.addShape("rect", {
      x: x - 0.04,
      y: top,
      w: w + 0.08,
      h: Math.max(bot - top, 0.18),
      fill: { color: b.fill },
      line: { type: "none" },
    });
    if (b.label) {
      slide.addText(b.label, {
        x: x - 0.02,
        y: top + 0.008,
        w: w,
        h: LABEL_STRIP,
        fontFace: T.FONT,
        fontSize: 7,
        bold: true,
        color: b.labelColor || T.MUTED,
        margin: 0,
        valign: "middle",
        charSpacing: 0.4,
      });
    }
  });

  // ── lifelines ──
  centers.forEach((cx) => {
    slide.addShape("line", {
      x: cx,
      y: lifeTop,
      w: 0,
      h: lifeBot - lifeTop,
      line: { color: "9E9E9E", width: 0.75, dashType: "dash" },
    });
  });

  // ── participant headers ──
  lanes.forEach((ln, i) => {
    const bx = x + laneW * i + 0.045;
    const bw = laneW - 0.09;
    slide.addShape("rect", {
      x: bx,
      y,
      w: bw,
      h: headerH,
      fill: { color: ln.fill || "FFFFFF" },
      line: { color: ln.color || T.INK, width: 1 },
    });
    const parts = [
      {
        text: ln.label,
        options: { bold: true, breakLine: !!ln.sub, fontSize: laneFontSize },
      },
    ];
    if (ln.sub) {
      parts.push({
        text: ln.sub,
        options: { fontSize: laneFontSize - 1.4, color: T.MUTED },
      });
    }
    slide.addText(parts, {
      x: bx,
      y,
      w: bw,
      h: headerH,
      fontFace: T.FONT,
      align: "center",
      valign: "middle",
      margin: 1,
      color: T.INK,
      lineSpacingMultiple: 0.92,
    });
  });

  // ── messages ──
  messages.forEach((m, i) => {
    const yy = msgY(i);
    const seq = i + 1;

    if (m.kind === "self") {
      const cx = centers[m.from];
      const bw = Math.min(laneW * 1.7, 2.5);
      slide.addShape("roundRect", {
        x: cx - bw / 2,
        y: yy - pitch * 0.3,
        w: bw,
        h: Math.max(pitch * 0.62, 0.17),
        rectRadius: 0.04,
        fill: { color: m.fill || "FFFFFF" },
        line: { color: m.color || T.MUTED, width: 0.75 },
      });
      slide.addText(`${seq}  ${m.text}`, {
        x: cx - bw / 2,
        y: yy - pitch * 0.3,
        w: bw,
        h: Math.max(pitch * 0.62, 0.17),
        fontFace: T.FONT,
        fontSize: msgFontSize - 0.5,
        color: T.INK,
        align: "center",
        valign: "middle",
        margin: 1,
      });
      return;
    }

    const x1 = centers[m.from];
    const x2 = centers[m.to];
    const leftward = x2 < x1;
    const ax = Math.min(x1, x2);
    const aw = Math.abs(x2 - x1);

    const isReturn = m.kind === "return";
    const stroke = m.color || (isReturn ? T.MUTED : m.kind === "db" ? T.BLUE : T.INK);

    slide.addShape("line", {
      x: ax,
      y: yy,
      w: aw,
      h: 0,
      flipH: leftward,
      line: {
        color: stroke,
        width: m.width || (isReturn ? 0.9 : 1.25),
        dashType: isReturn ? "dash" : "solid",
        endArrowType: "triangle",
      },
    });

    // label sits just above the arrow; the box is widened past the arrow run so
    // ordinary labels stay on a single line
    const padW = Math.max(aw, o.labelMinW || 2.6);
    const labX = ax + aw / 2 - padW / 2;
    slide.addText(
      [
        { text: `${seq}  `, options: { bold: true, color: T.MUTED } },
        { text: m.text, options: { bold: !!m.bold, color: m.textColor || T.INK } },
      ],
      {
        x: labX,
        y: yy - labelSpace - LABEL_CLEAR,
        w: padW,
        h: labelSpace,
        fontFace: T.FONT,
        fontSize: msgFontSize,
        align: "center",
        valign: "bottom",
        margin: 0,
        lineSpacingMultiple: 0.9,
      }
    );
  });
}

module.exports = { sequence };
