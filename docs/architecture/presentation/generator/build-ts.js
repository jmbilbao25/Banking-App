/**
 * QR Payment Platform — Solution Design
 * TechStart. 15 slides.
 *
 *   node build-ts.js  ->  out/TechStart-QR-Payment-Solution-Design.pptx
 */

const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");
const T = require("./ts-theme");

const SHOTS = path.join(__dirname, "shots_trimmed");
const OUT = path.join(__dirname, "out", "TechStart-QR-Payment-Solution-Design.pptx");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "TechStart";
pptx.company = "EastWest Bank";
pptx.title = "QR Payment Platform — Solution Design";

const BLUE = "3B6FD4";

let page = 0;
function slide(opts) {
  const s = pptx.addSlide();
  page += 1;
  T.chrome(s, page, opts);
  return s;
}

function box(s, o) {
  const {
    x, y, w, h, title, sub, fill = "FFFFFF", color = T.PURPLE,
    titleSize = 9, subSize = 7.2, radius = 0.06, dash,
  } = o;
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: radius,
    fill: { color: fill }, line: { color, width: 1.1, dashType: dash || "solid" },
  });
  const parts = [{ text: title, options: { bold: true, breakLine: !!sub, fontSize: titleSize } }];
  if (sub) parts.push({ text: sub, options: { fontSize: subSize, color: T.MUTED } });
  s.addText(parts, {
    x, y, w, h, fontFace: T.FONT, align: "center", valign: "middle",
    margin: 2, color: T.INK, lineSpacingMultiple: 0.9,
  });
}

function diamond(s, o) {
  const { x, y, w, h, title, sub, fill = "FFF6E5", color = T.AMBER } = o;
  s.addShape("diamond", { x, y, w, h, fill: { color }, line: { type: "none" } });
  s.addShape("diamond", {
    x: x + 0.045, y: y + 0.045, w: w - 0.09, h: h - 0.09,
    fill: { color: fill }, line: { type: "none" },
  });
  const parts = [{ text: title, options: { bold: true, breakLine: !!sub, fontSize: 8 } }];
  if (sub) parts.push({ text: sub, options: { fontSize: 7, color: T.MUTED } });
  s.addText(parts, {
    x, y: y + h * 0.28, w, h: h * 0.44,
    fontFace: T.FONT, align: "center", valign: "middle", margin: 0,
    color: T.INK, lineSpacingMultiple: 0.88,
  });
}

function link(s, x1, y1, x2, y2, o = {}) {
  s.addShape("line", {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1,
    line: {
      color: o.color || T.PURPLE,
      width: o.width || 1.1,
      dashType: o.dash || "solid",
      endArrowType: o.arrow === false ? "none" : "triangle",
      beginArrowType: o.both ? "triangle" : "none",
    },
  });
}

function tag(s, x, y, w, text, color) {
  s.addShape("roundRect", {
    x, y, w, h: 0.2, rectRadius: 0.1,
    fill: { color: "FFFFFF" }, line: { color, width: 0.9 },
  });
  s.addText(text, {
    x, y, w, h: 0.2, fontFace: T.FONT, fontSize: 6.8, bold: true,
    color, align: "center", valign: "middle", margin: 0,
  });
}

/** numbered list with coloured discs */
function numbered(s, x, y, w, items, opts = {}) {
  const pitch = opts.pitch || 0.42;
  const size = opts.fontSize || 10.5;
  items.forEach((it, i) => {
    const yy = y + i * pitch;
    s.addShape("ellipse", {
      x, y: yy + 0.03, w: 0.28, h: 0.28,
      fill: { color: opts.color || T.PURPLE }, line: { type: "none" },
    });
    s.addText(String(i + 1), {
      x, y: yy + 0.03, w: 0.28, h: 0.28,
      fontFace: T.FONT, fontSize: 9, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0,
    });
    const isObj = typeof it === "object";
    const head = isObj ? it.t : it;
    const tail = isObj ? it.d : null;
    s.addText(
      [
        { text: head, options: { bold: true, color: T.INK, fontSize: size } },
        ...(tail ? [{ text: `  ${tail}`, options: { color: T.MUTED, fontSize: size - 1 } }] : []),
      ],
      {
        x: x + 0.4, y: yy, w: w - 0.4, h: pitch - 0.04,
        fontFace: T.FONT, margin: 0, valign: "middle", lineSpacingMultiple: 0.95,
      }
    );
  });
}

/* ═══════════════ 1 · Title ═══════════════ */
{
  const s = pptx.addSlide();
  page = 1;

  if (fs.existsSync(T.BANNER_PNG)) {
    const { w: bw, h: bh } = T.pngSize(T.BANNER_PNG);
    const h = 13.333 * (bh / bw);
    s.addImage({ path: T.BANNER_PNG, x: 0, y: 0, w: 13.333, h });
  } else {
    T.ribbon(s);
  }

  s.addText(
    [
      { text: "QR Payment Platform", options: { bold: true, fontSize: 36, breakLine: true, color: T.PURPLE_DK } },
      { text: "Solution Design", options: { fontSize: 21, color: T.MAGENTA } },
    ],
    { x: 0.62, y: 4.0, w: 9.0, h: 1.4, fontFace: T.FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.14 }
  );

  s.addShape("rect", { x: 0.62, y: 5.5, w: 1.0, h: 0.06, fill: { color: T.LIME }, line: { type: "none" } });

  s.addText("Presented by TechStart", {
    x: 0.62, y: 5.74, w: 9.0, h: 0.3,
    fontFace: T.FONT, fontSize: 13, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });
  s.addText("Merchant QR generation  ·  Bank-side scanning and authorisation  ·  Posting in the core banking system", {
    x: 0.62, y: 6.06, w: 10.5, h: 0.3,
    fontFace: T.FONT, fontSize: 10.5, color: T.MUTED, margin: 0, valign: "middle",
  });

  T.chrome(s, 1, {});

  s.addNotes(
    "Solution design for a QR payment capability. The merchant channel generates the QR, " +
      "the banking channel scans and authorises it, and the core banking system performs " +
      "the posting. Four platform topics follow: availability, scalability, observability " +
      "and regulatory alignment."
  );
}

