/**
 * QR Payment Platform — Current-State System Design
 * EastWest Bank DRB/ARB-style deck, generated with pptxgenjs.
 *
 *   node build.js  ->  ../QR-Payment-Platform-System-Design.pptx
 */

const path = require("path");
const PptxGenJS = require("pptxgenjs");
const T = require("./theme");
const { sequence } = require("./seq");

const SHOTS = path.join(__dirname, "shots_trimmed");
const OUT = path.join(__dirname, "out", "QR-Payment-Platform-System-Design.pptx");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 — must be set before any slide
pptx.author = "Cloud Architecture Study Team";
pptx.company = "EastWest Bank";
pptx.title = "QR Payment Platform — Current-State System Design";
pptx.subject = "Infrastructure and cloud architecture review of the QR payment prototype";

let page = 0;
function newSlide(opts) {
  const s = pptx.addSlide();
  page += 1;
  T.chrome(s, page, opts);
  return s;
}

/** Simple labelled node box for the architecture diagrams. */
function box(slide, o) {
  const {
    x, y, w, h, title, sub, fill = "FFFFFF", color = T.INK,
    titleSize = 9, subSize = 7.5, radius = 0.05, bold = true, dash,
  } = o;
  slide.addShape("roundRect", {
    x, y, w, h,
    rectRadius: radius,
    fill: { color: fill },
    line: { color, width: 1, dashType: dash || "solid" },
  });
  const parts = [{ text: title, options: { bold, breakLine: !!sub, fontSize: titleSize } }];
  if (sub) parts.push({ text: sub, options: { fontSize: subSize, color: T.MUTED } });
  slide.addText(parts, {
    x, y, w, h,
    fontFace: T.FONT,
    align: "center",
    valign: "middle",
    margin: 2,
    color: T.INK,
    lineSpacingMultiple: 0.92,
  });
}

function arrow(slide, x1, y1, x2, y2, o = {}) {
  const leftward = x2 < x1;
  const upward = y2 < y1;
  slide.addShape("line", {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    w: Math.abs(x2 - x1),
    h: Math.abs(y2 - y1),
    flipH: leftward,
    flipV: upward,
    line: {
      color: o.color || T.INK,
      width: o.width || 1.1,
      dashType: o.dash || "solid",
      endArrowType: o.arrow === false ? "none" : "triangle",
      beginArrowType: o.both ? "triangle" : "none",
    },
  });
  if (o.label) {
    slide.addText(o.label, {
      x: Math.min(x1, x2) - 0.35,
      y: (y1 + y2) / 2 - (o.labelDy != null ? o.labelDy : 0.22),
      w: Math.abs(x2 - x1) + 0.7,
      h: 0.2,
      fontFace: T.FONT,
      fontSize: o.labelSize || 7,
      color: o.labelColor || T.MUTED,
      align: "center",
      valign: "middle",
      margin: 0,
    });
  }
}

function caption(slide, x, y, w, text) {
  slide.addText(text, {
    x, y, w, h: 0.24,
    fontFace: T.FONT,
    fontSize: 10,
    bold: true,
    color: T.BLACK,
    align: "center",
    valign: "middle",
    margin: 0,
  });
}

function subcaption(slide, x, y, w, text) {
  slide.addText(text, {
    x, y, w, h: 0.34,
    fontFace: T.FONT,
    fontSize: 8,
    italic: true,
    color: T.MUTED,
    align: "center",
    valign: "top",
    margin: 0,
    lineSpacingMultiple: 0.95,
  });
}

function shot(slide, file, x, y, w, h) {
  slide.addImage({
    path: path.join(SHOTS, file),
    x, y, w, h,
    sizing: { type: "contain", w, h },
  });
}

function footnote(slide, text) {
  slide.addText(text, {
    x: T.CX,
    y: 6.5,
    w: T.CW,
    h: 0.24,
    fontFace: T.FONT,
    fontSize: 8,
    italic: true,
    color: T.MUTED,
    margin: 0,
    valign: "middle",
  });
}

