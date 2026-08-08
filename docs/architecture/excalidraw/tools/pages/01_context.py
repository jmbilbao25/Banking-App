"""Page 1 -- system context.

The platform is one black box. Only the actors and the external systems it
depends on appear; internal structure is deliberately omitted so the reader
settles the scope boundary before any implementation detail. Everything that
follows is a progressively narrower view of the box drawn here.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("context")

s.header(
    60, 50,
    "QR Payment Platform \u2014 System Context",
    "Who uses the platform and what it depends on. One box, no internals \u2014 the scope boundary comes first.",
    "PAGE 1 of 6  \u00b7  CONTEXT",
    "Context diagram",
    w=1500,
)

SECU = SEM["security"][1]
EXT = SEM["external"][1]

# ---------------------------------------------------------------- actors
cust = s.icon("browser", 150, 300, 44)
s.text("Customer\nmobile and web", 80, 352, 180, 13, color=SUBTLE,
       align="center")
merch = s.icon("devices", 150, 470, 44)
s.text("Merchant\nPOS and storefront", 80, 522, 180, 13, color=SUBTLE,
       align="center")

# ---------------------------------------------------------------- the system
s.zone(400, 250, 600, 392, "QR Payment Platform", "plain", sw=3,
       label_size=18)

s.text("Accepts QR Ph payments, moves money between customer\nand merchant accounts, and settles to the merchant bank.",
       430, 300, 540, 15, color=INK, align="left")

s.line([(430, 360), (970, 360)], color="#CBD5E1", sw=1)

s.text("Runs on Azure in Southeast Asia (Singapore), with a warm\nstandby in East Asia (Hong Kong).",
       430, 382, 540, 13, color=BODY, align="left")
s.text("Two trust zones sit inside this boundary: the banking domain\nowns the ledger, the commerce domain owns orders and stock.",
       430, 440, 540, 13, color=BODY, align="left")
s.text("Internal structure is deliberately left out here. Pages 2 to 6\nopen the box one layer at a time.",
       430, 500, 540, 13, color=BODY, align="left")

# ---------------------------------------------------------------- dependencies
DEPS = [
    ("externalid", "Microsoft Entra External ID",
     "customer identity, MFA, passkeys", "security", "authenticates", "dashed"),
    (None, "QR Ph switch",
     "BSP-mandated national QR standard", "external", "QR standard", "solid"),
    (None, "InstaPay and PESONet",
     "interbank settlement rails", "external", "settles funds", "solid"),
    (None, "AMLC reporting",
     "CTR and STR submissions", "external", "reports", "dashed"),
    (None, "Core banking system",
     "on-premises system of record", "external", "ExpressRoute", "solid"),
]

for i, (ik, title, sub, sem, label, style) in enumerate(DEPS):
    y = 250 + i * 82
    cy = y + 32
    card = s.card(1140, y, 420, 64, ik, title, sem, sub=sub)
    colour = SECU if sem == "security" else EXT
    s.arrow([(1004, cy), (1136, cy)], dst=card, color=colour, style=style)
    s.text(label, 1010, cy - 22, 130, 11, color=colour, align="left")

# ---------------------------------------------------------------- actor flows
s.arrow([(198, 322), (396, 322)], src=cust, color=SUBTLE)
s.text("scans a QR code and pays", 210, 296, 190, 11, color=SUBTLE,
       align="left")
s.arrow([(198, 492), (396, 492)], src=merch, color=SUBTLE)
s.text("displays a QR code", 210, 466, 190, 11, color=SUBTLE, align="left")

# ---------------------------------------------------------------- legend
s.legend_row(60, 700, ["security", "external"])
s.text("Source: docs/architecture/target-azure-architecture.md", 60, 742, 900,
       11, color="#94A3B8", align="left")

s.write("01-context.excalidraw")
