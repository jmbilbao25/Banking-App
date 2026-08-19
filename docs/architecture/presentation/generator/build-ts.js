/**
 * QR Payment Platform — Infrastructure Design Review
 * TechStart (EastWest ITG). 12 slides, deliberately light on words.
 *
 *   node build-ts.js  ->  out/TechStart-QR-Payment-Infra-Review.pptx
 */

const path = require("path");
const PptxGenJS = require("pptxgenjs");
const T = require("./ts-theme");

const SHOTS = path.join(__dirname, "shots_trimmed");
const EXCAL = "/projects/sandbox/Banking-App/docs/architecture/excalidraw/preview";
const OUT = path.join(__dirname, "out", "TechStart-QR-Payment-Infra-Review.pptx");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "TechStart — EastWest ITG";
pptx.company = "EastWest Bank";
pptx.title = "QR Payment Platform — Infrastructure Design Review";

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
  s.addShape("diamond", {
    x, y, w, h,
    fill: { color }, line: { type: "none" },
  });
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

/* ═══════════════ 1 · Title ═══════════════ */
{
  const s = pptx.addSlide();
  page = 1;
  T.ribbon(s);

  T.ewLogo(s, 0.62, 0.55, 0.42, { fontSize: 15 });

  s.addText(
    [
      { text: "QR Payment Platform", options: { bold: true, fontSize: 36, breakLine: true, color: T.PURPLE_DK } },
      { text: "Infrastructure Design Review", options: { fontSize: 21, breakLine: true, color: T.MAGENTA } },
    ],
    { x: 0.62, y: 2.65, w: 7.1, h: 1.6, fontFace: T.FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.14 }
  );

  s.addShape("rect", { x: 0.62, y: 4.42, w: 1.0, h: 0.06, fill: { color: T.LIME }, line: { type: "none" } });

  s.addText(
    [
      { text: "TechStart", options: { bold: true, fontSize: 13, color: T.PURPLE_DK } },
      { text: "  ·  a group under EastWest ITG", options: { fontSize: 13, color: T.MUTED } },
    ],
    { x: 0.62, y: 4.66, w: 7.1, h: 0.3, fontFace: T.FONT, margin: 0, valign: "middle" }
  );

  s.addText("HA  ·  Scalability  ·  Observability  ·  BSP readiness", {
    x: 0.62, y: 5.0, w: 3.35, h: 0.3,
    fontFace: T.FONT, fontSize: 10, color: T.MUTED, margin: 0, valign: "middle",
  });

  s.addText("TECHSTART", {
    x: 8.15, y: 1.28, w: 4.6, h: 0.6, rotate: 340,
    fontFace: T.FONT, fontSize: 30, bold: true, color: T.LIME,
    align: "center", valign: "middle", margin: 0, charSpacing: 2.5,
  });
  s.addText("Your dream  ·  Our focus", {
    x: 8.62, y: 2.06, w: 4.3, h: 0.34, rotate: 340,
    fontFace: T.FONT, fontSize: 11, color: "FFFFFF",
    align: "center", valign: "middle", margin: 0,
  });

  s.addNotes(
    "Hands-on infrastructure design review. We present the current build, then the four " +
      "platform topics we need input on: high availability, scalability on Kubernetes, " +
      "observability, and BSP readiness. Final slide is left blank to capture the infra " +
      "team's feedback live."
  );
}

/* ═══════════════ 2 · Project Overview ═══════════════ */
{
  const s = slide({ kicker: "Overview", title: "What we built" });

  const cards = [
    { t: "The product", l: ["Customer scans a QR at checkout", "Pays from their bank account", "Merchant order releases on payment"], a: T.MAGENTA },
    { t: "The build", l: ["2 Python / Flask services", "One database each", "Integrated over REST"], a: T.PURPLE },
    { t: "Where it runs", l: ["AWS EC2 — dev / test", "Azure ACI — production", "Jenkins build and deploy"], a: T.GOLD },
    { t: "What we need", l: ["Review of HA and scaling", "Observability direction", "BSP readiness check"], a: T.GREEN },
  ];
  cards.forEach((c, i) => {
    T.card(s, {
      x: T.CX + i * 3.11, y: 1.55, w: 2.87, h: 2.45,
      title: c.t, lines: c.l, accent: c.a, num: i + 1, titleSize: 12, bodySize: 10,
    });
  });

  s.addShape("roundRect", {
    x: T.CX, y: 4.32, w: T.CW, h: 1.72, rectRadius: 0.06,
    fill: { color: T.ALT }, line: { color: T.PURPLE, width: 1 },
  });
  s.addText("Verified end to end", {
    x: T.CX + 0.22, y: 4.5, w: 3.0, h: 0.3,
    fontFace: T.FONT, fontSize: 11.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });
  const stats = [
    ["31.00", "order total\nsettled"],
    ["1,469.00", "payer balance\nafter debit"],
    ["300 s", "QR validity\nwindow"],
    ["2 s", "merchant status\npoll interval"],
    ["2", "services, 2\ndatabases"],
  ];
  stats.forEach((st, i) => {
    T.stat(s, T.CX + 0.35 + i * 2.36, 4.92, 2.2, st[0], st[1], i % 2 ? T.PURPLE : T.MAGENTA);
  });

  T.footnote(s, "Figures observed from both services executed end to end, not estimated.", 6.2);
  s.addNotes("Keep this to 60 seconds. The five numbers prove the thing actually runs.");
}

