# Interactive Architecture — Hub and Spoke

Five explorable scenes of the **same** target architecture already documented in
[`../excalidraw/05-network-topology.excalidraw`](../excalidraw/05-network-topology.excalidraw).

Nothing here is a new design. The topology, the two separate database servers, the single hub
firewall, the Service-Bus-only link between the applications, and every correction carried in from
the proposal paper's technical review are unchanged. What changed is that a reader can now
interrogate them instead of scanning a wall of twenty-five cards.

Each `.html` file is **self-contained** — no build step, no network fetch, no dependencies. Open it
in a browser. Start at [`index.html`](index.html).

## Why five scenes instead of one denser page

The static page 5 had to answer every question at once, so it answered each one partially. These
scenes each answer one question fully and hand the rest to a sibling:

| # | Scene | Type | Question it answers |
|---|-------|------|---------------------|
| 1 | [`01-network-topology.html`](01-network-topology.html) | Architecture | Which network does each hop happen in, and what can reach what? |
| 2 | [`02-payment-sequence.html`](02-payment-sequence.html) | Sequence | What happens, in order, during one banking payment? |
| 3 | [`03-audit-and-residency.html`](03-audit-and-residency.html) | Data flow | Where does a record go, and what can a BSP examiner read? |
| 4 | [`04-build-and-run.html`](04-build-and-run.html) | Workflow | How does a change reach a cluster with no public API server? |
| 5 | [`05-payment-lifecycle.html`](05-payment-lifecycle.html) | Lifecycle | What states can a payment hold, and how does it end? |

Every scene carries **five guided chapters**. Press <kbd>P</kbd> to play them in order.

## What a click gives you

Scene 1 is built to be interrogated node by node. Clicking any box opens its **semantic passport**:

| Field | Example on `AKS: banking` |
|-------|---------------------------|
| Kind | `BACKEND` |
| What it is | private cluster |
| Which network holds it | `Spoke: banking 10.1.0.0/16` |
| How it behaves | no public API server; KEDA autoscale |
| Degree | 5 outgoing · 1 incoming |
| Authored reach | upstream 5, downstream 7 |
| Every line that touches it | → `PostgreSQL: bankdb` *SQL 5432, private endpoint* · → `Core banking, PH` *ExpressRoute, never public* · → `Service Bus Premium` *AMQP outbox rows* · → `Azure Managed Redis` *sessions + locks* · → `Azure Firewall` *internet-bound* · ← `API Management` *request + claims* |

So "what does this do" and "what is being sent" are both answerable without leaving the diagram. Every
relationship label names the protocol, port or payload rather than restating its endpoints, and the
passport lists them per node with direction.

Three levels of detail are deliberate, because a diagram that shows everything at once shows nothing:

- **MAP** (below 100%) — shapes and frames only.
- **READ** (100%, the default) — labels and the one-line "what it is".
- **FULL** (past 175%) — the behaviour line on every box. Focusing a node reveals its own detail at
  any zoom, so you never have to zoom to read the thing you clicked.

The frames are network boundaries, so a node's context line is the VNet or facility that actually
holds it. The managed data services sit outside every frame on purpose: a private endpoint puts a
network interface in your subnet, but the service itself stays Azure-managed.

## Controls

| Key | Action |
|-----|--------|
| <kbd>?</kbd> | the full control list |
| <kbd>P</kbd> / <kbd>[</kbd> <kbd>]</kbd> | play the chapters / step through them |
| <kbd>/</kbd> | find a node by label or id |
| <kbd>R</kbd> | trace the directed route between two nodes |
| <kbd>L</kbd> | compare two kinds of node |
| <kbd>M</kbd> | overview radar |
| <kbd>F</kbd> | presentation mode |
| <kbd>T</kbd> / <kbd>S</kbd> | light or dark / visual style |
| <kbd>E</kbd> | export PNG, JPEG, WebP, dual-theme SVG, WebM, share card |
| <kbd>+</kbd> <kbd>-</kbd> <kbd>0</kbd> | zoom, reset |

Selecting a node opens its upstream and downstream relationships and a copyable deep link.
Deep links restore state: `#view=<chapter-id>`, `#focus=<node-id>`,
`#focus=<node-id>&reach=upstream`, `#route=<source>~<target>`.

Tracing shows **authored reachability only**. The viewer never infers a path, a verb, or a runtime
consequence that is not in the typed source — so a route it will not draw is a route this design
does not have.

## Regenerating