/* ═══════════════ 2 · Solution Overview ═══════════════ */
{
  const s = slide({ kicker: "Overview", title: "Solution overview" });

  const cards = [
    { t: "Merchant channel", l: ["Customer checks out", "Order is created", "QR code is generated"], a: BLUE },
    { t: "Banking channel", l: ["Customer scans the QR", "Reviews the order", "Authorises the payment"], a: T.MAGENTA },
    { t: "Core banking", l: ["Funds transfer is posted", "Balances are updated", "Reference is returned"], a: T.PURPLE },
    { t: "Confirmation", l: ["Order is marked paid", "Merchant is notified", "Receipt is shown"], a: T.GREEN },
  ];
  cards.forEach((c, i) => {
    T.card(s, {
      x: T.CX + i * 3.11, y: 1.6, w: 2.87, h: 2.35,
      title: c.t, lines: c.l, accent: c.a, num: i + 1, titleSize: 12, bodySize: 10,
    });
  });

  cards.slice(0, 3).forEach((_, i) => {
    link(s, T.CX + 2.87 + i * 3.11 + 0.02, 2.78, T.CX + (i + 1) * 3.11 - 0.02, 2.78, { color: T.MUTED, width: 1.2 });
  });

  s.addShape("roundRect", {
    x: T.CX, y: 4.34, w: T.CW, h: 1.9, rectRadius: 0.06,
    fill: { color: T.ALT }, line: { color: T.PURPLE, width: 1 },
  });
  s.addText("Design principle", {
    x: T.CX + 0.24, y: 4.52, w: 5.0, h: 0.3,
    fontFace: T.FONT, fontSize: 12, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });
  s.addText(
    "The merchant channel never holds funds and never moves money. It generates a QR that " +
      "references an order. Every debit, credit and balance stays inside the core banking system.",
    {
      x: T.CX + 0.24, y: 4.88, w: 11.6, h: 0.6,
      fontFace: T.FONT, fontSize: 11.5, color: T.INK, margin: 0, valign: "top", lineSpacingMultiple: 1.08,
    }
  );

  const chips = [
    ["QR is single-use", T.MAGENTA],
    ["Time-bound — 300 s", T.PURPLE],
    ["Customer authenticates first", BLUE],
    ["Posting happens in T24", T.GREEN],
  ];
  chips.forEach((c, i) => {
    T.pill(s, T.CX + 0.24 + i * 2.95, 5.66, 2.75, c[0], c[1]);
  });

  s.addNotes("One minute. The design principle line is the important one.");
}

/* ═══════════════ 3 · Business Requirements ═══════════════ */
{
  const s = slide({ kicker: "Scope", title: "Business requirements" });

  numbered(
    s, T.CX, 1.8, 7.5,
    [
      { t: "E-Commerce generates the QR", d: "at checkout, from the order" },
      { t: "Banking app scans the QR", d: "to initiate the payment" },
      { t: "Core banking performs the posting", d: "debit payer, credit merchant" },
      { t: "QR is single-use and time-bound", d: "expires after 300 seconds" },
      { t: "Customer authenticates before authorising", d: "" },
      { t: "Merchant is notified on confirmation", d: "" },
      { t: "Order and payment are traceable end to end", d: "" },
    ],
    { pitch: 0.6, fontSize: 11.5 }
  );

  s.addShape("roundRect", {
    x: 8.4, y: 1.7, w: 4.38, h: 4.26, rectRadius: 0.06,
    fill: { color: "FFFFFF" }, line: { color: T.MAGENTA, width: 1.3 },
  });
  s.addShape("rect", { x: 8.4, y: 1.7, w: 4.38, h: 0.06, fill: { color: T.MAGENTA }, line: { type: "none" } });
  s.addText("The core requirement", {
    x: 8.58, y: 1.9, w: 4.0, h: 0.34,
    fontFace: T.FONT, fontSize: 12.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });

  box(s, { x: 8.62, y: 2.44, w: 3.94, h: 0.74, title: "E-Commerce", sub: "generates the QR", fill: "EEF4FF", color: BLUE, titleSize: 11, subSize: 9 });
  link(s, 10.59, 3.18, 10.59, 3.42);
  box(s, { x: 8.62, y: 3.42, w: 3.94, h: 0.74, title: "Banking App", sub: "scans the QR", fill: "FDF2F8", color: T.MAGENTA, titleSize: 11, subSize: 9 });
  link(s, 10.59, 4.16, 10.59, 4.4);
  box(s, { x: 8.62, y: 4.4, w: 3.94, h: 0.8, title: "T24 — Core Banking", sub: "performs the business logic and posting", fill: "F3EEFB", color: T.PURPLE, titleSize: 11, subSize: 9 });

  s.addText("The bank remains the system of record.", {
    x: 8.62, y: 5.34, w: 3.94, h: 0.3,
    fontFace: T.FONT, fontSize: 10, italic: true, color: T.MUTED,
    align: "center", valign: "middle", margin: 0,
  });

  s.addNotes(
    "Read requirement 1 to 3 as one sentence: the merchant generates, the bank scans, " +
      "and the core banking system posts."
  );
}

