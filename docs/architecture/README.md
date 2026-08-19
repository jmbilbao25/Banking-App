# QR Payment Platform — Architecture Review & Azure Target State

Design-only deliverable. **No application code is changed by these documents.**

| Doc | Contents |
|---|---|
| [current-state.md](current-state.md) | As-is architecture, rendered from the actual repo contents |
| [critical-findings.md](critical-findings.md) | Exploitable defects found in `banking-app/` and `ecommerce-app/` |
| [target-azure-architecture.md](target-azure-architecture.md) | Azure-native target state, all diagrams |
| [bsp-compliance-matrix.md](bsp-compliance-matrix.md) | BSP / NPC / AMLA / PCI-DSS traceability |
| [migration-roadmap.md](migration-roadmap.md) | Phased plan, sequenced by risk reduction |
| [miro-board-spec.md](miro-board-spec.md) | Board layout spec + import instructions |

## Diagram sources

Mermaid sources live in [`diagrams/`](diagrams/) so they can be imported into Miro
without copy-pasting out of Markdown:

| File | Diagram |
|---|---|
| `diagrams/01-current-state.mmd` | Current architecture |
| `diagrams/02-azure-network-topology.mmd` | Hub-and-spoke landing zone |
| `diagrams/03-azure-runtime-flow.mmd` | End-to-end request/data flow |
| `diagrams/04-service-domain-map.mmd` | Microservice decomposition |
| `diagrams/05-payment-saga.mmd` | Payment saga sequence (target state) |
| `diagrams/06-cicd-gitops.mmd` | Supply chain and delivery |
| `diagrams/07-dr-topology.mmd` | Multi-region DR |
| `diagrams/08-current-payment-sequence.mmd` | **Current-state** end-to-end runtime sequence |
| `diagrams/09-current-failure-modes.mmd` | **Current-state** failure modes and blast radius |

GitHub renders these inline in the Markdown files. For Miro, see
[miro-board-spec.md](miro-board-spec.md).

## Scope note

The repository is presently a **functional prototype**, and it is well organised as one.
This review assesses it against the bar it would have to clear to operate as a
BSP-supervised payment service in the Philippines — a deliberately much higher bar than
the one the prototype was built to. Findings are severity-ranked so the prototype can be
hardened incrementally rather than rewritten.