The typed JSON IR for every scene lives in [`src/`](src). It is the source of record; the HTML is
build output. To rebuild, install the [Archify](https://github.com/tt-a1i/archify) skill and run,
from the `archify/` directory:

```bash
node bin/archify.mjs deliver architecture src/01-network-topology.architecture.json  01-network-topology.html   --quality showcase
node bin/archify.mjs deliver sequence     src/02-payment-sequence.sequence.json      02-payment-sequence.html   --quality showcase
node bin/archify.mjs deliver dataflow     src/03-audit-and-residency.dataflow.json   03-audit-and-residency.html --quality showcase
node bin/archify.mjs deliver workflow     src/04-build-and-run.workflow.json         04-build-and-run.html      --quality showcase
node bin/archify.mjs deliver lifecycle    src/05-payment-lifecycle.lifecycle.json    05-payment-lifecycle.html  --quality showcase
```

`deliver` refuses to replace a good artifact with a failing one: it renders a candidate, runs nine
artifact checks plus the showcase composition gate, and only then commits the HTML. All five scenes
pass with **zero errors and zero warnings**.

Browser evidence was collected separately with `visual-check`, which measures the delivered file at
1440×900, 1600×1000, 1920×1080 and 2048×1320 in both themes. All five contain without scrolling and
keep their smallest node text above the 6px projected-readability floor at every size.

## Editing notes, so the next change does not fight the renderer

Learned the hard way while authoring these; they are renderer constraints, not preferences.

- **Guided chapters are capped at five per scene.** That cap is why the material is split across
  five scenes rather than piled into one.
- **Keep the rendered diagram under roughly 500px tall at a 1440×900 viewport**, which works out to
  `1036 × viewBoxHeight / viewBoxWidth ≤ 500`. Overshoot it and the page scrolls, which fails
  containment.
- **Sequence, data-flow and lifecycle sublabels render at 7px.** At a viewBox wider than about
  1085 they fall below the 6px readability floor, so scenes 2 and 5 carry no sublabels and put that
  wording into the node label, the chapter note, or a card instead.
- **In a lifecycle, every lane except `main` and `terminal` shares one vertical band.** Two states
  in different non-terminal lanes at the same column will collide unless one gets a `yOffset`.
- **In architecture grid mode, `cellW`/`cellH` set the pitch, not the node size.** Set `size`
  explicitly per component or every node stays 120×60.
- A relationship label needs a clear gap wider than `6.5 × characters + 13 + 8` pixels. Widen the
  gap or move the label; do not delete the wording to pass the check.
- **Node text has two different budgets, and they are not the same number.** At scene 1's 150px node
  width and 1350 viewBox: a `sublabel` must stay at or under **27 characters**, because it is
  measured by the readability gate and may not shrink below 8.7px; a `tag` may run to **39
  characters**, because it renders as fine detail and is exempt. Put the short identity in the
  sublabel and the specific behaviour in the tag — the passport shows both regardless.
- **Vertical relationships tolerate much longer labels than horizontal ones.** A horizontal label is
  bounded by the inter-column gap; a vertical one is only bounded by the neighbouring columns. That
  is why `SQL 5432, private endpoint` fits on a vertical edge and `request + claims` is as long as
  the horizontal ones get.
- **Four cards do not fit.** Cards lay out in one row, so a fourth column makes every card narrower,
  wraps more lines and pushes the page past the viewport. Three cards, at most four items each.

### Source evidence is available but not enabled

Archify can mark a node `SRC n` and link it to Git-verified files and line ranges, pinned to one
public commit. It is deliberately **not** enabled here: `deliver` verifies the evidence by comparing
`git remote get-url origin` against the authored `https://github.com/...` URL, and the environment
these scenes were built in proxies every Git remote through a gateway host, so that comparison can
never match. Enabling it by rewriting the remote would have made the artifact assert a provenance
check that had not actually run.

On an ordinary checkout it is two additions. Add to `meta`:

```json
"repository": {
  "url": "https://github.com/jmbilbao25/Banking-App",
  "revision": "13598d1e9480fa2920a2cb439f93a4e554e4035b"
}
```

then add `sources` to the four components that exist as code today, and deliver with
`--repo-root <path-to-checkout>`:

| Component | Source worth citing |
|---|---|
| `aksBank` | `banking-app/app.py` L11–37 — the Flask app this cluster would run |
| `bankdb` | `banking-app/models.py` L6–22 — today's schema, with `Float` money and no unique `order_id` |
| `aksShop` | `ecommerce-app/app.py` L1–40 — the shop service this cluster would run |
| `ecomdb` | `ecommerce-app/models.py` L12–30 — products, orders and stock as they exist today |

The other nine components have no code to cite, which is itself the useful signal: four of thirteen
boxes exist today and the rest are proposed.

## What these scenes claim

Nothing in this folder is deployed. Address ranges, node counts and sizes are proposals, not
EastWest's configuration.

Carried forward deliberately, because a diagram that hides its corrections is worse than one that
never made them:

- Front Door cannot use a VNet-injected classic API Management instance as a Private Link origin,
  so an internal Application Gateway is the origin (§9.1).
- A private endpoint's /32 route beats a 0.0.0.0/0 route, so application-to-database traffic is
  **not** firewall-inspected — and scene 1 has a chapter that says exactly that (§9.3).
- "No public IP address" was withdrawn in favour of "no workload endpoint is reachable from the
  internet" (§9.4).
- Private DNS zones resolve endpoint names; the DNS Private Resolver only forwards to and from
  on-premises (§9.5).
- The single 99.99% availability figure and the USD 16k monthly run rate are **withdrawn**, not
  restated (§9.8, §9.9).
- Seven-year locked retention against RA 10173 erasure rights remains open and needs a written
  legal position (§9.6).

Sources: [`CloudConsolidation_ProposalPaper.md`](../../consolidation/CloudConsolidation_ProposalPaper.md)
§8.1, §8.4, §8.5, §9.1–§9.10 and §10; the six static pages in [`../excalidraw`](../excalidraw);
database ownership per `banking-app/app.py`.

Rendered with [Archify](https://github.com/tt-a1i/archify) (MIT).