/* ═══════════════ 3 · Business Requirements & Assumptions ═══════════════ */
{
  const s = slide({ kicker: "Scope", title: "Business requirements and assumptions" });

  s.addText("Requirements — as built", {
    x: T.CX, y: 1.5, w: 7.4, h: 0.28,
    fontFace: T.FONT, fontSize: 11.5, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });

  T.table(
    s,
    [
      ["#", "Requirement", "Status"],
      ["1", "Customer pays a merchant by scanning a QR code", { text: "Working", color: T.GREEN, bold: true }],
      ["2", "QR expires automatically after 5 minutes", { text: "Working", color: T.GREEN, bold: true }],
      ["3", "A QR cannot be paid twice", { text: "Working", color: T.GREEN, bold: true }],
      ["4", "Merchant sees payment without refreshing", { text: "Working", color: T.GREEN, bold: true }],
      ["5", "Order releases only after funds actually move", { text: "Gap", color: T.RED, bold: true }],
      ["6", "Platform survives losing one instance", { text: "Gap", color: T.RED, bold: true }],
    ],
    { y: 1.84, w: 7.4, colW: [0.4, 5.3, 1.7], fontSize: 10, rowH: 0.38 }
  );

  T.card(s, {
    x: 8.28, y: 1.5, w: 4.5, h: 2.55,
    title: "Assumptions",
    lines: [
      "Azure and AWS accounts are lab, not production",
      "Prototype volume — no throughput target agreed",
      "Services stay separately deployable",
      "Existing Kubernetes manifests are the intended runtime",
    ],
    accent: T.PURPLE, titleSize: 11.5, bodySize: 9.8,
  });

  T.card(s, {
    x: 8.28, y: 4.2, w: 4.5, h: 1.78,
    title: "If an assumption is wrong",
    lines: [
      "Lab → production changes urgency, not the plan",
      "A volume target changes all sizing here",
      "A shared ITG cluster changes the Kubernetes plan",
    ],
    accent: T.AMBER, fill: "FFF9EF", titleSize: 11.5, bodySize: 9.8,
  });

  s.addShape("roundRect", {
    x: T.CX, y: 4.64, w: 7.4, h: 1.34, rectRadius: 0.06,
    fill: { color: "FDECEC" }, line: { color: T.RED, width: 1.1 },
  });
  s.addText(
    [
      { text: "The one functional gap\n", options: { bold: true, fontSize: 11, color: T.RED, breakLine: true } },
      {
        text:
          "The merchant order is marked paid before the money moves. Two databases " +
          "commit one after the other, so a failure between them leaves an order paid " +
          "with no matching debit.",
        options: { fontSize: 9.8, color: T.INK },
      },
    ],
    { x: T.CX + 0.18, y: 4.76, w: 7.04, h: 1.12, fontFace: T.FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.06 }
  );

  s.addNotes("Requirements 1-4 work. 5 and 6 are the two we want the infra team's view on.");
}