/* ═══════════════ 4 · Assumptions ═══════════════ */
{
  const s = slide({ kicker: "Scope", title: "Assumptions" });

  T.table(
    s,
    [
      ["#", "Assumption"],
      ["1", { text: "There are no budget constraints on the solution.", bold: true }],
      ["2", "A third-party payment gateway can provide this capability. This design assumes an in-house build using the bank's own channels and core system."],
      ["3", { text: "E-Commerce is the QR generator only. It never holds funds and never moves money.", bold: true }],
      ["4", { text: "The banking app is the scanning and authorisation channel only.", bold: true }],
      ["5", { text: "All business logic, posting and balances remain in the core banking system.", bold: true }],
      ["6", "The core banking system is T24."],
      ["7", "The existing microservice and API management layer can be reused for the integration."],
      ["8", "Volumes are pilot scale. A production throughput target will be set separately."],
    ],
    { y: 1.66, w: 8.5, colW: [0.45, 8.05], fontSize: 10.5, rowH: 0.5 }
  );

  T.card(s, {
    x: 9.28, y: 1.66, w: 3.5, h: 2.15,
    title: "Build vs buy",
    lines: [
      "A gateway would shorten delivery",
      "An in-house build keeps the ledger and the customer journey inside the bank",
    ],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11.5, bodySize: 10,
  });

  T.card(s, {
    x: 9.28, y: 3.98, w: 3.5, h: 2.1,
    title: "Boundary",
    lines: [
      "Channels present and capture",
      "T24 decides and records",
      "Nothing settles outside the core",
    ],
    accent: T.PURPLE, fill: T.ALT, titleSize: 11.5, bodySize: 10,
  });

  s.addNotes("Assumption 1 and 6 are the two to confirm in the room.");
}

/* ═══════════════ 5 · User Flow ═══════════════ */
{
  const s = slide({ kicker: "Journey", title: "User flow" });

  const rA = 1.72;
  const h1 = 0.5;

  s.addShape("roundRect", {
    x: 0.6, y: rA, w: 0.85, h: h1, rectRadius: 0.06,
    fill: { color: T.PURPLE }, line: { type: "none" },
  });
  s.addText("User", {
    x: 0.6, y: rA, w: 0.85, h: h1,
    fontFace: T.FONT, fontSize: 9.5, bold: true, color: "FFFFFF",
    align: "center", valign: "middle", margin: 0,
  });

  box(s, { x: 1.72, y: rA, w: 1.95, h: h1, title: "E-Commerce Checkout", sub: "items + total", fill: "EEF4FF", color: BLUE });
  box(s, { x: 3.94, y: rA, w: 1.95, h: h1, title: "Generate QR", sub: "valid 5 minutes", fill: "EEF4FF", color: BLUE });
  box(s, { x: 6.16, y: rA, w: 1.55, h: h1, title: "Scan QR", fill: "FDF2F8", color: T.MAGENTA });
  diamond(s, { x: 8.05, y: rA - 0.16, w: 1.6, h: 0.82, title: "QR valid?" });

  link(s, 1.45, rA + 0.25, 1.72, rA + 0.25);
  link(s, 3.67, rA + 0.25, 3.94, rA + 0.25);
  link(s, 5.89, rA + 0.25, 6.16, rA + 0.25);
  link(s, 7.71, rA + 0.25, 8.05, rA + 0.25);

  link(s, 9.65, rA + 0.25, 10.5, rA + 0.25, { color: T.AMBER });
  tag(s, 9.83, rA - 0.06, 0.44, "NO", T.AMBER);
  box(s, { x: 10.5, y: rA, w: 2.0, h: h1, title: "Back to store", sub: "get a new QR", fill: "FFF6E5", color: T.AMBER });

  const rB = 3.12;
  link(s, 8.85, rA + 0.66, 8.85, rB - 0.16, { color: T.GREEN });
  tag(s, 8.92, rA + 0.8, 0.46, "YES", T.GREEN);

  diamond(s, { x: 8.05, y: rB - 0.16, w: 1.6, h: 0.82, title: "Logged in?", fill: "EFF8F0", color: T.GREEN });

  box(s, { x: 5.3, y: rB, w: 2.1, h: h1, title: "Payment Details", sub: "items + total", fill: "F3EEFB", color: T.PURPLE });
  link(s, 8.05, rB + 0.2, 7.4, rB + 0.2, { color: T.GREEN });
  tag(s, 7.5, rB - 0.24, 0.62, "YES", T.GREEN);

  box(s, { x: 9.9, y: rB, w: 1.7, h: h1, title: "Login", fill: "EFF8F0", color: T.GREEN });
  link(s, 9.65, rB + 0.25, 9.9, rB + 0.25, { color: T.GREEN });
  tag(s, 9.62, rB - 0.28, 1.0, "NOT YET", T.GREEN);

  link(s, 10.75, rB + h1, 10.75, 4.0, { color: T.GREEN, arrow: false });
  link(s, 10.75, 4.0, 6.9, 4.0, { color: T.GREEN, arrow: false });
  link(s, 6.9, 4.0, 6.9, rB + h1, { color: T.GREEN });

  link(s, 6.0, rB + h1, 6.0, 4.24, { arrow: false, color: T.PURPLE });
  link(s, 6.0, 4.24, 5.15, 4.24, { arrow: false, color: T.PURPLE });
  link(s, 5.15, 4.24, 5.15, 4.56, { color: BLUE });
  link(s, 6.0, 4.24, 7.45, 4.24, { arrow: false, color: T.PURPLE });
  link(s, 7.45, 4.24, 7.45, 4.56, { color: T.AMBER });

  const chains = [
    { x: 4.3, col: BLUE, fill: "EEF4FF", steps: ["Confirm", "Post to T24", "Payment complete"], lastGreen: true },
    { x: 6.6, col: T.AMBER, fill: "FFF6E5", steps: ["Cancel", "No amount deducted", "QR scan screen"], lastGreen: false },
  ];
  chains.forEach((c) => {
    c.steps.forEach((st, i) => {
      const y = 4.56 + i * 0.72;
      const isLast = i === c.steps.length - 1;
      box(s, {
        x: c.x, y, w: 1.7, h: 0.46,
        title: st,
        fill: isLast && c.lastGreen ? "EFF8F0" : c.fill,
        color: isLast && c.lastGreen ? T.GREEN : c.col,
        titleSize: 8.5,
      });
      if (i < c.steps.length - 1) link(s, c.x + 0.85, y + 0.46, c.x + 0.85, y + 0.72, { color: c.col });
    });
  });

  T.card(s, {
    x: 9.0, y: 4.56, w: 3.78, h: 1.9,
    title: "Controls in the flow",
    lines: ["Expiry — 300 s", "Single use per order", "Status checked before posting", "Balance verified in core"],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11, bodySize: 9.5,
  });

  s.addNotes("Two outcomes: confirm posts to T24, cancel deducts nothing.");
}

