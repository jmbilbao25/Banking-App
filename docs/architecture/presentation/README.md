# Current-State System Design Deck

EastWest Bank DRB/ARB-style presentation of the **current** (as-is) architecture of the
QR payment platform, scoped to **cloud and infrastructure** concerns.

| File | Contents |
|---|---|
| `QR-Payment-Platform-System-Design.pptx` | Editable deck, 23 slides, 16:9 |
| `QR-Payment-Platform-System-Design.pdf` | Same deck for distribution |
| `screenshots/` | Screenshots captured from the prototype running end to end |
| `generator/` | Scripts that produce everything above |

## Slide map

| # | Slide | Notes |
|---|---|---|
| 1 | Title | |
| 2 | Project Details | Scope and objectives |
| 3 | Design Considerations | Approach, alternatives, constraints, dependencies |
| 4 | Assumptions | With impact-if-invalid column |
| 5 | Architecture and Platform Risks | R-1 … R-8, exposure-classified |
| 6 | Solution Overview | System context and integration shape |
| 7–9 | User Interfaces | Real screenshots of the merchant and bank journeys |
| **10** | **Runtime Sequence — end to end** | Every network hop, port, protocol and timeout |
| **11** | **Runtime Sequence — settlement call chain** | Commit ordering and the exposure window |
| 12 | Deployment topology | AWS Dev, Azure Prod, and the delivery pipeline |
| 13 | System Interfaces | Interface inventory |
| 14 | Infrastructure and Technology Stack | Versions and support position |
| 15 | Network and Remote Access | Current network posture |
| 16 | Data and Databases | Ownership, schema, durability |
| 17 | Reporting and Processes | Observability position |
| 18 | Fault Management | Failure modes and blast radius |
| 19 | Performance and Reliability | |
| 20 | Scalability, Resilience and DR | With RPO/RTO targets |
| 21 | Architecture Maturity Assessment | Scored against a production bar |
| 22 | Recommended Direction | Three phases, sequenced by risk reduction |
| 23 | Other Design Details | Testing, deployment, cost, decisions requested |

Slides 10 and 11 are drawn as **native PowerPoint shapes**, not images, so lanes,
arrows and labels stay editable. Their Mermaid equivalents live in
[`../diagrams/`](../diagrams/) as `08-current-payment-sequence.mmd` and
`09-current-failure-modes.mmd`.

## Regenerating

Screenshots are captured against both services running locally on SQLite:

```bash
cd ecommerce-app && USE_SQLITE=1 BANK_PUBLIC_BASE=http://127.0.0.1:5001 \
  MERCHANT_ACCOUNT=techstart-grocery python3 app.py &
cd banking-app   && USE_SQLITE=1 ECOM_CALLBACK_BASE=http://127.0.0.1:5000 python3 app.py &

cd docs/architecture/presentation/generator
python3 capture.py     # drives the full journey, writes shots/
python3 crop.py        # trims dead space -> shots_trimmed/
npm install pptxgenjs
node build.js          # writes the .pptx
```

PDF export (LibreOffice):

```bash
soffice --headless --convert-to pdf QR-Payment-Platform-System-Design.pptx
```

`capture.py` asserts each redirect and state transition as it goes, so it fails loudly
if the flow changes — the screenshots cannot silently drift from the application.

## Provenance

Every factual claim in the deck was reconstructed from the repository contents
(`app.py`, `models.py`, `Dockerfile`, `Jenkinsfile`, `docker-compose.*.yml`, `nginx/`,
`k8s/`) or observed during a live end-to-end run. Nothing is taken from the README's
aspirational description.

The deck is design-only. **No application code was changed to produce it.**