/* ═══════════════ 4 · User Flow ═══════════════ */
{
  const s = slide({ kicker: "Journey", title: "User flow" });

  const BLUE = "3B6FD4";
  const rA = 1.68;   // row A boxes
  const h1 = 0.5;

  /* ── Row A: order and QR ─────────────────────────────── */
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
  box(s, { x: 6.16, y: rA, w: 1.55, h: h1, title: "Scan QR", fill: "EEF4FF", color: BLUE });
  diamond(s, { x: 8.05, y: rA - 0.16, w: 1.6, h: 0.82, title: "QR valid?" });

  link(s, 1.45, rA + 0.25, 1.72, rA + 0.25);
  link(s, 3.67, rA + 0.25, 3.94, rA + 0.25);
  link(s, 5.89, rA + 0.25, 6.16, rA + 0.25);
  link(s, 7.71, rA + 0.25, 8.05, rA + 0.25);

  // NO -> back to store
  link(s, 9.65, rA + 0.25, 10.5, rA + 0.25, { color: T.RED });
  tag(s, 9.83, rA - 0.06, 0.44, "NO", T.RED);
  box(s, { x: 10.5, y: rA, w: 2.0, h: h1, title: "Back to store", sub: "get a new QR", fill: "FDECEC", color: T.RED });

  /* ── Row B: authentication ───────────────────────────── */
  const rB = 3.06;
  link(s, 8.85, rA + 0.66, 8.85, rB - 0.16, { color: T.GREEN });
  tag(s, 8.92, rA + 0.78, 0.46, "YES", T.GREEN);

  diamond(s, { x: 8.05, y: rB - 0.16, w: 1.6, h: 0.82, title: "Logged in?", fill: "EFF8F0", color: T.GREEN });

  box(s, { x: 5.3, y: rB, w: 2.1, h: h1, title: "Payment Details", sub: "items + total", fill: "F3EEFB", color: T.PURPLE });
  link(s, 8.05, rB + 0.2, 7.4, rB + 0.2, { color: T.GREEN });
  tag(s, 7.5, rB - 0.24, 0.62, "YES", T.GREEN);

  box(s, { x: 9.9, y: rB, w: 1.7, h: h1, title: "Login", fill: "EFF8F0", color: T.GREEN });
  link(s, 9.65, rB + 0.25, 9.9, rB + 0.25, { color: T.GREEN });
  tag(s, 9.62, rB - 0.28, 1.0, "NOT LOGGED IN", T.GREEN);

  // login rejoins payment details from below
  link(s, 10.75, rB + h1, 10.75, 3.94, { color: T.GREEN, arrow: false });
  link(s, 10.75, 3.94, 6.9, 3.94, { color: T.GREEN, arrow: false });
  link(s, 6.9, 3.94, 6.9, rB + h1, { color: T.GREEN });

  /* ── Row C: outcomes ────────────────────────────────── */
  link(s, 6.0, rB + h1, 6.0, 4.18, { arrow: false, color: T.PURPLE });
  link(s, 6.0, 4.18, 5.15, 4.18, { arrow: false, color: T.PURPLE });
  link(s, 5.15, 4.18, 5.15, 4.5, { color: BLUE });
  link(s, 6.0, 4.18, 7.45, 4.18, { arrow: false, color: T.PURPLE });
  link(s, 7.45, 4.18, 7.45, 4.5, { color: T.AMBER });

  const chain = [
    { x: 4.3, col: BLUE, fill: "EEF4FF", steps: [["Confirm", null], ["Process Payment", null], ["Payment complete", null]], last: { fill: "EFF8F0", color: T.GREEN } },
    { x: 6.6, col: T.AMBER, fill: "FFF6E5", steps: [["Cancel", null], ["No amount deducted", null], ["QR scan screen", null]], last: null },
  ];
  chain.forEach((c) => {
    c.steps.forEach((st, i) => {
      const y = 4.5 + i * 0.75;
      const isLast = i === c.steps.length - 1;
      box(s, {
        x: c.x, y, w: 1.7, h: 0.48,
        title: st[0],
        fill: isLast && c.last ? c.last.fill : c.fill,
        color: isLast && c.last ? c.last.color : c.col,
        titleSize: 8.5,
      });
      if (i < c.steps.length - 1) {
        link(s, c.x + 0.85, y + 0.48, c.x + 0.85, y + 0.75, { color: c.col });
      }
    });
  });

  T.card(s, {
    x: 9.0, y: 4.5, w: 3.78, h: 1.98,
    title: "Guards in the flow",
    lines: ["Expiry — 300 s", "Single use per order", "Live status re-check before debit", "Balance check"],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11, bodySize: 9.5,
  });

  T.footnote(s, "Flow reviewed against the code: QR validity is 300 seconds (5 minutes).", 6.6);
  s.addNotes("This mirrors the flow diagram from the team, corrected to the 300 s the code actually uses.");
}

