# Presentation decks

Two decks for two audiences.

| Deck | Slides | Use it for |
|---|---|---|
| **`TechStart-QR-Payment-Infra-Review.pptx`** | 12 | **The one you present.** TechStart branding, light on words, built around the four platform topics we need infra input on. |
| `QR-Payment-Platform-System-Design.pptx` | 23 | Detailed reference pack in EastWest DRB/ARB template. Use as the appendix / leave-behind. |

PDFs of both sit alongside them. `screenshots/` holds the captures used by both.

---

## The presentation deck — TechStart

TechStart palette from the TechStart Program banner: magenta `C2007B`, deep purple
`6B1F7C`, lime `C4D82E`, gold dot texture. EastWest diamond mark and wordmark on every
slide. No confidentiality sidebar.

| # | Slide | Notes |
|---|---|---|
| 1 | Title | Diagonal ribbon motif |
| 2 | What we built | Four cards + five verified figures |
| 3 | Business requirements and assumptions | Six requirements with status, assumptions, the one functional gap |
| 4 | User flow | Left-to-right flowchart, native shapes |
| 5 | Target architecture — hub and spoke | The real Excalidraw board, plus the 1→7 request path |
| 6 | The application, running | Three live captures |
| 7 | How a payment moves | Nine steps; the two-commit gap highlighted |
| 8 | **High availability** | Layer-by-layer, today vs target |
| 9 | **Scalability on Kubernetes** | ACI today vs AKS, plus the blockers |
| 10 | **Observability** | Logs / metrics / traces, now vs target |
| 11 | **BSP readiness** | Six instruments mapped |
| 12 | **Feedback and recommendations** | **Deliberately blank** — filled in live with the infra team |

Every topic slide ends with an "Ask the infra team" card, so the session has somewhere
to go. Slide 12 is the capture surface.

### Notes on accuracy

- Slide 4 corrects the source flow diagram: QR validity is **300 s (5 minutes)**, not 3.
- Slide 5 uses `excalidraw/preview/05-network-topology.png`, the hub-and-spoke board.
- Slide 11 is an **engineering mapping, not a legal opinion**. Confirm every citation
  with Compliance and Legal.
- Images are placed by reading each PNG's real dimensions and fitting to aspect, so
  nothing is stretched.

---

## Regenerating

Screenshots come from both services running locally on SQLite:

```bash
cd ecommerce-app && USE_SQLITE=1 BANK_PUBLIC_BASE=http://127.0.0.1:5001 \
  MERCHANT_ACCOUNT=techstart-grocery python3 app.py &
cd banking-app   && USE_SQLITE=1 ECOM_CALLBACK_BASE=http://127.0.0.1:5000 python3 app.py &

cd docs/architecture/presentation/generator
python3 capture.py      # drives the real journey -> shots/
python3 crop.py         # trims dead space   -> shots_trimmed/
npm install pptxgenjs
node build-ts.js        # the 12-slide TechStart deck
node build.js           # the 23-slide reference pack
```

PDF export:

```bash
soffice --headless --convert-to pdf TechStart-QR-Payment-Infra-Review.pptx
```

`capture.py` asserts each redirect and state transition, so it fails loudly if the
application changes — screenshots cannot silently drift.

## Generator layout

| File | Role |
|---|---|
| `generator/ts-theme.js` | TechStart theme: chrome, ribbon, EastWest logo, cards, tables, aspect-correct image fitting |
| `generator/build-ts.js` | The 12-slide presentation deck |
| `generator/theme.js` | EastWest DRB/ARB theme for the reference pack |
| `generator/seq.js` | Native-shape sequence diagram renderer |
| `generator/build.js` | The 23-slide reference pack |
| `generator/capture.py` | Playwright walkthrough of the live payment journey |
| `generator/crop.py` | Screenshot dead-space trimming |

## Provenance

Facts come from the repository (`app.py`, `models.py`, `Dockerfile`, `Jenkinsfile`,
`docker-compose.*.yml`, `nginx/`, `k8s/`) or from an observed end-to-end run. Nothing is
taken from the README's aspirational description.

Design-only. **No application code was changed to produce either deck.**
