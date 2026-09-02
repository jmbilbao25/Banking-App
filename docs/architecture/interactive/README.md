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