/* ══════════════════════════════════════════════════════════════════════
   1 — Title
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = pptx.addSlide();
  page = 1;
  T.chrome(s, 1, {});
  s.addText(
    [
      {
        text: "QR Payment Platform",
        options: { bold: true, fontSize: 34, breakLine: true, color: T.BLACK },
      },
      {
        text: "Current-State System Design",
        options: { fontSize: 24, breakLine: true, color: T.BLACK },
      },
      {
        text: "Cloud & Infrastructure Architecture Review",
        options: { fontSize: 14, color: T.MUTED, italic: true },
      },
    ],
    {
      x: 1.15,
      y: 3.15,
      w: 10.6,
      h: 1.9,
      fontFace: T.FONT,
      margin: 0,
      valign: "top",
      lineSpacingMultiple: 1.12,
    }
  );
  s.addText("Prepared for: Head of Infrastructure  ·  For architecture review", {
    x: 1.15,
    y: 5.25,
    w: 10.6,
    h: 0.28,
    fontFace: T.FONT,
    fontSize: 11,
    color: T.MUTED,
    margin: 0,
  });
  s.addNotes(
    "Scope: this deck documents the CURRENT deployed architecture of a two-service QR " +
      "payment prototype, assessed from an infrastructure and cloud-platform standpoint. " +
      "It is a design-only review — no application code was changed. Screenshots and the " +
      "runtime sequences were captured from the prototype actually running end to end."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   2 — Project Details
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Project Details" });
  let y = T.CY + 0.05;
  const step = 0.34;
  const rows = [
    ["Project Name", "QR Payment Platform — Banking App and Merchant (E-commerce) App"],
    ["Document Type", "Current-State (As-Is) System Design · Infrastructure & Cloud Architecture"],
    ["Prepared By", "Cloud Architecture Study Team"],
    ["Reviewed With", "Head of Infrastructure"],
    ["Repository", "github.com/jmbilbao25/Banking-App"],
    ["Environments in Scope", "AWS EC2 (Dev/Test) · Azure Container Instances (Prod) · Jenkins CI/CD"],
  ];
  rows.forEach(([l, v]) => {
    T.labelValue(s, y, l, v);
    y += step;
  });

  y += 0.06;
  T.labelValue(
    s,
    y,
    "Scope and Objectives",
    [
      {
        text:
          "Establish a verified, evidence-based baseline of the platform as it runs today, so " +
          "that platform investment and a cloud target state can be argued from fact rather " +
          "than from the README.",
        options: { breakLine: true, paraSpaceAfter: 6 },
      },
      ...T.bullets([
        "Document the deployed runtime topology across both cloud environments",
        "Trace the end-to-end payment flow hop by hop, including ports, protocols and timeouts",
        "Record the delivery pipeline, network posture, data tier and observability position",
        "Assess resilience, scalability and recoverability against a production operating bar",
        "Identify the architecture-level gaps that must close before any production traffic",
      ]),
    ],
    { h: 2.1 }
  );

  footnote(
    s,
    "All statements in this deck were reconstructed from the repository contents and from " +
      "the prototype executed end to end in a sandbox, not from documentation."
  );
  s.addNotes(
    "Framing for the infra head: we are not proposing features. We are presenting a measured " +
      "baseline of what exists, and the platform gaps between that baseline and something " +
      "operable. Everything is traceable to a file or an observed run."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   3 — Design Considerations
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Design Considerations" });
  let y = T.CY + 0.05;

  T.labelValue(
    s,
    y,
    "Design Approach",
    "Two independently deployable Python/Flask services — a banking service and a merchant " +
      "service — integrated over synchronous REST. Each owns its own relational database. " +
      "Containers are built once and promoted from AWS Dev to Azure Prod by a Jenkins pipeline.",
    { h: 0.62 }
  );
  y += 0.7;

  T.labelValue(
    s,
    y,
    "Design Alternatives",
    "Kubernetes manifests for both services already exist in the repository but are not the " +
      "deployed path; production currently runs on Azure Container Instances. AKS is therefore " +
      "an available, partially prepared alternative rather than a greenfield decision.",
    { h: 0.62 }
  );
  y += 0.7;

  T.labelValue(
    s,
    y,
    "Constraints and Limitations",
    [
      ...T.bullets([
        "Prototype was built to demonstrate a payment journey, not to meet an operating standard",
        "Azure Container Instances offers no ingress, autoscaling or rolling-update primitive",
        "No infrastructure-as-code — cloud resources are created by imperative CLI calls in CI",
        "Single-node databases in both environments; no managed HA tier is provisioned",
      ]),
    ],
    { h: 1.0 }
  );
  y += 1.06;

  T.labelValue(
    s,
    y,
    "Dependencies",
    "Docker Hub (image distribution) · Jenkins (build and deploy orchestration) · Azure " +
      "subscription (ACI, Azure Database for MySQL) · AWS account (EC2 Dev/Test host).",
    { h: 0.46 }
  );
  y += 0.54;

  T.labelValue(
    s,
    y,
    "Assessment Basis",
    "Repository inspection, container and pipeline definitions, plus a live end-to-end " +
      "execution of both services to confirm the runtime behaviour documented here.",
    { h: 0.46 }
  );

  s.addNotes(
    "The alternatives line matters: the k8s manifests being present but unused is the single " +
      "cheapest lever we have. The team has already done part of the work for a managed " +
      "orchestrator; it simply is not the deployed path."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   4 — Assumptions
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Design Considerations", subtitle: "Assumptions" });
  T.table(
    s,
    [
      ["Assumption", "Identified by", "Impact if assumption is proven invalid"],
      [
        "The Azure and AWS environments in the pipeline are non-production / lab subscriptions.",
        "Study Team",
        "If any is a production subscription, the public endpoints and inline pipeline credentials become an immediate operational exposure and must be remediated before this review proceeds.",
      ],
      [
        "Existing container images can be rebuilt unchanged onto a managed orchestrator (AKS or Container Apps).",
        "Study Team",
        "Additional refactoring effort is required — chiefly externalising session state and the service-to-service addressing that is currently passed as environment variables.",
      ],
      [
        "The published Kubernetes manifests represent the team's intended target runtime.",
        "Study Team",
        "The migration path must be re-planned; effort estimates based on reusing those manifests would not hold.",
      ],
      [
        "Reported transaction volume is prototype-scale, with no committed throughput or latency target.",
        "Study Team",
        "Capacity, autoscaling and database sizing must be re-derived from a real volume forecast before any sizing in this deck is used.",
      ],
      [
        "The two services are intended to remain separately deployable, not merged into one application.",
        "Study Team",
        "The integration analysis and the network segmentation design would both be restated around a single deployable unit.",
      ],
    ],
    { y: T.CY + 0.06, colW: [5.0, 1.3, 5.8], fontSize: 9.5, rowH: 0.92 }
  );
  s.addNotes(
    "Assumption 1 is the one we want confirmed in the room. Everything downstream about " +
      "urgency depends on whether those endpoints are lab or real."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   5 — Risks
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Design Considerations", subtitle: "Architecture and Platform Risks" });
  T.table(
    s,
    [
      ["#", "Risk Description", "Exposure", "Mitigation"],
      [
        { text: "R-1", bold: true },
        "Every tier is a single instance behind a single DNS name. There is no load balancer distributing traffic across the two production containers.",
        { text: "Availability", color: T.RED, bold: true },
        "Introduce a managed ingress (Application Gateway / Front Door) and place both replicas behind a health-probed backend pool.",
      ],
      [
        { text: "R-2", bold: true },
        "Deployment recreates each container (delete then create), so every release is a full outage of that service.",
        { text: "Availability", color: T.RED, bold: true },
        "Move to a platform with rolling updates and readiness gating — AKS (manifests already exist) or Azure Container Apps.",
      ],
      [
        { text: "R-3", bold: true },
        "Single-node databases with no replica, no automated backup and no point-in-time recovery. RPO and RTO are undefined.",
        { text: "Data loss", color: T.RED, bold: true },
        "Managed database with zone-redundant HA, automated backups and a tested restore. Define and sign off RPO/RTO.",
      ],
      [
        { text: "R-4", bold: true },
        "All traffic, including service-to-service calls, is cleartext HTTP on port 80. No TLS anywhere in the path.",
        { text: "Confidentiality", color: T.RED, bold: true },
        "TLS termination at a managed edge, HTTPS end to end, and private networking for east-west traffic.",
      ],
      [
        { text: "R-5", bold: true },
        "Two databases are committed in sequence with no distributed transaction, queue, retry or reconciliation. A timeout leaves them permanently disagreeing.",
        { text: "Integrity", color: T.RED, bold: true },
        "Asynchronous integration over a managed broker with an outbox, idempotent consumers and a scheduled reconciliation job.",
      ],
      [
        { text: "R-6", bold: true },
        "Images are published to a public registry under a mutable :latest tag, unsigned and unscanned. What is running cannot be proven.",
        { text: "Supply chain", color: T.AMBER, bold: true },
        "Private registry (ACR) with immutable digests, vulnerability scanning and signed images gated in the pipeline.",
      ],
      [
        { text: "R-7", bold: true },
        "No infrastructure-as-code; environments are produced by imperative CLI calls, so they cannot be reproduced or audited.",
        { text: "Operability", color: T.AMBER, bold: true },
        "Declarative IaC (Bicep or Terraform) under version control, applied by pipeline with drift detection.",
      ],
      [
        { text: "R-8", bold: true },
        "No metrics, tracing, structured logging or alerting. An incident cannot be detected proactively or reconstructed afterwards.",
        { text: "Operability", color: T.AMBER, bold: true },
        "OpenTelemetry to Azure Monitor / App Insights, correlation IDs across services, dashboards and SLO-based alerts.",
      ],
    ],
    { y: T.CY + 0.04, colW: [0.5, 4.85, 1.15, 5.6], fontSize: 8.5, rowH: 0.62 }
  );
  s.addNotes(
    "R-1 through R-5 are the ones that would stop a go-live. R-6 through R-8 are what make " +
      "the platform operable once it is live. We sequence them in that order on the roadmap slide."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   6 — Solution Overview / context
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Solution Overview", subtitle: "System context and component responsibilities" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "A customer shops on the merchant service, which issues a QR code encoding a payment URL " +
      "addressed to the banking service. The customer authorises the payment in the banking " +
      "service, which then calls the merchant service back to release the order.",
    { h: 0.5 }
  );

  const dy = 2.25;

  box(s, { x: 0.88, y: dy + 0.5, w: 1.5, h: 0.9, title: "Customer", sub: "Browser / device", fill: "FFFFFF" });

  // merchant domain
  s.addShape("roundRect", {
    x: 2.85, y: dy - 0.12, w: 3.75, h: 1.97, rectRadius: 0.05,
    fill: { color: "F7FAFF" }, line: { color: T.BLUE, width: 1, dashType: "dash" },
  });
  s.addText("Merchant domain", {
    x: 2.93, y: dy - 0.08, w: 3.6, h: 0.22, fontFace: T.FONT, fontSize: 8,
    bold: true, color: T.BLUE, margin: 0,
  });
  box(s, { x: 3.0, y: dy + 0.2, w: 1.6, h: 0.55, title: "Nginx", sub: ":80 reverse proxy", fill: "FFFFFF" });
  box(s, { x: 3.0, y: dy + 0.95, w: 1.6, h: 0.72, title: "ecommerce-app", sub: "Flask · Gunicorn :5000", fill: "E8F0FE", color: T.BLUE });
  box(s, { x: 4.85, y: dy + 0.95, w: 1.6, h: 0.72, title: "ecomdb", sub: "MySQL 5.7", fill: "FFFFFF", color: T.BLUE });

  // banking domain
  s.addShape("roundRect", {
    x: 7.05, y: dy - 0.12, w: 3.75, h: 1.97, rectRadius: 0.05,
    fill: { color: "F5FBF6" }, line: { color: T.GREEN, width: 1, dashType: "dash" },
  });
  s.addText("Banking domain", {
    x: 7.13, y: dy - 0.08, w: 3.6, h: 0.22, fontFace: T.FONT, fontSize: 8,
    bold: true, color: T.GREEN, margin: 0,
  });
  box(s, { x: 7.2, y: dy + 0.2, w: 1.6, h: 0.55, title: "Nginx", sub: ":80 reverse proxy", fill: "FFFFFF" });
  box(s, { x: 7.2, y: dy + 0.95, w: 1.6, h: 0.72, title: "banking-app", sub: "Flask · Gunicorn :5001", fill: "E8F5E9", color: T.GREEN });
  box(s, { x: 9.05, y: dy + 0.95, w: 1.6, h: 0.72, title: "bankdb", sub: "MySQL 5.7", fill: "FFFFFF", color: T.GREEN });

  // customer -> merchant edge, and internal wiring
  arrow(s, 2.38, dy + 0.47, 3.0, dy + 0.47, {});
  s.addText("HTTP :80", {
    x: 2.4, y: dy + 0.21, w: 0.62, h: 0.2,
    fontFace: T.FONT, fontSize: 6.5, color: T.MUTED,
    align: "center", valign: "middle", margin: 0,
  });
  arrow(s, 3.8, dy + 0.75, 3.8, dy + 0.95, {});
  arrow(s, 4.6, dy + 1.31, 4.85, dy + 1.31, { both: true });
  arrow(s, 8.0, dy + 0.75, 8.0, dy + 0.95, {});
  arrow(s, 8.8, dy + 1.31, 9.05, dy + 1.31, { both: true });
  // customer -> bank edge (the QR hop)
  arrow(s, 1.63, dy + 1.4, 1.63, dy + 2.28, { arrow: false });
  arrow(s, 1.63, dy + 2.28, 8.0, dy + 2.28, { arrow: false });
  arrow(s, 8.0, dy + 2.28, 8.0, dy + 1.85, {});
  s.addText("customer scans the QR  →  HTTP :80 to the banking edge", {
    x: 2.6, y: dy + 2.04, w: 4.6, h: 0.2,
    fontFace: T.FONT, fontSize: 6.8, color: T.MUTED,
    align: "center", valign: "middle", margin: 0,
  });

  // cross-service integration, routed clear of every node
  arrow(s, 3.8, dy + 1.67, 3.8, dy + 2.68, { color: T.RED, width: 1.4, arrow: false });
  arrow(s, 7.6, dy + 1.67, 7.6, dy + 2.68, { color: T.RED, width: 1.4, arrow: false });
  arrow(s, 3.8, dy + 2.68, 7.6, dy + 2.68, { both: true, color: T.RED, width: 1.4 });
  s.addText("synchronous REST  —  order lookup and payment callback", {
    x: 3.3, y: dy + 2.72, w: 4.8, h: 0.22,
    fontFace: T.FONT, fontSize: 7.5, bold: true, color: T.RED,
    align: "center", valign: "middle", margin: 0,
  });

  T.callout(s, {
    x: 11.0, y: dy - 0.12, w: 1.9, h: 3.06,
    title: "Integration shape",
    body: [
      "Bidirectional, synchronous, cleartext HTTP.",
      "",
      "Addressing is by environment variable, not service discovery.",
      "",
      "No broker, no retry, no circuit breaker.",
      "",
      "In production this path leaves the trust boundary.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 8,
  });

  footnote(
    s,
    "Both services also expose /health, and container probes are defined for it in the " +
      "unused Kubernetes manifests."
  );
  s.addNotes(
    "The red arrow is the crux of the whole review: the two domains are coupled " +
      "synchronously and bidirectionally, over the public internet in production."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   7 — UI: merchant journey
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({
    title: "User Interfaces",
    subtitle: "Merchant service — catalogue to QR presentment",
  });
  const bw = 3.85, bx = [0.78, 4.9, 9.02], by = 1.62, bh = 4.35;
  const caps = [
    ["Product catalogue", "Basket state is held in the signed session cookie — no server-side session store."],
    ["Basket review", "Stock is re-validated against the database on every basket mutation."],
    ["Checkout and QR presentment", "Order is created PENDING with a 300-second expiry; the page polls status every 2 s."],
  ];
  const files = ["01-ecom-store.png", "02-ecom-cart.png", "03-ecom-checkout-qr.png"];
  bx.forEach((x, i) => {
    caption(s, x, 1.2, bw, caps[i][0]);
    shot(s, files[i], x, by, bw, bh);
    subcaption(s, x, by + bh + 0.06, bw, caps[i][1]);
  });
  footnote(s, "Screens captured from the prototype running end to end; order 133004e1, total 31.00.");
  s.addNotes(
    "These are real captures from a live run, not mock-ups. The QR encodes a plain HTTP URL " +
      "pointing at the banking service, built from the BANK_PUBLIC_BASE environment variable."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   8 — UI: bank journey
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({
    title: "User Interfaces",
    subtitle: "Banking service — authorisation to settlement",
  });
  const bw = 3.85, bx = [0.78, 4.9, 9.02], by = 1.62, bh = 4.35;
  const caps = [
    ["Authentication", "Scanning the QR without a session stores next_url and redirects to login."],
    ["Payment authorisation", "Order lines are fetched live from the merchant service with a 2-second timeout."],
    ["Settlement confirmation", "Rendered only after the merchant callback and the ledger commit have both returned."],
  ];
  const files = ["04-bank-login.png", "05-bank-pay-form.png", "07-bank-success.png"];
  bx.forEach((x, i) => {
    caption(s, x, 1.2, bw, caps[i][0]);
    shot(s, files[i], x, by, bw, bh);
    subcaption(s, x, by + bh + 0.06, bw, caps[i][1]);
  });
  footnote(s, "Session cookies are signed with an application-local key, so they are not portable between replicas.");
  s.addNotes(
    "Note for the infra head: because the signing key is application-local, two replicas " +
      "cannot validate each other's sessions. That is a platform constraint, not a code preference."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   9 — UI: confirmation and state convergence
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({
    title: "User Interfaces",
    subtitle: "Post-settlement state across both services",
  });
  const bw = 3.85, bx = [0.78, 4.9, 9.02], by = 1.62, bh = 4.15;
  const caps = [
    ["Merchant order converges to PAID", "Reached only by the 2-second client poll — the merchant is never pushed a notification."],
    ["Ledger balance after debit", "Payer balance moved 1,500.00 to 1,469.00 for the 31.00 order."],
    ["Replay of the same QR", "A second presentment of the same order is refused by the duplicate check."],
  ];
  const files = ["08-ecom-checkout-paid.png", "09-bank-accounts-after.png", "10-bank-replay-blocked.png"];
  bx.forEach((x, i) => {
    caption(s, x, 1.2, bw, caps[i][0]);
    shot(s, files[i], x, by, bw, bh);
    subcaption(s, x, by + bh + 0.06, bw, caps[i][1]);
  });
  footnote(
    s,
    "State convergence between the two services depends entirely on client-side polling; " +
      "there is no server-to-server notification or event."
  );
  s.addNotes(
    "The middle screenshot is our proof the flow really settled: 1500 minus 31 equals 1469, " +
      "observed in the running system."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   10 — Runtime sequence (hero)
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({
    title: "Runtime Sequence",
    subtitle: "End-to-end QR payment — every network hop as deployed today",
  });

  const lanes = [
    { label: "Customer", sub: "device", fill: "FFFFFF" },
    { label: "Nginx :80", sub: "merchant edge", fill: T.BAND_GREY },
    { label: "ecommerce-app", sub: "Gunicorn :5000", fill: T.BAND_BLUE, color: T.BLUE },
    { label: "ecomdb", sub: "MySQL 5.7", fill: "FFFFFF", color: T.BLUE },
    { label: "Nginx :80", sub: "bank edge", fill: T.BAND_GREY },
    { label: "banking-app", sub: "Gunicorn :5001", fill: T.BAND_GREEN, color: T.GREEN },
    { label: "bankdb", sub: "MySQL 5.7", fill: "FFFFFF", color: T.GREEN },
  ];

  const messages = [
    { from: 0, to: 1, text: "GET /  —  cleartext HTTP, no TLS" },
    { from: 1, to: 2, text: "proxy_pass http://ecommerce:5000" },
    { from: 2, to: 0, text: "store.html + session cookie (basket state)", kind: "return" },
    { from: 0, to: 2, text: "GET /checkout/create" },
    { from: 2, to: 3, text: "INSERT orders (PENDING, expires_at = +300 s)", kind: "db" },
    { from: 0, to: 2, text: "GET /qr/{order_id}" },
    { from: 2, to: 0, text: "QR PNG — encodes BANK_PUBLIC_BASE env var", kind: "return" },
    { from: 0, to: 2, text: "GET /api/orders/{id}/status — polled every 2 000 ms" },
    { from: 0, to: 4, text: "GET /pay?order_id&amount&merchant_account&expires" },
    { from: 4, to: 5, text: "proxy_pass http://banking:5001" },
    { from: 5, to: 0, text: "302 /login  →  POST /login  →  session cookie", kind: "return" },
    { from: 5, to: 2, text: "GET /api/orders/{id}  ·  timeout 2 s then 3 s", bold: true, color: T.RED, textColor: T.RED },
    { from: 5, to: 2, text: "POST /api/orders/{id}/paid  ·  timeout 5 s", bold: true, color: T.RED, textColor: T.RED },
    { from: 2, to: 3, text: "COMMIT 1 — status = PAID, stock decremented", kind: "db", bold: true },
    { from: 5, to: 6, text: "COMMIT 2 — balances + transaction inserted", kind: "db", bold: true },
  ];

  const bands = [
    { from: 0, to: 2, label: "1 · CATALOGUE AND BASKET", fill: T.BAND_BLUE },
    { from: 3, to: 6, label: "2 · ORDER CREATION AND QR PRESENTMENT", fill: T.BAND_AMBER },
    { from: 7, to: 7, label: "3 · CLIENT-SIDE STATUS POLLING", fill: T.BAND_GREY },
    { from: 8, to: 10, label: "4 · PAYER AUTHENTICATION", fill: T.BAND_BLUE },
    { from: 11, to: 14, label: "5 · SETTLEMENT — TWO DATABASES, TWO COMMITS", fill: T.BAND_RED },
  ];

  sequence(s, {
    x: 0.82, y: 1.14, w: 10.5, h: 5.24,
    lanes, messages, bands,
    laneFontSize: 8.2, msgFontSize: 7.5,
    headerH: 0.42,
    labelMinW: 2.5,
  });

  // legend
  s.addShape("roundRect", {
    x: 11.48, y: 1.14, w: 1.44, h: 1.62, rectRadius: 0.05,
    fill: { color: "FFFFFF" }, line: { color: T.MUTED, width: 0.75 },
  });
  s.addText("LEGEND", {
    x: 11.48, y: 1.18, w: 1.44, h: 0.2,
    fontFace: T.FONT, fontSize: 7, bold: true, color: T.MUTED,
    align: "center", valign: "middle", margin: 0, charSpacing: 0.8,
  });
  const legend = [
    ["request", T.INK, "solid"],
    ["response", T.MUTED, "dash"],
    ["database write", T.BLUE, "solid"],
    ["cross-service", T.RED, "solid"],
  ];
  legend.forEach((lg, i) => {
    const ly = 1.46 + i * 0.31;
    s.addShape("line", {
      x: 11.58, y: ly, w: 0.34, h: 0,
      line: { color: lg[1], width: 1.3, dashType: lg[2], endArrowType: "triangle" },
    });
    s.addText(lg[0], {
      x: 11.96, y: ly - 0.1, w: 0.92, h: 0.2,
      fontFace: T.FONT, fontSize: 6.8, color: T.INK, margin: 0, valign: "middle",
    });
  });

  T.callout(s, {
    x: 11.48, y: 2.94, w: 1.44, h: 3.44,
    title: "Note",
    body: [
      "Steps 12–15 are the exposure window.",
      "",
      "The merchant database commits before the bank database, and the two calls cross the public internet.",
      "",
      "No distributed transaction, queue or reconciliation exists.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 7,
  });

  footnote(s, "Reconstructed from banking-app/app.py, ecommerce-app/app.py and nginx/nginx.conf; confirmed against a live run.");
  s.addNotes(
    "Walk the audience down the five bands. The punchline is band 5: steps 12 to 15. " +
      "Merchant state becomes durable at step 14 and bank state at step 15, with a network " +
      "call between them and nothing to reconcile the gap."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   11 — Runtime sequence (settlement zoom)
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({
    title: "Runtime Sequence",
    subtitle: "Settlement call chain — commit ordering and the exposure window",
  });

  const lanes = [
    { label: "banking-app", sub: "Gunicorn :5001", fill: T.BAND_GREEN, color: T.GREEN },
    { label: "ecommerce-app", sub: "Gunicorn :5000", fill: T.BAND_BLUE, color: T.BLUE },
    { label: "ecomdb", sub: "MySQL 5.7 — merchant", fill: "FFFFFF", color: T.BLUE },
    { label: "bankdb", sub: "MySQL 5.7 — bank", fill: "FFFFFF", color: T.GREEN },
  ];

  const messages = [
    { from: 0, to: 1, text: "GET /api/orders/{id}  ·  timeout 2 s   (render the form)" },
    { from: 0, to: 1, text: "GET /api/orders/{id}  ·  timeout 3 s   (re-check status)" },
    { from: 0, to: 1, text: "POST /api/orders/{id}/paid  ·  timeout 5 s", bold: true, color: T.RED, textColor: T.RED },
    { from: 1, to: 2, text: "UPDATE orders SET status = 'PAID'", kind: "db" },
    { from: 1, to: 2, text: "UPDATE products SET stock = stock − quantity", kind: "db" },
    { from: 2, to: 1, text: "COMMIT   —   merchant state is now durable", kind: "return", bold: true, textColor: T.RED },
    { from: 1, to: 0, text: "200 OK", kind: "return" },
    { from: 0, to: 3, text: "UPDATE accounts   —   debit payer, credit merchant", kind: "db" },
    { from: 0, to: 3, text: "INSERT transactions", kind: "db" },
    { from: 3, to: 0, text: "COMMIT   —   bank state is now durable", kind: "return", bold: true, textColor: T.RED },
  ];

  const bands = [
    { from: 0, to: 1, label: "READ-ONLY PRE-CHECKS", fill: T.BAND_BLUE },
    { from: 2, to: 5, label: "MERCHANT SIDE COMMITS FIRST", fill: T.BAND_AMBER },
    { from: 6, to: 9, label: "BANK SIDE COMMITS SECOND — EXPOSURE WINDOW", fill: T.BAND_RED },
  ];

  sequence(s, {
    x: 0.82, y: 1.2, w: 8.05, h: 5.0,
    lanes, messages, bands,
    laneFontSize: 9, msgFontSize: 8,
    headerH: 0.44,
    labelMinW: 3.3,
  });

  T.callout(s, {
    x: 9.1, y: 1.2, w: 3.8, h: 1.62,
    title: "What the ordering guarantees",
    body: [
      "The merchant's order is marked PAID and stock is decremented BEFORE any money moves.",
      "Once step 6 commits, that outcome is durable and irreversible.",
    ],
    accent: T.AMBER, fill: T.BAND_AMBER, fontSize: 9,
  });

  T.callout(s, {
    x: 9.1, y: 2.95, w: 3.8, h: 1.72,
    title: "What fails in the window",
    body: [
      "Any fault between steps 6 and 10 — database failover, container eviction, a lost response, a 5 s timeout that in fact succeeded — leaves the order PAID with no corresponding ledger entry.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 9,
  });

  T.callout(s, {
    x: 9.1, y: 4.8, w: 3.8, h: 1.42,
    title: "Platform capability required",
    body: [
      "Transactional outbox, a managed broker with at-least-once delivery, idempotent consumers, and a scheduled reconciliation sweep.",
    ],
    accent: T.GREEN, fill: T.BAND_GREEN, fontSize: 9,
  });

  footnote(s, "Timeout values are the literal values configured in the banking service's HTTP client calls.");
  s.addNotes(
    "This is the slide to linger on. It is not a coding style question — it is a missing " +
      "platform capability. Two datastores cannot be made consistent by ordering alone."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   12 — Deployment topology
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({
    title: "Infrastructure and Technology Stack",
    subtitle: "Current deployment topology across both cloud environments",
  });

  // AWS Dev
  s.addShape("roundRect", {
    x: 0.82, y: 1.2, w: 5.7, h: 2.5, rectRadius: 0.05,
    fill: { color: "FFF8E7" }, line: { color: "E08600", width: 1.25, dashType: "dash" },
  });
  s.addText("AWS  ·  EC2 single VM  ·  Dev / Test", {
    x: 0.92, y: 1.25, w: 4.4, h: 0.24, fontFace: T.FONT, fontSize: 9,
    bold: true, color: "9A5B00", margin: 0,
  });
  box(s, { x: 0.98, y: 1.58, w: 1.55, h: 0.55, title: "Nginx :80", sub: "merchant", fill: "FFFFFF" });
  box(s, { x: 0.98, y: 2.22, w: 1.55, h: 0.62, title: "ecommerce-app", sub: "Gunicorn", fill: T.BAND_BLUE, color: T.BLUE });
  box(s, { x: 0.98, y: 2.93, w: 1.55, h: 0.55, title: "MySQL 5.7", sub: "docker volume", fill: "FFFFFF" });
  box(s, { x: 2.72, y: 1.58, w: 1.55, h: 0.55, title: "Nginx :80", sub: "bank", fill: "FFFFFF" });
  box(s, { x: 2.72, y: 2.22, w: 1.55, h: 0.62, title: "banking-app", sub: "Gunicorn", fill: T.BAND_GREEN, color: T.GREEN });
  box(s, { x: 2.72, y: 2.93, w: 1.55, h: 0.55, title: "MySQL 5.7", sub: "docker volume", fill: "FFFFFF" });
  T.callout(s, {
    x: 4.47, y: 1.58, w: 1.95, h: 1.9,
    title: "Posture",
    body: [
      "Docker Compose on one VM.",
      "Public IP, HTTP :80 only.",
      "Both apps and both databases share a single failure domain.",
    ],
    accent: "E08600", fill: "FFFFFF", fontSize: 7.8,
  });

  // Azure Prod
  s.addShape("roundRect", {
    x: 0.82, y: 3.85, w: 5.7, h: 2.35, rectRadius: 0.05,
    fill: { color: "F0F6FF" }, line: { color: T.BLUE, width: 1.25, dashType: "dash" },
  });
  s.addText("Azure  ·  Container Instances  ·  Production  ·  centralindia", {
    x: 0.92, y: 3.9, w: 5.2, h: 0.24, fontFace: T.FONT, fontSize: 9,
    bold: true, color: "0D47A1", margin: 0,
  });
  box(s, { x: 0.98, y: 4.22, w: 1.28, h: 0.55, title: "bank-app-1", sub: "ACI · 1 vCPU", fill: T.BAND_GREEN, color: T.GREEN, titleSize: 8 });
  box(s, { x: 2.38, y: 4.22, w: 1.28, h: 0.55, title: "bank-app-2", sub: "ACI · 1 vCPU", fill: T.BAND_GREEN, color: T.GREEN, titleSize: 8 });
  box(s, { x: 0.98, y: 4.87, w: 1.28, h: 0.55, title: "ecom-app-1", sub: "ACI · 1 vCPU", fill: T.BAND_BLUE, color: T.BLUE, titleSize: 8 });
  box(s, { x: 2.38, y: 4.87, w: 1.28, h: 0.55, title: "ecom-app-2", sub: "ACI · 1 vCPU", fill: T.BAND_BLUE, color: T.BLUE, titleSize: 8 });
  box(s, { x: 0.98, y: 5.52, w: 2.68, h: 0.55, title: "Azure Database for MySQL  —  public endpoint", fill: "FFFFFF", titleSize: 8 });
  T.callout(s, {
    x: 3.78, y: 4.22, w: 2.64, h: 1.85,
    title: "Gaps at this tier",
    body: [
      "No load balancer, gateway or WAF in front of the four containers.",
      "Each container has its own public DNS label.",
      "No VNet, no private endpoint, no autoscaling, no rolling update.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 7.8,
  });

  // Delivery
  s.addShape("roundRect", {
    x: 6.75, y: 1.2, w: 6.15, h: 5.58, rectRadius: 0.05,
    fill: { color: "FAFAFA" }, line: { color: T.MUTED, width: 1.25, dashType: "dash" },
  });
  s.addText("Delivery pipeline", {
    x: 6.85, y: 1.25, w: 3.0, h: 0.24, fontFace: T.FONT, fontSize: 9,
    bold: true, color: T.INK, margin: 0,
  });

  const px = 7.05, pw = 5.55;
  const steps = [
    ["Jenkins  ·  agent any", "no pinned agent, no IaC", "FFFFFF"],
    ["docker build", "image built from repository", "FFFFFF"],
    ["Docker Hub  ·  public registry", ":latest mutable tag, unsigned, unscanned", T.BAND_AMBER],
    ["Deploy to Dev  ·  AWS EC2", "ssh StrictHostKeyChecking=no to a hardcoded IP, then compose pull / up", T.BAND_AMBER],
    ["Validation gate", "curl the Dev endpoint, retry up to 2 minutes", T.BAND_GREEN],
    ["Deploy to Prod  ·  Azure ACI", "az container delete then create, per instance", T.BAND_RED],
  ];
  let sy = 1.56;
  steps.forEach((st, i) => {
    box(s, {
      x: px, y: sy, w: pw, h: 0.55, title: st[0], sub: st[1],
      fill: st[2], titleSize: 8.5, subSize: 7,
      color: st[2] === T.BAND_RED ? T.RED : st[2] === T.BAND_AMBER ? T.AMBER : st[2] === T.BAND_GREEN ? T.GREEN : T.INK,
    });
    if (i < steps.length - 1) arrow(s, px + pw / 2, sy + 0.55, px + pw / 2, sy + 0.72, {});
    sy += 0.72;
  });

  T.callout(s, {
    x: px, y: sy + 0.04, w: pw, h: 0.85,
    title: "Consequence",
    body: [
      "Delete-then-create means every production release is a planned outage, and a mutable :latest tag means the running artefact cannot be identified or deterministically rolled back.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 8,
  });

  s.addNotes(
    "Two environments with materially different topologies, and neither has an ingress tier. " +
      "The pipeline promotes correctly but deploys destructively."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   13 — System interfaces
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "System Interfaces", subtitle: "Interface inventory and integration characteristics" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "All integration is synchronous REST over cleartext HTTP. There is no message broker, no " +
      "API gateway and no service mesh in the current design.",
    { h: 0.42 }
  );

  T.table(
    s,
    [
      ["Source", "Destination", "Interface", "Type", "Frequency", "Transport / posture"],
      ["Customer device", "Nginx → ecommerce-app", "GET / · /cart · /checkout/*", "Synchronous HTML", "Interactive", "HTTP :80, cleartext"],
      ["Customer device", "ecommerce-app", "GET /api/orders/{id}/status", "Synchronous JSON", "Every 2 000 ms per open checkout", "HTTP :80, cleartext"],
      ["Customer device", "ecommerce-app", "GET /qr/{order_id}", "Image (PNG)", "Once per order", "HTTP :80, cleartext"],
      ["Customer device", "Nginx → banking-app", "GET/POST /pay · /login", "Synchronous HTML", "Interactive", "HTTP :80, cleartext"],
      [
        { text: "banking-app", bold: true },
        { text: "ecommerce-app", bold: true },
        { text: "GET /api/orders/{id}", bold: true },
        "Synchronous JSON",
        "Twice per payment",
        { text: "HTTP, public internet, 2 s / 3 s timeout", color: T.RED },
      ],
      [
        { text: "banking-app", bold: true },
        { text: "ecommerce-app", bold: true },
        { text: "POST /api/orders/{id}/paid", bold: true },
        "Synchronous JSON",
        "Once per payment",
        { text: "HTTP, public internet, 5 s timeout", color: T.RED },
      ],
      ["Container platform", "Both services", "GET /health", "Liveness / readiness", "Defined, never executed", "Only in the unused k8s manifests"],
      ["Each service", "Its own database", "SQLAlchemy / PyMySQL", "Database session", "Per request", "In-cluster or public MySQL endpoint"],
    ],
    { y: 1.72, colW: [1.75, 1.9, 2.45, 1.65, 2.05, 2.3], fontSize: 8.5, rowH: 0.42 }
  );

  T.callout(s, {
    x: T.CX, y: 5.86, w: T.CW, h: 0.56,
    title: "Interface observation",
    body: [
      "The two highlighted rows are the only east-west calls in the system, and they carry the settlement decision. In production they traverse the public internet with no private link, no mutual authentication and no retry.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 9,
  });

  s.addNotes(
    "Six of nine interfaces are customer-facing and cleartext. The two that matter most for " +
      "money movement are the two that leave the trust boundary entirely."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   14 — Technology stack
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Infrastructure and Technology Stack", subtitle: "Component versions and support position" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "Python/Flask services packaged as single-stage Docker images, fronted by Nginx and " +
      "persisted to MySQL. Versions below are the versions pinned in the repository.",
    { h: 0.42 }
  );

  T.table(
    s,
    [
      ["Layer", "Technology", "Version", "Role", "Support position"],
      ["Runtime", "Python", "3.11 (slim base image)", "Application runtime", "Supported"],
      ["Framework", "Flask", "3.0.3", "Web framework for both services", "Supported"],
      ["Framework", "Flask-SQLAlchemy", "3.1.1", "ORM and data access", "Supported"],
      ["App server", "Gunicorn", "21.2.0", "WSGI server, bound to container port 80", "Supported"],
      ["Edge", "Nginx", "Container image, :80", "Reverse proxy; no TLS configured", { text: "No TLS termination", color: T.RED }],
      ["Database", "MySQL", "5.7", "Relational store, one per service", { text: "Reached end of life October 2023", color: T.RED, bold: true }],
      ["Database", "Azure Database for MySQL", "Managed, public endpoint", "Production data tier", { text: "Supported; not privately networked", color: T.AMBER }],
      ["Fallback store", "SQLite", "Bundled with Python", "Silent fallback when DB_HOST does not resolve", { text: "Not fit for production use", color: T.RED }],
      ["Container", "Docker", "Single-stage build, runs as root", "Image packaging", { text: "USER directive present but commented out", color: T.AMBER }],
      ["Orchestration (Dev)", "Docker Compose", "v3.8 file format", "Single-VM orchestration on EC2", { text: "No HA, no scheduler", color: T.AMBER }],
      ["Orchestration (Prod)", "Azure Container Instances", "Managed", "Runs four containers, two per service", { text: "No ingress, autoscale or rolling update", color: T.RED }],
      ["Orchestration (defined)", "Kubernetes manifests", "apps/v1", "Deployment, Service, Secret — present in repo", { text: "Not deployed; Service is type LoadBalancer", color: T.AMBER }],
      ["CI/CD", "Jenkins", "Declarative pipeline, agent any", "Build, promote and deploy", "Supported"],
      ["Registry", "Docker Hub", "Public repository", "Image distribution", { text: "Mutable :latest, unsigned, unscanned", color: T.AMBER }],
    ],
    { y: 1.7, colW: [1.85, 2.25, 2.05, 3.35, 2.6], fontSize: 8.3, rowH: 0.31 }
  );

  footnote(s, "MySQL 5.7 end-of-life is the single most schedule-sensitive item in this table.");
  s.addNotes(
    "Lead with MySQL 5.7: it is out of support, which converts a technical-debt conversation " +
      "into a dated one. Moving to a managed, supported version also delivers HA and backups."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   15 — Network and remote access
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Network and Remote Access", subtitle: "Current network posture" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "There is no private networking anywhere in the current design. Every component is " +
      "reachable over the public internet on cleartext HTTP, and east-west service traffic " +
      "leaves the trust boundary and returns over the same public path.",
    { h: 0.58 }
  );

  const ty = 2.0;
  box(s, { x: 0.85, y: ty + 0.75, w: 1.5, h: 0.72, title: "Internet", sub: "any client", fill: "FFFFFF" });

  s.addShape("roundRect", {
    x: 2.7, y: ty, w: 3.05, h: 2.35, rectRadius: 0.05,
    fill: { color: "FFF8E7" }, line: { color: "E08600", width: 1.15, dashType: "dash" },
  });
  s.addText("AWS EC2 — public IP", {
    x: 2.78, y: ty + 0.05, w: 2.9, h: 0.22, fontFace: T.FONT, fontSize: 8, bold: true, color: "9A5B00", margin: 0,
  });
  box(s, { x: 2.85, y: ty + 0.38, w: 2.75, h: 0.5, title: "Security group :80 open", fill: "FFFFFF", titleSize: 8 });
  box(s, { x: 2.85, y: ty + 0.98, w: 2.75, h: 0.5, title: "Nginx → Flask (compose bridge network)", fill: "FFFFFF", titleSize: 8 });
  box(s, { x: 2.85, y: ty + 1.58, w: 2.75, h: 0.5, title: "MySQL on the same docker network", fill: "FFFFFF", titleSize: 8 });

  s.addShape("roundRect", {
    x: 6.15, y: ty, w: 3.15, h: 2.35, rectRadius: 0.05,
    fill: { color: "F0F6FF" }, line: { color: T.BLUE, width: 1.15, dashType: "dash" },
  });
  s.addText("Azure ACI — public DNS labels", {
    x: 6.23, y: ty + 0.05, w: 3.0, h: 0.22, fontFace: T.FONT, fontSize: 8, bold: true, color: "0D47A1", margin: 0,
  });
  box(s, { x: 6.3, y: ty + 0.38, w: 2.85, h: 0.5, title: "4 containers, each its own public FQDN", fill: "FFFFFF", titleSize: 8 });
  box(s, { x: 6.3, y: ty + 0.98, w: 2.85, h: 0.5, title: "No VNet · no subnet · no NSG", fill: T.BAND_RED, color: T.RED, titleSize: 8 });
  box(s, { x: 6.3, y: ty + 1.58, w: 2.85, h: 0.5, title: "Azure MySQL public endpoint", fill: T.BAND_RED, color: T.RED, titleSize: 8 });

  arrow(s, 2.35, ty + 1.11, 2.85, ty + 1.11, { label: "HTTP :80", labelSize: 7, labelDy: 0.18 });
  arrow(s, 5.75, ty + 0.63, 6.3, ty + 0.63, { label: "HTTP :80", labelSize: 7, labelDy: 0.18 });
  arrow(s, 4.22, ty + 2.35, 4.22, ty + 2.72, { color: T.RED, width: 1.4 });
  arrow(s, 7.72, ty + 2.35, 7.72, ty + 2.72, { color: T.RED, width: 1.4 });
  box(s, {
    x: 2.7, y: ty + 2.72, w: 6.6, h: 0.5,
    title: "East-west service-to-service calls traverse the public internet — no private link, no mTLS",
    fill: T.BAND_RED, color: T.RED, titleSize: 8.5,
  });

  T.callout(s, {
    x: 9.7, y: ty, w: 3.2, h: 3.22,
    title: "Absent controls",
    body: [
      "• TLS / HTTPS anywhere in the path",
      "• WAF and DDoS protection",
      "• API gateway or managed ingress",
      "• VNet, subnets, NSGs, private endpoints",
      "• Rate limiting at the edge",
      "• Bastion or just-in-time admin access",
      "• Egress control and IP allow-listing",
      "",
      "Administrative access to Dev is by SSH to a hardcoded public IP with host-key checking disabled.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 8.5,
  });

  T.callout(s, {
    x: 0.85, y: 5.5, w: 8.45, h: 0.92,
    title: "Target direction",
    body: [
      "Front Door or Application Gateway with WAF terminates TLS at the edge; workloads move into a VNet with private endpoints to the data tier; east-west traffic stays inside the VNet and is mutually authenticated. This is the prerequisite for every other hardening item.",
    ],
    accent: T.GREEN, fill: T.BAND_GREEN, fontSize: 8.5,
  });

  s.addNotes(
    "For an infra audience this is the most actionable slide: nothing here requires " +
      "application rework. It is all platform and network configuration."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   16 — Data and databases
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Data and Databases", subtitle: "Data ownership, schema and durability position" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "Each service owns a private schema, and there is no shared database and no cross-service " +
      "foreign key. The order lifecycle and the ledger are therefore two independent " +
      "consistency domains joined only by an HTTP call.",
    { h: 0.58 }
  );

  const dy2 = 2.02;
  s.addShape("roundRect", {
    x: 0.85, y: dy2, w: 4.15, h: 2.5, rectRadius: 0.05,
    fill: { color: "F7FAFF" }, line: { color: T.BLUE, width: 1.15 },
  });
  s.addText("ecomdb  —  owned by ecommerce-app", {
    x: 0.95, y: dy2 + 0.06, w: 3.9, h: 0.24, fontFace: T.FONT, fontSize: 8.5, bold: true, color: T.BLUE, margin: 0,
  });
  const et = [
    ["users", "id · username · password"],
    ["products", "id · name · price · image_url · stock"],
    ["orders", "id · user_id · total_amount · status · created_at · expires_at"],
    ["order_items", "id · order_id · product_id · product_name · price · quantity · subtotal"],
  ];
  let ey = dy2 + 0.36;
  et.forEach(([n, f]) => {
    box(s, { x: 0.95, y: ey, w: 3.95, h: 0.48, title: n, sub: f, fill: "FFFFFF", titleSize: 8, subSize: 6.8, color: T.BLUE });
    ey += 0.52;
  });

  s.addShape("roundRect", {
    x: 5.25, y: dy2, w: 4.15, h: 2.5, rectRadius: 0.05,
    fill: { color: "F5FBF6" }, line: { color: T.GREEN, width: 1.15 },
  });
  s.addText("bankdb  —  owned by banking-app", {
    x: 5.35, y: dy2 + 0.06, w: 3.9, h: 0.24, fontFace: T.FONT, fontSize: 8.5, bold: true, color: T.GREEN, margin: 0,
  });
  const bt = [
    ["accounts", "id · name · type · is_admin · password · balance"],
    ["transactions", "id · order_id · from_acct · to_acct · amount · timestamp"],
  ];
  let by2 = dy2 + 0.36;
  bt.forEach(([n, f]) => {
    box(s, { x: 5.35, y: by2, w: 3.95, h: 0.48, title: n, sub: f, fill: "FFFFFF", titleSize: 8, subSize: 6.8, color: T.GREEN });
    by2 += 0.52;
  });
  box(s, {
    x: 5.35, y: by2 + 0.06, w: 3.95, h: 0.85,
    title: "transactions.order_id is the only link to the merchant domain",
    sub: "It is a plain column — not a foreign key, and not uniquely indexed",
    fill: T.BAND_AMBER, color: T.AMBER, titleSize: 8, subSize: 7,
  });

  T.callout(s, {
    x: 9.65, y: dy2, w: 3.25, h: 2.5,
    title: "Durability position",
    body: [
      "• Single-node MySQL in both environments",
      "• No read replica or standby",
      "• No automated backup or PITR configured",
      "• Dev data sits on a local docker volume",
      "• RPO and RTO are undefined",
      "• Monetary values are stored as floating point rather than exact decimal",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 8.5,
  });

  T.table(
    s,
    [
      ["Concern", "Current position", "Required for production"],
      ["High availability", "None — single instance per environment", "Zone-redundant managed instance with automatic failover"],
      ["Backup and recovery", "Not configured; no restore has been tested", "Automated backups, point-in-time restore, periodic restore drills"],
      ["Network exposure", "Public endpoint / shared docker network", "Private endpoint, no public network access"],
      ["Cross-domain consistency", "Two commits, no coordination", "Outbox plus broker, idempotent consumers, reconciliation sweep"],
    ],
    { y: 4.72, colW: [2.0, 4.55, 5.55], fontSize: 8.5, rowH: 0.36 }
  );

  s.addNotes(
    "The durability column is the part to press: there is no backup and no tested restore. " +
      "That is an operational, not architectural, gap and it can be closed quickly."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   17 — Reporting and processes / observability
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Reporting and Processes", subtitle: "Observability and operational reporting position" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "Diagnostics today consist of unstructured print statements to container stdout. There is " +
      "no metrics pipeline, no distributed tracing, no log aggregation and no alerting.",
    { h: 0.46 }
  );

  T.table(
    s,
    [
      ["Capability", "Current state", "Operational consequence", "Recommended platform service"],
      ["Application logging", "print() to stdout, unstructured, lost on replace", "No post-incident reconstruction is possible", "Container Insights → Log Analytics"],
      ["Log retention", "None — no aggregation or retention policy", "Nothing survives a redeploy, i.e. every release", "Log Analytics workspace with retention"],
      ["Metrics", "None collected", "Saturation, latency and error rate are invisible", "Azure Monitor with workload dashboards"],
      ["Distributed tracing", "No correlation ID crosses the two services", "A payment cannot be followed across services", "OpenTelemetry → Application Insights"],
      ["Health probing", "/health exists; probes only in unused manifests", "Unhealthy containers are never replaced", "Probes enforced by the orchestrator"],
      ["Alerting and on-call", "None", "Failures are found by users, not the platform", "Alert rules bound to SLOs, routed to on-call"],
      ["Availability reporting", "No SLI, SLO or error budget defined", "Reliability cannot be stated or improved", "SLO dashboards with error-budget alerts"],
      ["Audit trail", "transactions table only; mutable", "Cannot answer a point-in-time audit question", "Append-only store, immutable retention"],
    ],
    { y: 1.72, colW: [1.95, 3.6, 3.35, 3.2], fontSize: 8.5, rowH: 0.44 }
  );

  T.callout(s, {
    x: T.CX, y: 5.88, w: T.CW, h: 0.54,
    title: "Position",
    body: [
      "The platform currently has no means of detecting that a payment failed, and no means of reconstructing one after the fact. Observability is the prerequisite for operating this service at all, ahead of any feature work.",
    ],
    accent: T.AMBER, fill: T.BAND_AMBER, fontSize: 9,
  });

  s.addNotes(
    "Tie this back to slide 11: the dual-commit exposure window is not merely possible — " +
      "today it would also be undetectable and unrecoverable."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   18 — Fault management
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Fault Management", subtitle: "Failure modes and blast radius" });

  T.table(
    s,
    [
      ["Failure event", "Platform response today", "Blast radius", "Detection"],
      ["Nginx container stops", "None — no supervisor beyond docker restart policy, no second instance", { text: "Full outage of that service", color: T.RED, bold: true }, { text: "User report", color: T.RED }],
      ["Application container stops", "ACI restarts the instance; clients pinned to that DNS label fail meanwhile", { text: "Full outage for that label", color: T.RED, bold: true }, { text: "User report", color: T.RED }],
      ["Application becomes unhealthy but stays up", "Nothing — no readiness probe is executed in the deployed path", { text: "Silent black-holing of requests", color: T.RED, bold: true }, { text: "None", color: T.RED }],
      ["Database instance fails", "No standby, no failover; connections simply fail", { text: "Full outage plus potential data loss", color: T.RED, bold: true }, { text: "User report", color: T.RED }],
      ["Database volume is lost", "No backup and no tested restore exists", { text: "Permanent ledger loss", color: T.RED, bold: true }, { text: "None until reconciliation", color: T.RED }],
      ["DB_HOST fails to resolve at start-up", "Silently falls back to a pod-local SQLite file and reports healthy", { text: "Divergent, ephemeral ledger per replica", color: T.RED, bold: true }, { text: "None — /health returns ok", color: T.RED }],
      ["Merchant callback times out after committing", "Bank aborts and tells the customer the payment failed", { text: "Permanent cross-database disagreement", color: T.RED, bold: true }, { text: "None", color: T.RED }],
      ["Production release", "Container is deleted then recreated", { text: "Planned outage on every deploy", color: T.AMBER, bold: true }, "Expected"],
      ["Availability-zone loss", "Not addressed; no zonal or regional redundancy", { text: "Total outage", color: T.RED, bold: true }, { text: "Cloud provider status", color: T.AMBER }],
    ],
    { y: T.CY + 0.06, colW: [3.05, 4.6, 2.65, 1.8], fontSize: 8.5, rowH: 0.42 }
  );

  T.callout(s, {
    x: T.CX, y: 5.56, w: 5.9, h: 0.86,
    title: "Common root cause",
    body: [
      "Every row above traces to the same two absences: no redundant, load-balanced instance at any tier, and no platform-level health enforcement.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 8.5,
  });
  T.callout(s, {
    x: 6.98, y: 5.56, w: 5.9, h: 0.86,
    title: "Highest-leverage remediation",
    body: [
      "A managed orchestrator with health-gated rolling updates plus a zone-redundant managed database closes seven of the nine rows without any application change.",
    ],
    accent: T.GREEN, fill: T.BAND_GREEN, fontSize: 8.5,
  });

  s.addNotes(
    "The 'silent SQLite fallback' row is the one that tends to land hardest with " +
      "infrastructure teams: a DNS blip becomes silent data divergence while health checks " +
      "still report success."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   19 — Performance and reliability
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Performance and Reliability", subtitle: "Current characteristics and known load behaviour" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "No load test, latency budget or throughput target exists. The figures below are " +
      "structural characteristics derived from the deployed configuration, not measurements.",
    { h: 0.46 }
  );

  T.table(
    s,
    [
      ["Dimension", "Current position", "Assessment"],
      ["Service level objective", "None defined; no SLI, SLO or error budget", { text: "Reliability cannot be stated or measured", color: T.RED }],
      ["Capacity per instance", "1 vCPU / 1 GiB per ACI container, Gunicorn default worker count", { text: "Unsized — worker count is not tuned to the CPU allocation", color: T.AMBER }],
      ["Horizontal scale", "Fixed at two containers per service; no autoscaling and no load balancer to use them", { text: "Effective concurrency is one instance", color: T.RED }],
      ["Latency profile of a payment", "Up to three sequential cross-service HTTP calls with 2 s + 3 s + 5 s timeouts", { text: "Worst-case tail latency of roughly 10 s before any database work", color: T.RED }],
      ["Polling overhead", "Each open checkout page issues 0.5 requests per second, each hitting the database", { text: "Load scales with idle browser tabs rather than with transactions", color: T.AMBER }],
      ["Database connections", "Default SQLAlchemy pool per container; no proxy or external pooler", { text: "Connection storms likely as instance count grows", color: T.AMBER }],
      ["Caching", "None at any layer", { text: "Every read reaches the database", color: T.AMBER }],
      ["Static asset delivery", "Served by the application container; no CDN", { text: "Avoidable load on the application tier", color: T.AMBER }],
      ["Backpressure", "No rate limiting, queueing or shedding anywhere", { text: "A traffic spike degrades into failure rather than delay", color: T.RED }],
    ],
    { y: 1.72, colW: [2.5, 5.15, 4.45], fontSize: 8.6, rowH: 0.42 }
  );

  T.callout(s, {
    x: T.CX, y: 6.0, w: T.CW, h: 0.46,
    title: "Note",
    body: [
      "The 10-second worst-case payment latency is a design consequence of chaining synchronous calls, not a tuning problem; it resolves only by making the settlement path asynchronous.",
    ],
    accent: T.AMBER, fill: T.BAND_AMBER, fontSize: 9,
  });

  s.addNotes(
    "The polling-overhead row usually gets attention: load is driven by open tabs rather " +
      "than by transactions, which is exactly the wrong scaling property for a payment system."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   20 — Scalability, resilience and DR
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Scalability, Resilience and Disaster Recovery" });

  T.labelValue(
    s,
    T.CY + 0.02,
    "Description/s",
    "The platform is single-region and single-instance in effect. No disaster recovery plan, " +
      "runbook or recovery objective currently exists.",
    { h: 0.46 }
  );

  const cy2 = 1.78;
  const cols = [
    {
      x: 0.85,
      title: "Scalability",
      accent: T.AMBER,
      fill: T.BAND_AMBER,
      items: [
        "Fixed instance count, set imperatively in the pipeline",
        "No autoscaling on any signal",
        "No load balancer, so the second instance receives no traffic",
        "Session state in an app-local signed cookie prevents free horizontal scaling",
        "Data tier cannot scale reads — no replica",
      ],
    },
    {
      x: 5.0,
      title: "Resilience",
      accent: T.RED,
      fill: T.BAND_RED,
      items: [
        "Single failure domain per environment",
        "No zone redundancy at app or data tier",
        "Health probes defined but never executed",
        "No retry, circuit breaker or bulkhead on cross-service calls",
        "Deployment model removes capacity before restoring it",
      ],
    },
    {
      x: 9.15,
      title: "Disaster recovery",
      accent: T.RED,
      fill: T.BAND_RED,
      items: [
        "No secondary region",
        "No database backup configured",
        "No restore has ever been tested",
        "RPO and RTO undefined and unagreed",
        "No documented recovery runbook",
      ],
    },
  ];

  cols.forEach((c) => {
    s.addShape("roundRect", {
      x: c.x, y: cy2, w: 3.75, h: 2.62, rectRadius: 0.05,
      fill: { color: c.fill }, line: { color: c.accent, width: 1.25 },
    });
    s.addText(c.title, {
      x: c.x + 0.14, y: cy2 + 0.08, w: 3.45, h: 0.28,
      fontFace: T.FONT, fontSize: 12, bold: true, color: c.accent, margin: 0, valign: "middle",
    });
    s.addText(T.bullets(c.items, { spaceAfter: 8 }), {
      x: c.x + 0.16, y: cy2 + 0.42, w: 3.46, h: 2.12,
      fontFace: T.FONT, fontSize: 9.5, color: T.INK, margin: 0, valign: "top",
      lineSpacingMultiple: 1.03,
    });
  });

  T.table(
    s,
    [
      ["Objective", "Current", "Interim target", "Production target"],
      ["Availability", { text: "Not measured", color: T.RED }, "99.0 % single region, health-gated rolling deploys", "99.9 % zone-redundant, no planned downtime"],
      ["RPO", { text: "Undefined — data loss is unbounded", color: T.RED }, "24 hours via automated daily backup", "5 minutes via point-in-time restore"],
      ["RTO", { text: "Undefined — no restore procedure exists", color: T.RED }, "4 hours with a documented, rehearsed runbook", "1 hour with automated failover"],
      ["Deployment impact", { text: "Full outage per release", color: T.RED }, "Zero-downtime rolling update", "Blue-green or canary with automated rollback"],
    ],
    { y: 4.6, colW: [1.9, 3.3, 3.55, 3.35], fontSize: 8.5, rowH: 0.35 }
  );

  footnote(s, "Interim targets are deliberately modest — they are what the existing Kubernetes manifests could deliver once actually deployed.");
  s.addNotes(
    "Ask for one decision here: agreement on RPO and RTO. Every other number on this slide " +
      "follows from those two, and neither can be chosen by the delivery team alone."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   21 — Architecture maturity assessment
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Architecture Maturity Assessment", subtitle: "Current state against a production operating bar" });

  const rows = [
    ["Compute and orchestration", 1, "ACI with fixed instances; no ingress, autoscale or rolling update", "Managed orchestrator, health-gated rolling deploys"],
    ["Networking", 1, "Public cleartext HTTP end to end; no VNet or private endpoints", "Private VNet, TLS at a WAF-protected edge"],
    ["Data platform", 1, "Single-node MySQL 5.7 (end of life); no HA, backup or PITR", "Zone-redundant managed database with tested restore"],
    ["Service integration", 1, "Synchronous, bidirectional HTTP; no broker, retry or reconciliation", "Asynchronous events with outbox and idempotency"],
    ["Delivery and supply chain", 2, "Gated Dev→Prod promotion, but destructive deploys from a mutable tag", "Immutable signed digests, scanned images, progressive delivery"],
    ["Configuration and secrets", 1, "Credentials inline in pipeline definitions; no secret store", "Managed identity plus a secret store, no static credentials"],
    ["Infrastructure as code", 1, "None — imperative CLI calls create cloud resources", "Declarative IaC in version control with drift detection"],
    ["Observability", 1, "Unstructured stdout only; no metrics, tracing or alerting", "Full telemetry pipeline with SLO-based alerting"],
    ["Resilience and DR", 1, "Single region, single instance; no backup, RPO/RTO undefined", "Multi-zone with agreed and rehearsed recovery objectives"],
    ["Health and self-healing", 2, "/health endpoints exist and probes are written, but are not deployed", "Probes enforced by the orchestrator with automatic replacement"],
  ];

  const tbl = [["Domain", "Level", "Current position", "Production bar"]].concat(
    rows.map((r) => [
      { text: r[0], bold: true },
      { text: `${r[1]} / 5`, color: r[1] <= 1 ? T.RED : T.AMBER, bold: true, align: "center" },
      r[2],
      r[3],
    ])
  );

  T.table(s, tbl, {
    y: T.CY + 0.06,
    colW: [2.4, 0.75, 4.85, 4.1],
    fontSize: 8.5,
    rowH: 0.4,
  });

  T.callout(s, {
    x: T.CX, y: 5.68, w: 5.9, h: 0.74,
    title: "What is already right",
    body: [
      "Clean service separation with private schemas, health endpoints, environment-driven configuration, an idempotent seed, and a Dev→Prod pipeline with a validation gate. The foundations are sound.",
    ],
    accent: T.GREEN, fill: T.BAND_GREEN, fontSize: 8.5,
  });
  T.callout(s, {
    x: 6.98, y: 5.68, w: 5.9, h: 0.74,
    title: "What blocks production",
    body: [
      "No redundancy, no private networking, no backup, no observability, and an unsupported database version. These are platform gaps, not application defects.",
    ],
    accent: T.RED, fill: T.BAND_RED, fontSize: 8.5,
  });

  s.addNotes(
    "Be even-handed: the application decomposition is genuinely good for a prototype. " +
      "What is missing is a platform underneath it, which is precisely this audience's remit."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   22 — Recommended direction
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Recommended Direction", subtitle: "Sequenced by risk reduction per unit of effort" });

  const phases = [
    {
      x: 0.85,
      tag: "PHASE 1",
      title: "Stop the bleeding",
      sub: "Weeks 1–2 · configuration only",
      accent: T.RED,
      fill: T.BAND_RED,
      items: [
        "Enable automated database backups and perform a test restore",
        "Terminate TLS at a managed edge; disable plain HTTP",
        "Move credentials out of pipeline definitions into a secret store",
        "Remove the silent SQLite fallback so failures are loud",
        "Ship container logs to a Log Analytics workspace",
      ],
    },
    {
      x: 5.0,
      tag: "PHASE 2",
      title: "Make it operable",
      sub: "Weeks 3–8 · platform work",
      accent: T.AMBER,
      fill: T.BAND_AMBER,
      items: [
        "Deploy the existing manifests to a managed orchestrator",
        "Health-gated rolling updates to end deployment downtime",
        "Managed database with zone redundancy and private endpoint",
        "Workloads into a VNet; private east-west traffic only",
        "Private registry with immutable digests and image scanning",
        "Metrics, tracing and correlation IDs across both services",
      ],
    },
    {
      x: 9.15,
      tag: "PHASE 3",
      title: "Make it correct at scale",
      sub: "Quarter 2 · architecture change",
      accent: T.GREEN,
      fill: T.BAND_GREEN,
      items: [
        "Replace the synchronous callback with broker-based events",
        "Transactional outbox plus idempotent consumers",
        "Scheduled reconciliation between the two domains",
        "Autoscaling driven by real throughput signals",
        "Declarative IaC for every environment",
        "Agreed RPO/RTO with a rehearsed recovery runbook",
      ],
    },
  ];

  phases.forEach((p) => {
    s.addShape("roundRect", {
      x: p.x, y: T.CY + 0.06, w: 3.75, h: 4.24, rectRadius: 0.05,
      fill: { color: "FFFFFF" }, line: { color: p.accent, width: 1.4 },
    });
    s.addShape("rect", {
      x: p.x, y: T.CY + 0.06, w: 3.75, h: 0.3,
      fill: { color: p.accent }, line: { type: "none" },
    });
    s.addText(p.tag, {
      x: p.x + 0.12, y: T.CY + 0.06, w: 3.5, h: 0.3,
      fontFace: T.FONT, fontSize: 8.5, bold: true, color: "FFFFFF",
      margin: 0, valign: "middle", charSpacing: 1.2,
    });
    s.addText(
      [
        { text: p.title, options: { bold: true, fontSize: 12.5, breakLine: true, color: T.INK } },
        { text: p.sub, options: { fontSize: 8.5, italic: true, color: T.MUTED } },
      ],
      {
        x: p.x + 0.14, y: T.CY + 0.44, w: 3.45, h: 0.6,
        fontFace: T.FONT, margin: 0, valign: "top", lineSpacingMultiple: 1.0,
      }
    );
    s.addText(T.bullets(p.items, { spaceAfter: 9 }), {
      x: p.x + 0.16, y: T.CY + 1.02, w: 3.46, h: 3.16,
      fontFace: T.FONT, fontSize: 10, color: T.INK, margin: 0, valign: "top",
      lineSpacingMultiple: 1.04,
    });
  });

  T.callout(s, {
    x: T.CX, y: 5.5, w: T.CW, h: 0.92,
    title: "Sequencing rationale",
    body: [
      "Phase 1 is configuration only and removes the risk of unrecoverable data loss and cleartext credentials within a fortnight — no application change is required.",
      "Phase 2 is platform work that reuses the Kubernetes manifests already written, and it closes seven of the nine fault-management rows.",
      "Phase 3 is the only phase requiring application change, and it is the only way to make the two-database settlement path correct under failure.",
    ],
    accent: T.BLUE, fill: "F0F6FF", fontSize: 8.8,
  });

  s.addNotes(
    "Close on the ask: endorsement of the Phase 1 list, agreement on RPO/RTO, and a decision " +
      "on the Phase 2 orchestrator target. Phase 3 needs no decision today."
  );
}

/* ══════════════════════════════════════════════════════════════════════
   23 — Other design details
   ══════════════════════════════════════════════════════════════════════ */
{
  const s = newSlide({ title: "Other Design Details" });
  let y = T.CY + 0.06;

  T.labelValue(
    s,
    y,
    "Testing Approach",
    [
      ...T.bullets([
        "No automated test suite, and no test stage in the pipeline",
        "The only gate is a curl reachability check against the Dev endpoint after deployment",
        "For this review both services were executed end to end and the payment journey observed and captured",
        "Required before production: integration tests across the service boundary, a failure-injection exercise on the settlement path, and a load test to establish a latency budget",
      ]),
    ],
    { h: 1.28 }
  );
  y += 1.36;

  T.labelValue(
    s,
    y,
    "Deployment Approach",
    [
      ...T.bullets([
        "Jenkins builds one image per service and promotes the same artefact from Dev to Prod",
        "Dev deployment is SSH plus Docker Compose onto a single EC2 host",
        "Production deployment deletes and recreates each Azure Container Instance, which incurs downtime on every release",
        "No rollback path — the :latest tag is mutable, so the previous artefact is not addressable",
      ]),
    ],
    { h: 1.28 }
  );
  y += 1.36;

  T.labelValue(
    s,
    y,
    "Cost Position",
    "Current footprint is small: one EC2 instance, four 1 vCPU container instances and one " +
      "managed MySQL instance. The Phase 1 and Phase 2 recommendations are largely " +
      "configuration and managed-service adoption rather than net new capacity, so the " +
      "material cost increase is the managed database HA tier and the log analytics workspace.",
    { h: 0.86 }
  );
  y += 0.94;

  T.labelValue(
    s,
    y,
    "Decisions Requested",
    [
      ...T.bullets([
        { text: "Confirm whether the Azure and AWS subscriptions in the pipeline are lab or production", bold: true },
        { text: "Agree RPO and RTO so the data-tier design can be fixed", bold: true },
        { text: "Endorse the Phase 1 remediation list and nominate the Phase 2 orchestrator target", bold: true },
      ]),
    ],
    { h: 0.86 }
  );

  s.addNotes(
    "Finish on the three decisions. Keep it short — the deck has already made the case, and " +
      "this slide only needs to capture what we are asking them to sign off."
  );
}

/* ══════════════════════════════════════════════════════════════════════ */
pptx
  .writeFile({ fileName: OUT })
  .then(() => console.log(`Wrote ${OUT}  (${page} slides)`))
  .catch((e) => {
    console.error("FAILED:", e);
    process.exit(1);
  });