/* ═══════════════ 5 · Current architecture (Excalidraw) ═══════════════ */
{
  const s = slide({
    kicker: "Architecture",
    title: "Target architecture — hub and spoke",
    subtitle: "One region, one hub, four spokes. No workload endpoint reachable from the internet.",
  });

  T.image(s, path.join(EXCAL, "05-network-topology.png"), T.CX, 1.46, 7.32, 5.02);

  // numbered request path
  s.addText("One banking payment, phone to database", {
    x: 8.05, y: 1.46, w: 4.73, h: 0.26,
    fontFace: T.FONT, fontSize: 11, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });

  const hops = [
    ["Front Door Premium", "TLS ends here; WAF; the only way in"],
    ["Application Gateway WAF v2", "internal — the Private Link origin"],
    ["API Management Premium", "checks the sign-in token first"],
    ["AKS private cluster", "the banking app; no public API server"],
    ["Azure Firewall Premium", "inspects everything outbound"],
    ["Banking endpoint", "reaches bankdb only"],
    ["PostgreSQL — bankdb", "accounts, ledger, transactions"],
  ];
  hops.forEach((hp, i) => {
    const y = 1.8 + i * 0.335;
    s.addShape("ellipse", {
      x: 8.05, y: y + 0.02, w: 0.26, h: 0.26,
      fill: { color: i === 6 ? T.MAGENTA : T.PURPLE }, line: { type: "none" },
    });
    s.addText(String(i + 1), {
      x: 8.05, y: y + 0.02, w: 0.26, h: 0.26,
      fontFace: T.FONT, fontSize: 8.5, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(
      [
        { text: hp[0], options: { bold: true, color: T.INK, fontSize: 9.5 } },
        { text: `   ${hp[1]}`, options: { color: T.MUTED, fontSize: 8.5 } },
      ],
      {
        x: 8.4, y, w: 4.38, h: 0.3,
        fontFace: T.FONT, margin: 0, valign: "middle",
      }
    );
  });

  T.card(s, {
    x: 8.05, y: 4.26, w: 4.73, h: 1.34,
    title: "Why this shape",
    lines: [
      "Spokes peer with the hub only — apps cannot reach each other",
      "Service Bus is the only link between the apps",
      "Core banking over ExpressRoute, never the internet",
    ],
    accent: T.PURPLE, fill: T.ALT, titleSize: 10.5, bodySize: 9,
  });

  T.card(s, {
    x: 8.05, y: 5.72, w: 4.73, h: 0.76,
    title: "Open with the infra team",
    lines: ["Singapore region — cross-border basis and BSP notice required"],
    accent: T.AMBER, fill: "FFF9EF", titleSize: 10.5, bodySize: 9,
  });

  s.addNotes(
    "Walk the seven numbers, then stop. Two things to raise: the Service Bus decision, " +
      "because it is what fixes the two-database gap on the next slide, and the Singapore " +
      "region, because Azure has no PH region and that needs a legal basis, not engineering."
  );
}

/* ═══════════════ 6 · Application walkthrough ═══════════════ */
{
  const s = slide({ kicker: "Demo", title: "The application, running" });

  const shots = [
    ["01-ecom-store.png", "Merchant catalogue"],
    ["03-ecom-checkout-qr.png", "QR presented at checkout"],
    ["05-bank-pay-form.png", "Authorising in the bank app"],
  ];

  const bw = 3.9;
  shots.forEach(([f, cap], i) => {
    const x = T.CX + i * 4.06;
    s.addText(cap, {
      x, y: 1.5, w: bw, h: 0.26,
      fontFace: T.FONT, fontSize: 10.5, bold: true, color: T.PURPLE_DK,
      align: "center", valign: "middle", margin: 0,
    });
    T.image(s, path.join(SHOTS, f), x, 1.84, bw, 4.5, { valign: "top" });
  });

  T.footnote(s, "Live captures from both services running end to end. Images are placed at their true aspect ratio.", 6.5);
  s.addNotes("Thirty seconds. The point is that it works, so the conversation can be about the platform.");
}

/* ═══════════════ 7 · Payment sequence ═══════════════ */
{
  const s = slide({ kicker: "Runtime", title: "How a payment moves" });

  const lanes = [
    { n: "Customer", c: T.PURPLE, f: "FFFFFF" },
    { n: "Merchant app", c: "3B6FD4", f: "EEF4FF" },
    { n: "Merchant DB", c: "3B6FD4", f: "FFFFFF" },
    { n: "Bank app", c: T.GREEN, f: "EFF8F0" },
    { n: "Bank DB", c: T.GREEN, f: "FFFFFF" },
  ];
  const x0 = 0.9;
  const lw = 2.28;
  const cxs = lanes.map((_, i) => x0 + lw * i + lw / 2);

  lanes.forEach((l, i) => {
    s.addShape("roundRect", {
      x: x0 + lw * i + 0.12, y: 1.52, w: lw - 0.24, h: 0.4, rectRadius: 0.05,
      fill: { color: l.f }, line: { color: l.c, width: 1.1 },
    });
    s.addText(l.n, {
      x: x0 + lw * i + 0.12, y: 1.52, w: lw - 0.24, h: 0.4,
      fontFace: T.FONT, fontSize: 9.5, bold: true, color: T.INK,
      align: "center", valign: "middle", margin: 0,
    });
    s.addShape("line", {
      x: cxs[i], y: 1.94, w: 0, h: 4.1,
      line: { color: "AAAAAA", width: 0.75, dashType: "dash" },
    });
  });

  const msgs = [
    [0, 1, "checkout — create order", false],
    [1, 2, "save order · PENDING · 300 s", false],
    [1, 0, "show QR", true],
    [0, 3, "scan QR, log in, confirm", false],
    [3, 1, "check the order is still payable", false],
    [3, 1, "tell merchant it is paid", false],
    [1, 2, "commit 1 — order PAID", false],
    [3, 4, "commit 2 — money moves", false],
    [3, 0, "receipt", true],
  ];

  const y0 = 2.42;
  const pitch = 0.42;

  // exposure window is drawn FIRST so the message labels sit on top of it
  s.addShape("roundRect", {
    x: cxs[1] - 0.34, y: 4.58, w: cxs[4] - cxs[1] + 0.68, h: 1.5,
    rectRadius: 0.05,
    fill: { color: "FDECEC", transparency: 55 },
    line: { color: T.RED, width: 1.1, dashType: "dash" },
  });

  msgs.forEach(([a, b, txt, ret], i) => {
    const yy = y0 + pitch * i;
    const leftward = cxs[b] < cxs[a];
    const isCommit = txt.startsWith("commit");
    const col = isCommit ? T.MAGENTA : ret ? T.MUTED : T.PURPLE_DK;
    s.addShape("line", {
      x: Math.min(cxs[a], cxs[b]), y: yy, w: Math.abs(cxs[b] - cxs[a]), h: 0,
      flipH: leftward,
      line: {
        color: col, width: isCommit ? 1.5 : 1.15,
        dashType: ret ? "dash" : "solid", endArrowType: "triangle",
      },
    });
    const padW = Math.max(Math.abs(cxs[b] - cxs[a]), 2.6);
    s.addText(
      [
        { text: `${i + 1}  `, options: { bold: true, color: T.MUTED } },
        { text: txt, options: { bold: isCommit, color: col } },
      ],
      {
        x: (cxs[a] + cxs[b]) / 2 - padW / 2, y: yy - 0.31, w: padW, h: 0.26,
        fontFace: T.FONT, fontSize: 9, align: "center", valign: "bottom", margin: 0,
      }
    );
  });

  s.addText(
    [
      { text: "Steps 7 and 8\n", options: { bold: true, fontSize: 10, color: T.RED, breakLine: true } },
      { text: "Two commits, two databases, nothing joining them. This is the gap.", options: { fontSize: 9, color: T.INK } },
    ],
    {
      x: 0.62, y: 6.14, w: 5.4, h: 0.62,
      fontFace: T.FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.05,
    }
  );

  s.addNotes("Nine steps. Land on 7 and 8 — that is the design question for the infra team.");
}

/* ═══════════════ 8 · High Availability ═══════════════ */
{
  const s = slide({ kicker: "Topic 1 of 4", title: "High availability" });

  T.table(
    s,
    [
      ["Layer", "Today", "What we think it should be"],
      ["Edge", { text: "One Nginx container, no failover", color: T.RED }, "Managed gateway, health-probed backend pool"],
      ["Application", { text: "2 containers, but no load balancer in front", color: T.RED }, "2+ replicas actually load balanced"],
      ["Database", { text: "Single node, no replica", color: T.RED }, "Zone-redundant managed instance"],
      ["Backup", { text: "None configured, no restore ever tested", color: T.RED }, "Automated backup, PITR, rehearsed restore"],
      ["Deploys", { text: "Delete then recreate — outage every release", color: T.RED }, "Rolling update, gated on readiness"],
    ],
    { y: 1.52, colW: [1.5, 5.5, 5.23], fontSize: 10, rowH: 0.46 }
  );

  T.stat(s, T.CX + 0.1, 4.72, 2.6, "0", "tiers with a redundant\ninstance taking traffic", T.RED);
  T.stat(s, T.CX + 3.0, 4.72, 2.6, "100%", "of releases cause\na planned outage", T.RED);
  T.stat(s, T.CX + 5.9, 4.72, 2.6, "?", "RPO and RTO\nnever agreed", T.AMBER);

  T.card(s, {
    x: 9.3, y: 4.46, w: 3.48, h: 1.98,
    title: "Ask the infra team",
    lines: [
      "What availability target applies here?",
      "What RPO and RTO do we design to?",
      "Standard gateway pattern in ITG?",
    ],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11, bodySize: 9.5,
  });

  s.addNotes("The three numbers are the whole slide. We cannot pick RPO/RTO ourselves.");
}

/* ═══════════════ 9 · Scalability — Kubernetes ═══════════════ */
{
  const s = slide({ kicker: "Topic 2 of 4", title: "Scalability on Kubernetes" });

  // current
  s.addText("Today — Azure Container Instances", {
    x: T.CX, y: 1.5, w: 5.9, h: 0.26,
    fontFace: T.FONT, fontSize: 11, bold: true, color: T.RED, margin: 0, valign: "middle",
  });
  s.addShape("roundRect", {
    x: T.CX, y: 1.84, w: 5.9, h: 1.42, rectRadius: 0.06,
    fill: { color: "FDECEC" }, line: { color: T.RED, width: 1.1 },
  });
  box(s, { x: 0.8, y: 2.04, w: 1.5, h: 0.5, title: "Public FQDN", sub: "per container", fill: "FFFFFF", color: T.RED, titleSize: 8.5 });
  box(s, { x: 2.55, y: 2.04, w: 1.35, h: 0.5, title: "app-1", fill: "FFFFFF", color: T.RED, titleSize: 8.5 });
  box(s, { x: 4.1, y: 2.04, w: 1.35, h: 0.5, title: "app-2", fill: "FFFFFF", color: T.RED, titleSize: 8.5 });
  s.addText("No load balancer  ·  no autoscaling  ·  fixed count  ·  recreate to deploy", {
    x: 0.8, y: 2.64, w: 5.4, h: 0.5,
    fontFace: T.FONT, fontSize: 9.5, color: T.INK, margin: 0, valign: "top",
  });

  // target
  s.addText("Proposed — AKS", {
    x: 6.88, y: 1.5, w: 5.9, h: 0.26,
    fontFace: T.FONT, fontSize: 11, bold: true, color: T.GREEN, margin: 0, valign: "middle",
  });
  s.addShape("roundRect", {
    x: 6.88, y: 1.84, w: 5.9, h: 1.42, rectRadius: 0.06,
    fill: { color: "EFF8F0" }, line: { color: T.GREEN, width: 1.1 },
  });
  box(s, { x: 7.1, y: 2.04, w: 1.2, h: 0.5, title: "Ingress", sub: "+ WAF", fill: "FFFFFF", color: T.GREEN, titleSize: 8.5 });
  box(s, { x: 8.45, y: 2.04, w: 1.2, h: 0.5, title: "Service", sub: "ClusterIP", fill: "FFFFFF", color: T.GREEN, titleSize: 8.5 });
  box(s, { x: 9.8, y: 2.04, w: 1.35, h: 0.5, title: "Pods", sub: "HPA 2→N", fill: "FFFFFF", color: T.GREEN, titleSize: 8.5 });
  box(s, { x: 11.3, y: 2.04, w: 1.3, h: 0.5, title: "Managed DB", sub: "private", fill: "FFFFFF", color: T.GREEN, titleSize: 8.5 });
  link(s, 8.3, 2.29, 8.45, 2.29, { color: T.GREEN });
  link(s, 9.65, 2.29, 9.8, 2.29, { color: T.GREEN });
  link(s, 11.15, 2.29, 11.3, 2.29, { color: T.GREEN });
  s.addText("Horizontal Pod Autoscaler  ·  cluster autoscaler  ·  rolling updates  ·  probes enforced", {
    x: 7.1, y: 2.64, w: 5.4, h: 0.5,
    fontFace: T.FONT, fontSize: 9.5, color: T.INK, margin: 0, valign: "top",
  });

  T.card(s, {
    x: T.CX, y: 3.52, w: 3.92, h: 2.5,
    title: "Already done",
    lines: [
      "Deployment, Service and Secret manifests written",
      "Liveness and readiness probes defined",
      "Config is all environment variables",
      "Stateless request handling",
    ],
    accent: T.GREEN, fill: "F4FBF5", titleSize: 11.5, bodySize: 10,
  });
  T.card(s, {
    x: 4.71, y: 3.52, w: 3.92, h: 2.5,
    title: "Blockers to fix first",
    lines: [
      "Session key is per-instance — externalise it",
      "Service type is LoadBalancer — should be ClusterIP",
      "Secrets are plaintext in the manifest",
      "No connection pooling for the database",
    ],
    accent: T.AMBER, fill: "FFF9EF", titleSize: 11.5, bodySize: 10,
  });
  T.card(s, {
    x: 8.87, y: 3.52, w: 3.91, h: 2.5,
    title: "Ask the infra team",
    lines: [
      "AKS or Container Apps for this workload?",
      "Is there a shared ITG cluster we join?",
      "What scales it — CPU, or requests per second?",
      "Who owns the manifests after handover?",
    ],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11.5, bodySize: 10,
  });

  s.addNotes("Our strongest slide: the manifests exist. The lift is smaller than it looks.");
}

/* ═══════════════ 10 · Observability ═══════════════ */
{
  const s = slide({ kicker: "Topic 3 of 4", title: "Observability" });

  const pillars = [
    { t: "Logs", now: "print() to stdout, lost on redeploy", tgt: "Container Insights → Log Analytics, structured JSON", a: T.PURPLE },
    { t: "Metrics", now: "None collected", tgt: "Azure Monitor, workload dashboards", a: T.MAGENTA },
    { t: "Traces", now: "No correlation ID between services", tgt: "OpenTelemetry → App Insights", a: T.GOLD },
  ];
  pillars.forEach((p, i) => {
    const x = T.CX + i * 4.14;
    s.addShape("roundRect", {
      x, y: 1.52, w: 3.95, h: 2.12, rectRadius: 0.06,
      fill: { color: "FFFFFF" }, line: { color: p.a, width: 1.2 },
    });
    s.addShape("rect", { x, y: 1.52, w: 3.95, h: 0.06, fill: { color: p.a }, line: { type: "none" } });
    s.addText(p.t, {
      x: x + 0.18, y: 1.68, w: 3.6, h: 0.34,
      fontFace: T.FONT, fontSize: 14, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
    });
    T.pill(s, x + 0.18, 2.12, 0.8, "NOW", T.RED);
    s.addText(p.now, {
      x: x + 1.06, y: 2.08, w: 2.72, h: 0.44,
      fontFace: T.FONT, fontSize: 9.5, color: T.INK, margin: 0, valign: "top",
    });
    T.pill(s, x + 0.18, 2.72, 0.8, "TARGET", T.GREEN);
    s.addText(p.tgt, {
      x: x + 1.06, y: 2.68, w: 2.72, h: 0.62,
      fontFace: T.FONT, fontSize: 9.5, color: T.INK, margin: 0, valign: "top",
    });
  });

  s.addShape("roundRect", {
    x: T.CX, y: 3.88, w: 7.75, h: 2.38, rectRadius: 0.06,
    fill: { color: "FFF9EF" }, line: { color: T.AMBER, width: 1.1 },
  });
  s.addText("What this costs us today", {
    x: T.CX + 0.2, y: 4.04, w: 7.35, h: 0.3,
    fontFace: T.FONT, fontSize: 12, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
  });
  s.addText(
    [
      "A failed payment is discovered by the customer, not by us",
      "An incident cannot be reconstructed after the fact",
      "/health exists — but nothing is configured to call it",
      "No dashboard, no alert, no on-call signal",
    ].map((l) => ({ text: l, options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } })),
    {
      x: T.CX + 0.22, y: 4.42, w: 7.3, h: 1.72,
      fontFace: T.FONT, fontSize: 10.5, color: T.INK, margin: 0, valign: "top",
    }
  );

  T.card(s, {
    x: 8.62, y: 3.88, w: 4.16, h: 2.38,
    title: "Ask the infra team",
    lines: [
      "Standard ITG logging stack for us to use?",
      "Azure Monitor or Dynatrace?",
      "Who receives the alerts?",
    ],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11, bodySize: 9.5,
  });

  s.addNotes("The /health line usually lands hardest: we built the probe and never wired it up.");
}

/* ═══════════════ 11 · BSP compliance ═══════════════ */
{
  const s = slide({ kicker: "Topic 4 of 4", title: "BSP readiness" });

  T.table(
    s,
    [
      ["Instrument", "Requirement", "Where we stand"],
      ["Circular 1055", "QR Ph — EMVCo standard, signed payload", { text: "Not met — our QR is a plain URL", color: T.RED }],
      ["Circular 1198", "Merchant onboarding, settlement, disputes", { text: "Not met — no KYC or settlement", color: T.RED }],
      ["MORB App. 75", "Encryption in transit and at rest, key management", { text: "Not met — HTTP throughout", color: T.RED }],
      ["Circular 1140", "Technology outsourcing, exit plan, BCP", { text: "Partial — no exit or BCP yet", color: T.AMBER }],
      ["RA 10173 (DPA)", "Lawful basis for cross-border data transfer", { text: "Open — data sits in centralindia", color: T.AMBER }],
      ["RA 9160 (AMLA)", "Covered and suspicious transaction reporting", { text: "Not met — no reporting", color: T.RED }],
    ],
    { y: 1.52, colW: [1.85, 5.3, 5.08], fontSize: 9.8, rowH: 0.4 }
  );

  T.card(s, {
    x: T.CX, y: 4.54, w: 6.0, h: 1.78,
    title: "The two that need a decision, not code",
    lines: [
      { text: "Cross-border data — Azure has no PH region, so a transfer basis is required", bold: false },
      { text: "Licensing under Circular 1198 may apply before any launch", bold: false },
    ],
    accent: T.AMBER, fill: "FFF9EF", titleSize: 11, bodySize: 9.8,
  });

  T.card(s, {
    x: 6.79, y: 4.54, w: 5.99, h: 1.78,
    title: "Ask the infra team",
    lines: [
      "Who owns the QR Ph conformance work?",
      "Is there an existing ITG cross-border transfer basis we inherit?",
      "Which controls does ITG already provide centrally?",
    ],
    accent: T.MAGENTA, fill: "FDF2F8", titleSize: 11, bodySize: 9.8,
  });

  T.footnote(
    s,
    "Engineering-side mapping only, not a legal opinion. Every citation to be confirmed with Compliance and Legal.",
    6.48
  );
  s.addNotes(
    "Be careful here: we are engineers reading circulars. Present as a mapping to be " +
      "confirmed, never as a compliance conclusion."
  );
}

/* ═══════════════ 12 · Feedback & Recommendations (blank) ═══════════════ */
{
  const s = slide({
    kicker: "Live capture",
    title: "Feedback and recommendations",
    subtitle: "To be filled in with the Infrastructure team during this session",
  });

  const cols = [
    { t: "Feedback", a: T.MAGENTA },
    { t: "Recommendations", a: T.PURPLE },
    { t: "Action items  ·  owner", a: T.GOLD },
  ];

  cols.forEach((c, i) => {
    const x = T.CX + i * 4.14;
    s.addShape("roundRect", {
      x, y: 1.72, w: 3.95, h: 4.6, rectRadius: 0.06,
      fill: { color: "FFFFFF" }, line: { color: c.a, width: 1.3 },
    });
    s.addShape("rect", { x, y: 1.72, w: 3.95, h: 0.06, fill: { color: c.a }, line: { type: "none" } });
    s.addText(c.t, {
      x: x + 0.2, y: 1.9, w: 3.55, h: 0.34,
      fontFace: T.FONT, fontSize: 13, bold: true, color: T.PURPLE_DK, margin: 0, valign: "middle",
    });
    // writing guides
    for (let r = 0; r < 8; r += 1) {
      s.addShape("line", {
        x: x + 0.24, y: 2.52 + r * 0.46, w: 3.47, h: 0,
        line: { color: "DDDDDD", width: 0.75 },
      });
    }
  });

  s.addNotes(
    "Deliberately blank. This is the hands-on part — capture the infrastructure team's " +
      "feedback, their recommendations, and who owns each follow-up, live on this slide."
  );
}

pptx
  .writeFile({ fileName: OUT })
  .then(() => console.log(`Wrote ${OUT}  (${page} slides)`))
  .catch((e) => { console.error("FAILED:", e); process.exit(1); });