/* ═══════════════ 6 · Solution Architecture — swimlane ═══════════════ */
{
  const s = slide({
    kicker: "Architecture",
    title: "Solution architecture",
    subtitle: "Channels present and capture. The core banking system decides and records.",
  });

  const lanes = [
    { n: "E-Commerce", c: BLUE, f: "EEF4FF" },
    { n: "Banking App", c: T.MAGENTA, f: "FDF2F8" },
    { n: "Microservice / APIM", c: T.PURPLE, f: "F3EEFB" },
    { n: "T24 — Core Banking", c: T.GREEN, f: "EFF8F0" },
  ];
  const x0 = 0.55;
  const lw = 12.23 / 4;
  const laneTop = 1.66;
  const laneBot = 6.4;

  lanes.forEach((l, i) => {
    const lx = x0 + lw * i;
    s.addShape("rect", {
      x: lx, y: laneTop, w: lw, h: 0.4,
      fill: { color: l.c }, line: { color: "FFFFFF", width: 1 },
    });
    s.addText(l.n, {
      x: lx, y: laneTop, w: lw, h: 0.4,
      fontFace: T.FONT, fontSize: 11, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0,
    });
    s.addShape("rect", {
      x: lx, y: laneTop + 0.4, w: lw, h: laneBot - laneTop - 0.4,
      fill: { color: i % 2 ? "FBFAFC" : "FFFFFF" },
      line: { color: T.HAIR, width: 0.75 },
    });
  });

  const cx = (i) => x0 + lw * i + lw / 2;
  const bw = 2.5;
  const bh = 0.5;
  const rows = [2.32, 3.06, 3.8, 4.54, 5.4];

  // lane 2 is narrowed and left-shifted so the datastore fits inside its own lane
  const L2X = 6.8;
  const L2W = 2.28;
  const L2R = L2X + L2W;
  const DBX = 9.16;

  // r1 create order
  box(s, { x: cx(0) - bw / 2, y: rows[0], w: bw, h: bh, title: "Create order", sub: "items + total", fill: "EEF4FF", color: BLUE, titleSize: 9.5 });
  box(s, { x: L2X, y: rows[0], w: L2W, h: bh, title: "Create Order API", fill: "F3EEFB", color: T.PURPLE, titleSize: 9.5 });
  link(s, cx(0) + bw / 2, rows[0] + bh / 2, L2X, rows[0] + bh / 2);

  // datastore, inside the microservice lane
  s.addShape("can", {
    x: DBX, y: rows[0] + 0.01, w: 0.5, h: 0.48,
    fill: { color: "FFFFFF" }, line: { color: T.PURPLE, width: 1.1 },
  });
  s.addText("Azure DB", {
    x: DBX - 0.14, y: rows[0] + 0.5, w: 0.78, h: 0.18,
    fontFace: T.FONT, fontSize: 7, color: T.MUTED, align: "center", valign: "middle", margin: 0,
  });
  link(s, L2R, rows[0] + bh / 2, DBX, rows[0] + bh / 2, { color: T.PURPLE });

  // r2 QR
  box(s, { x: L2X, y: rows[1], w: L2W, h: bh, title: "Return QR payload", fill: "F3EEFB", color: T.PURPLE, titleSize: 9.5 });
  box(s, { x: cx(0) - bw / 2, y: rows[1], w: bw, h: bh, title: "Display QR", fill: "EEF4FF", color: BLUE, titleSize: 9.5 });
  link(s, L2X, rows[1] + bh / 2, cx(0) + bw / 2, rows[1] + bh / 2);

  // r3 scan
  box(s, { x: cx(1) - bw / 2, y: rows[2], w: bw, h: bh, title: "Scan QR", fill: "FDF2F8", color: T.MAGENTA, titleSize: 9.5 });
  box(s, { x: L2X, y: rows[2], w: L2W, h: bh, title: "Get Order API", fill: "F3EEFB", color: T.PURPLE, titleSize: 9.5 });
  link(s, cx(1) + bw / 2, rows[2] + bh / 2 - 0.08, L2X, rows[2] + bh / 2 - 0.08);
  link(s, L2X, rows[2] + bh / 2 + 0.1, cx(1) + bw / 2, rows[2] + bh / 2 + 0.1, { dash: "dash", color: T.MUTED });

  // r4 confirm + post
  box(s, { x: cx(1) - bw / 2, y: rows[3], w: bw, h: bh, title: "Confirm payment", fill: "FDF2F8", color: T.MAGENTA, titleSize: 9.5 });
  box(s, { x: L2X, y: rows[3], w: L2W, h: bh, title: "Payment API", fill: "F3EEFB", color: T.PURPLE, titleSize: 9.5 });
  box(s, { x: cx(3) - bw / 2, y: rows[3], w: bw, h: bh, title: "Funds Transfer posting", sub: "debit payer · credit merchant", fill: "EFF8F0", color: T.GREEN, titleSize: 9.5, subSize: 7.5 });
  link(s, cx(1) + bw / 2, rows[3] + bh / 2, L2X, rows[3] + bh / 2);
  link(s, L2R, rows[3] + bh / 2, cx(3) - bw / 2, rows[3] + bh / 2);

  // r5 confirm back
  box(s, { x: cx(3) - bw / 2, y: rows[4], w: bw, h: bh, title: "Posting reference", fill: "EFF8F0", color: T.GREEN, titleSize: 9.5 });
  box(s, { x: L2X, y: rows[4], w: L2W, h: bh, title: "Update order status", fill: "F3EEFB", color: T.PURPLE, titleSize: 9.5 });
  box(s, { x: cx(0) - bw / 2, y: rows[4], w: bw, h: bh, title: "Order marked PAID", fill: "EFF8F0", color: T.GREEN, titleSize: 9.5 });
  link(s, cx(3) - bw / 2, rows[4] + bh / 2, L2R, rows[4] + bh / 2, { dash: "dash", color: T.MUTED });
  link(s, L2X, rows[4] + bh / 2, cx(0) + bw / 2, rows[4] + bh / 2, { dash: "dash", color: T.MUTED });

  s.addNotes(
    "Five rows. Note the only lane that touches money is T24, on row four. " +
      "Solid arrows are requests, dashed are responses."
  );
}

