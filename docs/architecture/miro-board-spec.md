# Miro Board Specification

## Status: board not yet created

I was **unable to create the Miro board.** The `miro-codegen` power is installed, but its
MCP server is currently exposing zero tools, which means the Miro OAuth connection has not
been authorised for this session. I attempted the connection and confirmed the tool list
is empty — this is not something I can work around from my side.

**To unblock:** authorise the Miro connection (the power prompts for OAuth on activation),
selecting the **specific Miro team** that should own the board. Once that is done, say the
word and I will build the board directly — the layout below is the spec I will build to,
so it should take one pass.

In the meantime, every diagram is available as validated Mermaid, which Miro can import.

---

## Option A — import the Mermaid sources (fastest)

All seven diagrams are in [`diagrams/`](diagrams/) as `.mmd` files, and all seven have
been parsed and validated against Mermaid 11, so they will not fail on import.

In Miro, use the diagramming/Mermaid import entry point and paste the contents of one
`.mmd` file per frame. Miro's menu placement for this has moved between releases, so look
for *Diagram*, *Diagram as code*, or *Mermaid* in the toolbar or the apps panel.

| Paste into frame | Source file |
|---|---|
| 1 — Current State | `diagrams/01-current-state.mmd` |
| 3 — Network Topology | `diagrams/02-azure-network-topology.mmd` |
| 4 — Runtime Flow | `diagrams/03-azure-runtime-flow.mmd` |
| 5 — Service Domains | `diagrams/04-service-domain-map.mmd` |
| 6 — Payment Saga | `diagrams/05-payment-saga.mmd` |
| 7 — CI/CD | `diagrams/06-cicd-gitops.mmd` |
| 8 — DR Topology | `diagrams/07-dr-topology.mmd` |

Frame 2 (Findings) is sticky notes rather than a diagram — see below.

## Option B — view on GitHub instead

GitHub renders Mermaid natively. If the goal is review rather than workshopping,
[target-azure-architecture.md](target-azure-architecture.md) already displays all six
target-state diagrams inline with no import step.

---

## Board layout

Single board, nine frames on a horizontal spine with a vertical drop for the findings
wall. Coordinates assume Miro's centre-origin canvas, units in board pixels.

```
                                    ┌──────────────────────────────────────┐
                                    │  0 · TITLE / LEGEND    (1400×800)    │
                                    │  x=0      y=-2400                    │
                                    └──────────────────────────────────────┘

┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ 1 · CURRENT STATE │──▶│ 2 · FINDINGS WALL │──▶│ 3 · NETWORK       │
│ 2400×1600         │   │ 2400×2000         │   │ 3200×2200         │
│ x=-5200 y=0       │   │ x=-2400 y=0       │   │ x=1200 y=0        │
└───────────────────┘   └───────────────────┘   └───────────────────┘
                                                          │
        ┌─────────────────────────────────────────────────┘
        ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ 4 · RUNTIME FLOW  │──▶│ 5 · SERVICE       │──▶│ 6 · PAYMENT SAGA  │
│ 3400×1800         │   │     DOMAINS       │   │ 2400×2600         │
│ x=1200 y=2600     │   │ 2800×2200         │   │ x=8000 y=2600     │
└───────────────────┘   │ x=4800 y=2600     │   └───────────────────┘
                        └───────────────────┘
        ┌─────────────────────────────────────────────────┐
        ▼                                                 ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ 7 · CI/CD         │──▶│ 8 · DR TOPOLOGY   │──▶│ 9 · ROADMAP       │
│ 3000×1600         │   │ 2800×2000         │   │ 2400×1800         │
│ x=1200 y=5600     │   │ x=4600 y=5600     │   │ x=7600 y=5600     │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

### Frame contents

| # | Frame | Content |
|---|---|---|
| 0 | Title / Legend | Board title, date, colour legend, link back to this repo path |
| 1 | Current State | `01-current-state.mmd`. Red-fill the four components that carry critical findings. |
| 2 | Findings Wall | 14 sticky notes, one per finding — see grid below |
| 3 | Network Topology | `02-azure-network-topology.mmd` |
| 4 | Runtime Flow | `03-azure-runtime-flow.mmd` |
| 5 | Service Domains | `04-service-domain-map.mmd` |
| 6 | Payment Saga | `05-payment-saga.mmd` |
| 7 | CI/CD | `06-cicd-gitops.mmd` |
| 8 | DR Topology | `07-dr-topology.mmd` |
| 9 | Roadmap | Six swimlanes, Phase 0–5, from `migration-roadmap.md` |

### Frame 2 — findings wall

Sticky notes, 4 columns × 4 rows, 400×400 each with 60px gutters. Colour by severity:
`red` = critical, `orange` = high, `yellow` = medium.

| Position | ID | Colour | Text |
|---|---|---|---|
| r1c1 | F-01 | red | Unauthenticated `/paid` endpoint → free goods |
| r1c2 | F-02 | red | Client-supplied amount → pay ₱0.01 for any order |
| r1c3 | F-03 | red | Unsigned QR → redirect funds, revive expired QR |
| r1c4 | F-04 | red | Callback before debit → paid with no funds moved |
| r2c1 | F-05 | orange | Double-spend race, no unique constraint |
| r2c2 | F-06 | orange | Float money columns → ledger will not reconcile |
| r2c3 | F-07 | orange | Plaintext passwords, `==` compare, no MFA |
| r2c4 | F-08 | orange | Hardcoded secret keys → forge admin, mint funds |
| r3c1 | F-09 | orange | Live DB credentials in public git history |
| r3c2 | F-10 | yellow | Containers run as root, `USER` commented out |
| r3c3 | F-11 | yellow | Silent SQLite fallback → silent ledger divergence |
| r3c4 | F-12 | yellow | Plaintext K8s Secret, public LoadBalancer |
| r4c1 | F-13 | yellow | No rate limiting, fraud controls, or AML hooks |
| r4c2 | F-14 | yellow | No observability — cannot answer an audit |
| r4c3 | — | red | **Chain:** F-01 + F-02 + F-03 + F-04 = free goods, redirected funds, undetectable |
| r4c4 | — | dark_blue | **Every finding maps to a target control.** See `critical-findings.md`. |

### Colour legend

| Colour | Meaning |
|---|---|
| Red | Critical finding / current-state defect |
| Orange | High severity |
| Yellow | Medium severity |
| Green | Target-state control, correct by construction |
| Blue | Azure security or governance service |
| Grey | External system or national payment rail |

### Connectors

| From | To | Label |
|---|---|---|
| Frame 1 | Frame 2 | assessed |
| Frame 2 | Frame 3 | drives controls |
| Frame 3 | Frame 4 | deploys into |
| Frame 4 | Frame 5 | decomposes to |
| Frame 5 | Frame 6 | payment path |
| Frame 6 | Frame 7 | delivered by |
| Frame 7 | Frame 8 | resilience |
| Frame 8 | Frame 9 | sequenced by |

---

## What I will do once Miro is connected

1. Create board `QR Payment Platform — Azure Target Architecture` in the team you select.
2. Create frames 0–9 at the coordinates above.
3. Import each `.mmd` into its frame.
4. Create the 16 sticky notes on the findings wall with severity colours.
5. Draw the eight inter-frame connectors.
6. Build the Phase 0–5 roadmap swimlanes.
7. Return the board URL.
