"""Page 4 -- how one QR payment actually executes.

Visual argument: the amount is resolved server-side, and the money move plus the
event that announces it are written in ONE transaction. The numbered steps carry
the sequence, so the only arrows drawn are the ones that change the story:
into the ACID region, and out of it via the outbox.
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
    "The client never states a price, and the ledger posting plus its outbox event commit together \u00b7 fixes F-01, F-02, F-03, F-04, F-05, F-06",
    "PAGE 4 of 6  \u00b7  RUNTIME FLOW",
    w=2000,
)

COLS = [60, 470, 880, 1290]
CW = 370


def step(n, col, y, icon, title, sub, sem, *, h=110):
    x = COLS[col]
    c = s.card(x, y, CW, h, icon, title, sem, sub=sub)
    stroke = SEM[sem][1]
    s.ellipse(x - 13, y - 13, 26, 26, sem, fill="#FFFFFF", stroke=stroke, sw=2)
    s.text(str(n), x - 13, y - 13 + 5, 26, 13, color=stroke, align="center",
           role="badge")
    return c


# ------------------------------------------------------------ row A
s.text("Admission  \u00b7  steps 1 to 4", 60, 180, 700, 14, color=INK)
a1 = step(1, 0, 210, "browser", "Customer scans QR Ph", "POST /payments\nIdempotency-Key header", "edge")
a2 = step(2, 1, 210, "frontdoor", "Front Door + WAF", "TLS 1.3 \u00b7 OWASP CRS 3.2\nbot and geo rules", "edge")
a3 = step(3, 2, 210, "apim", "APIM validates the token", "validate-jwt against Entra\nrate-limit-by-key", "net")
a4 = step(4, 3, 210, "redis", "Idempotency claim", "SETNX idempotency:{key}\na replay returns the first result", "data")

E = SEM["edge"][1]
N = SEM["net"][1]
D = SEM["data"][1]
C = SEM["compute"][1]
S = SEM["sec"][1]
O = SEM["ops"][1]

s.arrow([(432, 265), (468, 265)], src=a1, dst=a2, color=E)
s.arrow([(842, 265), (878, 265)], src=a2, dst=a3, color=E)
s.arrow([(1252, 265), (1288, 265)], src=a3, dst=a4, color=N)

# ------------------------------------------------------------ row B
s.text("Server-side validation  \u00b7  steps 5 to 8", 60, 360, 700, 14, color=INK)
b5 = step(5, 0, 390, "hsm", "qrph-service verifies JWS", "detached signature \u00b7 CRC16\nMHSM public key \u00b7 expiry", "sec")
b6 = step(6, 1, 390, "python", "order-service", "returns the AUTHORITATIVE amount\nthe client never supplies one", "compute")
b7 = step(7, 2, 390, "python", "fraud-service", "velocity \u00b7 device \u00b7 ML score\nHIGH means step-up auth", "compute")
b8 = step(8, 3, 390, "python", "aml-service", "sanctions and PEP screening\nCTR queued above PHP 500k", "compute")

s.arrow([(432, 445), (468, 445)], src=b5, dst=b6, color=S)
s.arrow([(842, 445), (878, 445)], src=b6, dst=b7, color=C)
s.arrow([(1252, 445), (1288, 445)], src=b7, dst=b8, color=C)

# ------------------------------------------------------------ row C: the hero
s.zone(60, 570, 1600, 200,
       "9   One local ACID transaction  \u2014  the only place money moves",
       "data", sw=3, label_size=15)
led = s.card(80, 612, 330, 52, "python", "ledger-service", "data",
             sub="double-entry, append-only")
pg = s.card(430, 612, 330, 52, "postgres", "PostgreSQL", "data",
            sub="SELECT ... FOR UPDATE on payer")
s.arrow([(412, 638), (428, 638)], src=led, dst=pg, color=D)

s.code(790, 596, 850, [
    ("BEGIN;", CODE_FG),
    ("  SELECT balance FROM account WHERE id = $1 FOR UPDATE;", CODE_ACCENT),
    ("  INSERT INTO journal (txn, account, dr, cr) VALUES (...);   -- payer debit", CODE_FG),
    ("  INSERT INTO journal (txn, account, dr, cr) VALUES (...);   -- merchant credit", CODE_FG),
    ("  INSERT INTO outbox (topic, payload) VALUES ('PaymentCompleted', ...);", CODE_ACCENT),
    ("COMMIT;", CODE_FG),
], title="one BEGIN ... COMMIT \u2014 the posting and the event that announces it")

s.text("If this transaction fails, no outbox row exists, so no event is ever published and the\norder stays PENDING with no money moved. A half-finished payment is impossible by\nconstruction rather than by retry logic.",
       80, 684, 700, 11, color=BODY, align="left")

s.arrow([(1475, 502), (1475, 540), (860, 540), (860, 568)], src=b8, color=C)
s.text("all checks passed", 880, 516, 220, 11, color=C, align="left")

# ------------------------------------------------------------ row D
s.text("Asynchronous consumers  \u00b7  steps 10 to 13", 60, 800, 700, 14, color=INK)
d10 = step(10, 0, 830, "servicebus", "Outbox relay publishes", "PaymentCompleted\nat-least-once to Service Bus", "data")
d11 = step(11, 1, 830, "python", "order-service marks PAID", "idempotent consumer\nno public callback exists", "compute")
d12 = step(12, 2, 830, "ledger", "audit-service", "hash-chained event\nanchored in Confidential Ledger", "compute")
d13 = step(13, 3, 830, "python", "notification-service", "push receipt and SMS\nDLQ after repeated failure", "compute")

s.arrow([(400, 772), (400, 828)], dst=d10, color=D)
s.text("outbox relay", 410, 786, 160, 11, color=D, align="left")

s.arrow([(432, 885), (468, 885)], src=d10, dst=d11, color=D)
s.arrow([(842, 885), (878, 885)], src=d11, dst=d12, color=C)
s.arrow([(1252, 885), (1288, 885)], src=d12, dst=d13, color=C)

s.text("The orchestrator returns 201 Created with the receipt as soon as the ledger commits. Steps 10 to 13 run asynchronously, so a slow\nconsumer delays a notification but can never delay, duplicate or lose the debit.",
       60, 962, 1600, 12, color=SUBTLE, align="left")

# ------------------------------------------------------------ evidence column
s.zone(1700, 210, 360, 700, "What actually moves on the wire", "plain",
       label_size=14)

s.code(1715, 258, 330, [
    ("Authorization: Bearer <jwt>", CODE_FG),
    ("Idempotency-Key: 3f9a1c-...-c1", CODE_ACCENT),
    ("{", CODE_FG),
    ("  \"qrPayload\": \"00020101...A1B2\",", CODE_FG),
    ("  \"orderRef\": \"ORD-88213\"", CODE_ACCENT),
    ("}", CODE_FG),
    ("# there is no amount field", CODE_DIM),
], title="POST /payments")

s.text("The client cannot state a price, and it\ncannot name the merchant. That single\nomission removes F-02 and F-03 together.",
       1715, 410, 340, 11, color=BODY, align="left")

s.code(1715, 462, 330, [
    ("00 02 01        version", CODE_FG),
    ("01 02 12        dynamic QR", CODE_FG),
    ("26 .. ..        merchant account", CODE_ACCENT),
    ("54 06 150.00    amount", CODE_ACCENT),
    ("63 04 A1B2      CRC16", CODE_FG),
], title="QR Ph payload \u00b7 EMVCo TLV")

s.text("A real QR Ph payload, not a URL with an\namount in the query string. It carries a\ndetached JWS signed by a non-exportable\nP-256 key in Managed HSM.",
       1715, 588, 340, 11, color=BODY, align="left")

s.code(1715, 656, 330, [
    ("txn  account   dr        cr", CODE_DIM),
    ("T91  alice     150.0000  -", CODE_ACCENT),
    ("T91  merchant  -         150.0000", CODE_ACCENT),
    ("CHECK SUM(dr) - SUM(cr) = 0", CODE_FG),
], title="journal rows \u00b7 NUMERIC(19,4)")

s.text("Balances are derived from these rows, never\nmutated in place, so the double-spend race\nand the floating-point drift both disappear.",
       1715, 782, 340, 11, color=BODY, align="left")

s.write("04-payment-flow.excalidraw")