/* ═══════════════ 7 · System Interfaces ═══════════════ */
{
  const s = slide({
    kicker: "Interfaces",
    title: "System interfaces",
    subtitle: "Channels reach the core banking system through API management and a site-to-site link.",
  });

  // Azure zone
  s.addShape("roundRect", {
    x: 0.55, y: 1.72, w: 12.23, h: 2.16, rectRadius: 0.06,
    fill: { color: "F5F9FF" }, line: { color: BLUE, width: 1.2, dashType: "dash" },
  });
  s.addText("Azure Cloud", {
    x: 0.72, y: 1.8, w: 3.0, h: 0.24,
    fontFace: T.FONT, fontSize: 9.5, bold: true, color: "0D47A1", margin: 0, valign: "middle",
  });

  const azure = [
    ["Channels", "web + mobile"],
    ["WAF", "filters traffic"],
    ["API Gateway", "APIM, token check"],
    ["Ingress", "controller"],
    ["Microservice", "AKS"],
    ["Database", "Azure SQL"],
  ];
  const aw = 1.82;
  azure.forEach((a, i) => {
    const x = 0.78 + i * 2.0;
    box(s, {
      x, y: 2.16, w: aw, h: 0.66,
      title: a[0], sub: a[1],
      fill: "FFFFFF", color: i === 0 ? T.MUTED : BLUE, titleSize: 9.5, subSize: 7.5,
    });
    if (i < azure.length - 1) link(s, x + aw, 2.49, x + 2.0, 2.49, { color: BLUE });
  });

  s.addText("TLS in transit  ·  no workload endpoint published directly to the internet", {
    x: 0.78, y: 3.0, w: 11.8, h: 0.24,
    fontFace: T.FONT, fontSize: 9, italic: true, color: T.MUTED, margin: 0, valign: "middle",
  });

  link(s, 6.1, 3.88, 6.1, 4.3, { color: T.PURPLE, width: 1.6, both: true });
  s.addText("Site-to-Site VPN", {
    x: 6.28, y: 3.94, w: 2.4, h: 0.28,
    fontFace: T.FONT, fontSize: 10, bold: true, color: T.PURPLE,
    valign: "middle", margin: 0,
  });

  // On-prem zone
  s.addShape("roundRect", {
    x: 0.55, y: 4.38, w: 12.23, h: 2.0, rectRadius: 0.06,
    fill: { color: "F7F5FA" }, line: { color: T.PURPLE, width: 1.2, dashType: "dash" },
  });
  s.addText("On-Premises Data Centre", {
    x: 0.72, y: 4.46, w: 4.0, h: 0.24,
    fontFace: T.FONT, fontSize: 9.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });

  const onprem = [
    ["NGFW", "perimeter firewall"],
    ["Load balancer", "distributes calls"],
    ["JBoss", "application server"],
    ["T24", "core banking"],
  ];
  const ow = 2.6;
  onprem.forEach((o, i) => {
    const x = 1.35 + i * 2.85;
    box(s, {
      x, y: 4.82, w: ow, h: 0.7,
      title: o[0], sub: o[1],
      fill: "FFFFFF", color: i === 3 ? T.GREEN : T.PURPLE,
      titleSize: 10, subSize: 8,
    });
    if (i < onprem.length - 1) link(s, x + ow, 5.17, x + 2.85, 5.17, { color: T.PURPLE });
  });

  s.addText("T24 remains the system of record for accounts, balances and postings", {
    x: 1.35, y: 5.66, w: 11.2, h: 0.24,
    fontFace: T.FONT, fontSize: 9, italic: true, color: T.MUTED, margin: 0, valign: "middle",
  });

  s.addNotes("Two zones, one link. The channels never talk to T24 directly.");
}

