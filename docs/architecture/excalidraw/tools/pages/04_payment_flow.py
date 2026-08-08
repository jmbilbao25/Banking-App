"""Page 4 -- how one QR payment executes.

Nine numbered steps. The numbers carry the order, so the only arrows drawn are
the ones that change the story: into the single ACID transaction, and out of it
to the consumers. The hero is step 8, because that is the only place money moves
and the only place the outbox event is created.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import (Scene, SEM, BODY, SUBTLE, INK, CODE_FG, CODE_ACCENT,
                   CODE_DIM)

s = Scene("payment-flow")

s.header(
    60, 50,
    "Payment Runtime \u2014 One QR Ph Transaction",
    "The amount is resolved server-side, and the ledger posting commits together with the event that announces it.",
    "PAGE 4 of 6  \u00b7  PAYMENT FLOW",
    "Activity flow \u00b7 single use case",
    w=2000,
)

EDGE = SEM["edge"][1]
PLAT = SEM["platform"][1]
DATA = SEM["data"][1]
SECU = SEM["security"][1]


def step(n, x, y, w, h, icon, title, sub, sem):
    c = s.card(x, y, w, h, icon, title, sem, sub=sub)
    stroke = SEM[sem][1]
    s.ellipse(x - 14, y - 14, 28, 28, sem, fill="#FFFFFF", stroke=stroke, sw=2)
    s.text(str(n), x - 14, y - 14 + 5, 28, 14, color=stroke, align="center",
           role="badge")
    return c


# ------------------------------------------------------------ admission
s.text("Admission", 60, 176, 700, 14, color=INK)
a1 = step(1, 60, 210, 460, 100, "browser", "Customer scans the QR code",
          "POST /payments carrying an\nIdempotency-Key header", "external")
a2 = step(2, 560, 210, 460, 100, "frontdoor", "Front Door and WAF",
          "TLS 1.3, OWASP CRS 3.2,\nbot and geo filtering", "edge")
a3 = step(3, 1060, 210, 460, 100, "apim", "API Management checks the token",
          "validate-jwt against Entra,\nrate-limit-by-key", "platform")
a4 = step(4, 1560, 210, 460, 100, None, "payment-orchestrator claims the key",
          "SETNX in Redis \u2014 a replay returns\nthe first result, never a second debit",
          "platform")

s.arrow([(524, 260), (556, 260)], src=a1, dst=a2, color=SUBTLE)
s.arrow([(1024, 260), (1056, 260)], src=a2, dst=a3, color=EDGE)
s.arrow([(1524, 260), (1556, 260)], src=a3, dst=a4, color=PLAT)

# ------------------------------------------------------------ validation
s.text("Server-side validation", 60, 356, 700, 14, color=INK)
b5 = step(5, 60, 390, 620, 100, None, "qrph-service verifies the signature",
          "detached JWS, CRC16, expiry\npublic key held in Managed HSM", "security")
b6 = step(6, 730, 390, 620, 100, None, "order-service resolves the amount",
          "the authoritative order total \u2014 the client\nnever supplies a figure to trust", "platform")
b7 = step(7, 1400, 390, 620, 100, None, "fraud and aml services screen",
          "velocity and device scoring, then\nsanctions and PEP checks", "platform")

s.arrow([(684, 440), (726, 440)], src=b5, dst=b6, color=SECU)
s.arrow([(1354, 440), (1396, 440)], src=b6, dst=b7, color=PLAT)

# ------------------------------------------------------------ the hero
s.zone(60, 570, 1960, 190, "8   One local ACID transaction", "data", sw=3,
       label_size=16)
# amber, matching page 3: what defines this service is that it runs on the
# confidential node pool, not that it holds state -- PostgreSQL does that
led = s.card(80, 612, 380, 64, None, "ledger-service", "security",
             sub="double-entry, append-only \u00b7 confidential pool")
pg = s.card(490, 612, 380, 64, "postgres", "PostgreSQL", "data",
            sub="row lock on the payer account")
s.arrow([(464, 644), (486, 644)], src=led, dst=pg, color=DATA)

s.code(910, 596, 1090, [
    ("BEGIN;", CODE_FG),
    ("  SELECT balance FROM account WHERE id = $1 FOR UPDATE;", CODE_ACCENT),
    ("  INSERT INTO journal (...);   -- payer debit, then merchant credit", CODE_FG),
    ("  INSERT INTO outbox (topic, payload) VALUES ('PaymentCompleted', ...);", CODE_ACCENT),
    ("COMMIT;", CODE_FG),
], title="one BEGIN ... COMMIT \u2014 the posting and the event that announces it")

s.text("This is the only place money moves. If the transaction fails there is no outbox row, so no\nevent is ever published and the order stays PENDING with nothing debited. A half-finished\npayment is impossible by construction rather than by retry logic.",
       80, 688, 800, 12, color=BODY, align="left")

s.arrow([(1500, 492), (1500, 530), (420, 530), (420, 608)], src=b7, dst=led,
        color=PLAT, sharp=True)
s.text("all checks passed", 700, 504, 260, 11, color=PLAT, align="left")

# ------------------------------------------------------------ consumers
s.text("Asynchronous consumers", 60, 846, 700, 14, color=INK)
d9 = step(9, 60, 880, 460, 84, "servicebus", "Service Bus Premium",
          "outbox relay publishes PaymentCompleted", "data")

CONS = [
    ("order-service marks the order PAID", "idempotent consumer, no public callback"),
    ("audit-service appends the receipt", "hash-chained, anchored in Confidential Ledger"),
    ("notification-service", "push receipt and SMS, DLQ after repeated failure"),
]
LANES = [(895, 588), (922, 600), (949, 612)]
for i, (title, sub) in enumerate(CONS):
    y = 840 + i * 78
    cy = y + 32
    c = s.card(660, y, 620, 64, None, title, "platform", sub=sub)
    exit_y, lane_x = LANES[i]
    s.arrow([(524, exit_y), (lane_x, exit_y), (lane_x, cy), (656, cy)],
            src=d9, dst=c, color=DATA, style="dashed", sharp=True)

s.arrow([(400, 762), (400, 876)], dst=d9, color=DATA)
s.text("outbox relay", 410, 800, 180, 11, color=DATA, align="left")

s.text("The orchestrator returns 201 Created with the receipt as soon as the ledger commits.\nThese three consumers run afterwards, so a slow consumer delays a notification but can\nnever delay, duplicate or lose the debit itself.",
       1340, 848, 680, 12, color=BODY, align="left")

# ------------------------------------------------------------ legend
s.legend_row(60, 1100, ["edge", "platform", "data", "security", "external"])
s.text("Source: docs/architecture/target-azure-architecture.md", 60, 1142, 900,
       11, color="#94A3B8", align="left")

s.write("04-payment-flow.excalidraw")