/* ═══════════════ 8 · Network and Remote Access ═══════════════ */
{
  const s = slide({
    kicker: "Network",
    title: "Network and remote access",
    subtitle: "Private connectivity between the Azure workload and the on-premises core.",
  });

  box(s, { x: 0.62, y: 3.0, w: 1.8, h: 0.8, title: "Customer", sub: "phone or browser", fill: "FFFFFF", color: T.MUTED, titleSize: 10, subSize: 8 });

  s.addShape("roundRect", {
    x: 2.9, y: 1.72, w: 5.0, h: 4.55, rectRadius: 0.06,
    fill: { color: "F5F9FF" }, line: { color: BLUE, width: 1.2, dashType: "dash" },
  });
  s.addText("Azure — spoke virtual network", {
    x: 3.06, y: 1.8, w: 4.5, h: 0.24,
    fontFace: T.FONT, fontSize: 9.5, bold: true, color: "0D47A1", margin: 0, valign: "middle",
  });
  const az = [
    ["Front door + WAF", "public entry point"],
    ["API Management", "internal only"],
    ["AKS private cluster", "no public API server"],
    ["Private endpoints", "database and secrets"],
    ["VPN gateway", "to the data centre"],
  ];
  az.forEach((a, i) => {
    const y = 2.2 + i * 0.78;
    box(s, { x: 3.14, y, w: 4.55, h: 0.6, title: a[0], sub: a[1], fill: "FFFFFF", color: BLUE, titleSize: 9.5, subSize: 7.5 });
    if (i < az.length - 1) link(s, 5.42, y + 0.6, 5.42, y + 0.78, { color: BLUE });
  });
  // customer enters at the public front door, not mid-stack
  link(s, 2.42, 3.4, 2.78, 3.4, { color: T.MUTED, arrow: false });
  link(s, 2.78, 3.4, 2.78, 2.5, { color: T.MUTED, arrow: false });
  link(s, 2.78, 2.5, 3.14, 2.5, { color: T.MUTED });

  s.addShape("roundRect", {
    x: 8.4, y: 1.72, w: 4.38, h: 4.55, rectRadius: 0.06,
    fill: { color: "F7F5FA" }, line: { color: T.PURPLE, width: 1.2, dashType: "dash" },
  });
  s.addText("On-premises data centre", {
    x: 8.56, y: 1.8, w: 4.0, h: 0.24,
    fontFace: T.FONT, fontSize: 9.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });
  const op = [
    ["VPN gateway", "terminates the tunnel"],
    ["NGFW", "inspects the traffic"],
    ["T24 application servers", "JBoss"],
    ["T24 core banking", "system of record"],
  ];
  op.forEach((o, i) => {
    const y = 2.4 + i * 0.9;
    box(s, {
      x: 8.62, y, w: 3.94, h: 0.66,
      title: o[0], sub: o[1],
      fill: "FFFFFF", color: i === 3 ? T.GREEN : T.PURPLE, titleSize: 9.5, subSize: 7.5,
    });
    if (i < op.length - 1) link(s, 10.59, y + 0.66, 10.59, y + 0.9, { color: T.PURPLE });
  });

  link(s, 7.9, 4.9, 8.4, 4.9, { color: T.PURPLE, width: 1.8, both: true });
  s.addText("S2S VPN", {
    x: 7.78, y: 4.56, w: 0.74, h: 0.24,
    fontFace: T.FONT, fontSize: 7.5, bold: true, color: T.PURPLE,
    align: "center", valign: "middle", margin: 0,
  });

  T.footnote(s, "Redundant tunnels are used so the link to the core is not a single point of failure.", 6.44);
  s.addNotes("Point at the VPN: redundant tunnels, and the AKS API server is private.");
}

/* ═══════════════ 9 · Application walkthrough ═══════════════ */
{
  const s = slide({ kicker: "Demo", title: "The application" });

  const shots = [
    ["01-ecom-store.png", "Merchant catalogue"],
    ["03-ecom-checkout-qr.png", "QR presented at checkout"],
    ["05-bank-pay-form.png", "Authorising in the bank app"],
  ];
  const bw = 3.9;
  shots.forEach(([f, cap], i) => {
    const x = T.CX + i * 4.06;
    s.addText(cap, {
      x, y: 1.56, w: bw, h: 0.26,
      fontFace: T.FONT, fontSize: 10.5, bold: true, color: T.PURPLE_DK,
      align: "center", valign: "middle", margin: 0,
    });
    T.image(s, path.join(SHOTS, f), x, 1.9, bw, 4.45, { valign: "top" });
  });

  s.addNotes("Thirty seconds — show that the journey works, then move to the platform topics.");
}

/* ═══════════════ 10 · Payment sequence ═══════════════ */
{
  const s = slide({ kicker: "Runtime", title: "Payment sequence" });

  const lanes = [
    { n: "Customer", c: T.MUTED, f: "FFFFFF" },
    { n: "E-Commerce", c: BLUE, f: "EEF4FF" },
    { n: "Banking App", c: T.MAGENTA, f: "FDF2F8" },
    { n: "Microservice", c: T.PURPLE, f: "F3EEFB" },
    { n: "T24", c: T.GREEN, f: "EFF8F0" },
  ];
  const x0 = 0.8;
  const lw = 2.32;
  const cxs = lanes.map((_, i) => x0 + lw * i + lw / 2);

  lanes.forEach((l, i) => {
    s.addShape("roundRect", {
      x: x0 + lw * i + 0.14, y: 1.62, w: lw - 0.28, h: 0.42, rectRadius: 0.05,
      fill: { color: l.f }, line: { color: l.c, width: 1.2 },
    });
    s.addText(l.n, {
      x: x0 + lw * i + 0.14, y: 1.62, w: lw - 0.28, h: 0.42,
      fontFace: T.FONT, fontSize: 10, bold: true, color: T.INK,
      align: "center", valign: "middle", margin: 0,
    });
    s.addShape("line", {
      x: cxs[i], y: 2.04, w: 0, h: 4.1,
      line: { color: "AAAAAA", width: 0.75, dashType: "dash" },
    });
  });

  const msgs = [
    [0, 1, "checkout", false],
    [1, 0, "QR displayed", true],
    [0, 2, "scan and log in", false],
    [2, 3, "get order details", false],
    [3, 2, "items and total", true],
    [2, 3, "confirm payment", false],
    [3, 4, "post funds transfer", false],
    [4, 3, "posting reference", true],
    [3, 1, "order marked paid", false],
    [2, 0, "receipt", true],
  ];

  const y0 = 2.5;
  const pitch = 0.4;
  msgs.forEach(([a, b, txt, ret], i) => {
    const yy = y0 + pitch * i;
    const isPost = txt.indexOf("funds transfer") >= 0;
    const col = isPost ? T.GREEN : ret ? T.MUTED : T.PURPLE_DK;
    s.addShape("line", {
      x: Math.min(cxs[a], cxs[b]), y: yy, w: Math.abs(cxs[b] - cxs[a]), h: 0,
      flipH: cxs[b] < cxs[a],
      line: {
        color: col, width: isPost ? 1.7 : 1.15,
        dashType: ret ? "dash" : "solid", endArrowType: "triangle",
      },
    });
    const padW = Math.max(Math.abs(cxs[b] - cxs[a]), 2.5);
    s.addText(
      [
        { text: `${i + 1}  `, options: { bold: true, color: T.MUTED } },
        { text: txt, options: { bold: isPost, color: col } },
      ],
      {
        x: (cxs[a] + cxs[b]) / 2 - padW / 2, y: yy - 0.3, w: padW, h: 0.25,
        fontFace: T.FONT, fontSize: 9.5, align: "center", valign: "bottom", margin: 0,
      }
    );
  });

  s.addText("Step 7 is the only step that moves money, and it happens inside T24.", {
    x: 0.8, y: 6.32, w: 11.8, h: 0.28,
    fontFace: T.FONT, fontSize: 10, bold: true, color: T.GREEN, margin: 0, valign: "middle",
  });

  s.addNotes("Ten steps. Land on step 7.");
}

/* ═══════════════ 11 · High Availability ═══════════════ */
{
  const s = slide({ kicker: "Topic 1 of 4", title: "High availability" });

  const items = [
    { t: "Application tier", d: "Two or more replicas spread across availability zones, behind a health-probed ingress", a: BLUE },
    { t: "Data tier", d: "Zone-redundant managed database with automated backup and point-in-time restore", a: T.PURPLE },
    { t: "Deployment", d: "Rolling updates gated on readiness probes, so a release does not interrupt service", a: T.MAGENTA },
    { t: "Core banking link", d: "Redundant site-to-site tunnels between Azure and the data centre", a: T.GREEN },
  ];
  items.forEach((it, i) => {
    const y = 1.66 + i * 1.12;
    s.addShape("roundRect", {
      x: T.CX, y, w: 8.2, h: 0.98, rectRadius: 0.06,
      fill: { color: "FFFFFF" }, line: { color: it.a, width: 1.2 },
    });
    s.addShape("rect", { x: T.CX, y, w: 0.07, h: 0.98, fill: { color: it.a }, line: { type: "none" } });
    s.addText(it.t, {
      x: T.CX + 0.24, y: y + 0.12, w: 7.7, h: 0.32,
      fontFace: T.FONT, fontSize: 12.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
    });
    s.addText(it.d, {
      x: T.CX + 0.24, y: y + 0.46, w: 7.7, h: 0.44,
      fontFace: T.FONT, fontSize: 10.5, color: T.INK, margin: 0, valign: "top",
    });
  });

  s.addShape("roundRect", {
    x: 9.1, y: 1.66, w: 3.68, h: 4.34, rectRadius: 0.06,
    fill: { color: T.ALT }, line: { color: T.PURPLE, width: 1.2 },
  });
  s.addText("Availability targets", {
    x: 9.3, y: 1.88, w: 3.3, h: 0.3,
    fontFace: T.FONT, fontSize: 12.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });
  T.stat(s, 9.3, 2.42, 3.3, "99.9%", "service availability", T.MAGENTA);
  T.stat(s, 9.3, 3.52, 3.3, "5 min", "recovery point objective", T.PURPLE);
  T.stat(s, 9.3, 4.62, 3.3, "1 hour", "recovery time objective", T.GREEN);

  T.footnote(s, "Recovery objectives to be confirmed and signed off before build.", 6.16);
  s.addNotes("The three numbers are the ask for sign-off.");
}

/* ═══════════════ 12 · Scalability ═══════════════ */
{
  const s = slide({ kicker: "Topic 2 of 4", title: "Scalability on Kubernetes" });

  box(s, { x: 0.62, y: 1.78, w: 1.9, h: 0.8, title: "Ingress", sub: "single entry, WAF", fill: "FFFFFF", color: BLUE, titleSize: 11, subSize: 8.5 });
  box(s, { x: 2.92, y: 1.78, w: 1.9, h: 0.8, title: "Service", sub: "ClusterIP", fill: "FFFFFF", color: BLUE, titleSize: 11, subSize: 8.5 });
  box(s, { x: 5.22, y: 1.78, w: 2.3, h: 0.8, title: "Pods", sub: "HPA scales 2 → N", fill: "EEF4FF", color: BLUE, titleSize: 11, subSize: 8.5 });
  box(s, { x: 7.92, y: 1.78, w: 2.1, h: 0.8, title: "Managed DB", sub: "private endpoint", fill: "FFFFFF", color: T.PURPLE, titleSize: 11, subSize: 8.5 });
  box(s, { x: 10.42, y: 1.78, w: 2.36, h: 0.8, title: "T24", sub: "over the S2S link", fill: "EFF8F0", color: T.GREEN, titleSize: 11, subSize: 8.5 });
  [2.52, 4.82, 7.52, 10.02].forEach((x, i) => {
    const nx = [2.92, 5.22, 7.92, 10.42][i];
    link(s, x, 2.18, nx, 2.18, { color: T.MUTED });
  });

  const cols = [
    {
      t: "How it scales", a: T.MAGENTA, fill: "FDF2F8",
      l: [
        "Horizontal Pod Autoscaler on CPU and requests per second",
        "Cluster autoscaler adds nodes when pods cannot be placed",
        "Pods are stateless, so any replica can serve any request",
      ],
    },
    {
      t: "What makes that possible", a: T.PURPLE, fill: T.ALT,
      l: [
        "Session state held outside the pod",
        "Configuration supplied by environment and secret store",
        "Connection pooling in front of the database",
      ],
    },
    {
      t: "Already in place", a: T.GREEN, fill: "F4FBF5",
      l: [
        "Deployment, Service and Secret manifests written",
        "Liveness and readiness probes defined",
        "Health endpoints exposed by both services",
      ],
    },
  ];
  cols.forEach((c, i) => {
    T.card(s, {
      x: T.CX + i * 4.14, y: 3.0, w: 3.95, h: 2.92,
      title: c.t, lines: c.l, accent: c.a, fill: c.fill,
      titleSize: 12.5, bodySize: 11, spaceAfter: 12,
    });
  });

  s.addNotes("The manifests already exist, which shortens the path to a managed cluster.");
}

/* ═══════════════ 13 · Observability ═══════════════ */
{
  const s = slide({ kicker: "Topic 3 of 4", title: "Observability" });

  const pillars = [
    { t: "Logs", d: "Structured JSON from every container, shipped to a Log Analytics workspace with a defined retention period.", a: T.PURPLE },
    { t: "Metrics", d: "Azure Monitor collects saturation, latency and error rate, surfaced on a workload dashboard.", a: T.MAGENTA },
    { t: "Traces", d: "OpenTelemetry with a correlation identifier carried across the channels, the microservice and the core.", a: BLUE },
  ];
  pillars.forEach((p, i) => {
    const x = T.CX + i * 4.14;
    s.addShape("roundRect", {
      x, y: 1.66, w: 3.95, h: 2.2, rectRadius: 0.06,
      fill: { color: "FFFFFF" }, line: { color: p.a, width: 1.25 },
    });
    s.addShape("rect", { x, y: 1.66, w: 3.95, h: 0.07, fill: { color: p.a }, line: { type: "none" } });
    s.addText(p.t, {
      x: x + 0.2, y: 1.86, w: 3.55, h: 0.36,
      fontFace: T.FONT, fontSize: 15, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
    });
    s.addText(p.d, {
      x: x + 0.2, y: 2.3, w: 3.55, h: 1.42,
      fontFace: T.FONT, fontSize: 10.5, color: T.INK, margin: 0, valign: "top", lineSpacingMultiple: 1.06,
    });
  });

  T.card(s, {
    x: T.CX, y: 4.14, w: 6.0, h: 2.1,
    title: "Health and self-healing",
    lines: [
      "Liveness and readiness probes enforced by the platform",
      "Unhealthy pods removed from rotation automatically",
      "Alerts routed to an on-call rota",
    ],
    accent: T.GREEN, fill: "F4FBF5", titleSize: 12, bodySize: 10.5,
  });

  T.card(s, {
    x: 6.79, y: 4.14, w: 5.99, h: 2.1,
    title: "What we can answer",
    lines: [
      "Where a specific payment reached, and how long each hop took",
      "Whether an error came from the channel, the microservice or the core",
      "Whether the service met its availability target this month",
    ],
    accent: T.PURPLE, fill: T.ALT, titleSize: 12, bodySize: 10.5,
  });

  s.addNotes("Frame as: a single payment can be followed across all four tiers.");
}

/* ═══════════════ 14 · BSP compliance ═══════════════ */
{
  const s = slide({ kicker: "Topic 4 of 4", title: "BSP and regulatory alignment" });

  T.table(
    s,
    [
      ["Instrument", "Requirement", "How the design responds"],
      ["Circular 1055", "National QR code standard — QR Ph", "EMVCo-format payload with a signed order reference"],
      ["Circular 1198", "Merchant payment acceptance", "Merchant onboarding, settlement and dispute handling in the core"],
      ["MORB Appendix 75", "Information security risk management", "TLS in transit, keys in Key Vault and HSM, immutable audit trail"],
      ["Circular 1140", "Technology outsourcing risk", "Documented exit strategy, portable stack, continuity plan"],
      ["RA 10173", "Data privacy and residency", "In-country archive copy; cross-border basis to be documented"],
      ["RA 9160", "Anti-money laundering reporting", "Covered and suspicious transaction reporting from the core"],
    ],
    { y: 1.66, colW: [2.0, 4.35, 5.88], fontSize: 10.5, rowH: 0.46 }
  );

  T.card(s, {
    x: T.CX, y: 5.06, w: 6.0, h: 1.26,
    title: "Confirmed with Compliance and Legal",
    lines: [
      "The cross-border transfer basis and the licensing position are decided outside engineering",
    ],
    accent: T.PURPLE, fill: T.ALT, titleSize: 11.5, bodySize: 10,
  });

  T.card(s, {
    x: 6.79, y: 5.06, w: 5.99, h: 1.26,
    title: "Standing position",
    lines: ["The core banking system remains the record for every posting and balance"],
    accent: T.GREEN, fill: "F4FBF5", titleSize: 11.5, bodySize: 10,
  });

  T.footnote(s, "Engineering mapping for discussion. Citations to be confirmed with Compliance and Legal.", 6.44);
  s.addNotes("Present as a mapping for discussion, never as a compliance conclusion.");
}

/* ═══════════════ 15 · Feedback and recommendations ═══════════════ */
{
  const s = slide({
    kicker: "Live capture",
    title: "Feedback and recommendations",
  });

  const cols = [
    { t: "Feedback", a: T.MAGENTA },
    { t: "Recommendations", a: T.PURPLE },
    { t: "Action  ·  owner", a: T.GREEN },
  ];
  cols.forEach((c, i) => {
    const x = T.CX + i * 4.14;
    s.addShape("roundRect", {
      x, y: 1.62, w: 3.95, h: 4.7, rectRadius: 0.06,
      fill: { color: "FFFFFF" }, line: { color: c.a, width: 1.3 },
    });
    s.addShape("rect", { x, y: 1.62, w: 3.95, h: 0.07, fill: { color: c.a }, line: { type: "none" } });
    s.addText(c.t, {
      x: x + 0.2, y: 1.82, w: 3.55, h: 0.34,
      fontFace: T.FONT, fontSize: 13, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
    });
    for (let r = 0; r < 8; r += 1) {
      s.addShape("line", {
        x: x + 0.24, y: 2.44 + r * 0.47, w: 3.47, h: 0,
        line: { color: "DDDDDD", width: 0.75 },
      });
    }
  });

  s.addNotes("Capture the infrastructure team's input here during the session.");
}

pptx
  .writeFile({ fileName: OUT })
  .then(() => console.log(`Wrote ${OUT}  (${page} slides)`))
  .catch((e) => { console.error("FAILED:", e); process.exit(1); });
