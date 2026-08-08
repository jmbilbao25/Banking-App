"""Page 1 -- capstone context.

The job of this page is to fix the scope boundary before anyone looks at Azure
detail. EastWest bought Temenos SaaS for core banking, so the honest scope for a
trainee project is the channel layer in front of it -- not a replacement core.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("context")

s.header(
    60, 50,
    "EastWest Digital Channels \u2014 Capstone Context",
    "Core banking is Temenos SaaS, so our scope is the channel layer in front of it. This page fixes that boundary before any Azure detail.",
    "PAGE 1 of 4  \u00b7  CONTEXT",
    "Context diagram",
    w=1600,
)

PLAT = SEM["platform"][1]
SECU = SEM["security"][1]
EXT = SEM["external"][1]

# ---------------------------------------------------------------- customers
retail = s.icon("browser", 160, 320, 40)
s.text("Retail customer\nEasyWay web and app", 80, 370, 200, 13, color=SUBTLE,
       align="center")
biz = s.icon("devices", 160, 500, 40)
s.text("Business customer\nEasyBiz app", 80, 550, 200, 13, color=SUBTLE,
       align="center")

# ---------------------------------------------------------------- our scope
s.zone(420, 260, 600, 400, "IN SCOPE \u2014 the channel layer we designed",
       "plain", sw=3, label_size=16)
s.card(440, 310, 560, 66, None, "EasyWay web and mobile API", "platform",
       sub="sign-in, account view, transfers")
s.card(440, 390, 560, 66, None, "Transfer service", "platform",
       sub="checks a request, then calls the core")
s.card(440, 470, 560, 66, "botservice", "ESTA chatbot", "platform",
       sub="existing bot \u2014 we add a transfer-status reply")
s.card(440, 550, 560, 66, "externalid", "Customer sign-in", "security",
       sub="Entra External ID, MFA, trusted device")

s.arrow([(204, 340), (416, 340)], src=retail, color=SUBTLE)
s.arrow([(204, 520), (416, 520)], src=biz, color=SUBTLE)

# ---------------------------------------------------------------- out of scope
s.text("OUT OF SCOPE \u2014 we integrate with these, we do not build them",
       1110, 266, 560, 13, color=BODY)
DEPS = [
    ("Temenos SaaS core banking", "accounts, balances and postings \u2014 the system of record", "accounts"),
    ("InstaPay and PESONet", "the BSP-regulated transfer rails", "transfers"),
    ("Infobip and MoEngage", "SMS, push and e-mail delivery", "notify"),
]
for i, (title, sub, label) in enumerate(DEPS):
    y = 320 + i * 100
    cy = y + 33
    c = s.card(1110, y, 540, 66, None, title, "external", sub=sub)
    s.arrow([(1024, cy), (1106, cy)], dst=c, color=EXT)
    s.text(label, 1028, cy - 20, 80, 11, color=EXT, align="left")

# ---------------------------------------------------------------- why
s.text("Why we drew the boundary here", 60, 700, 700, 14, color=INK)
s.text("EastWest selected Temenos SaaS for core banking in 2025. Their Head of Enterprise\nArchitecture describes the approach as \u201cback-to-core\u201d: keep the core standard and put\nchanges into configuration rather than custom code, so the core stays evergreen.\n\nWe followed that. Our design adds no logic to the core. The transfer service asks the\ncore to move money and treats the answer as final.",
       60, 726, 1000, 13, color=BODY, align="left")

s.text("Also unchanged by this project", 1110, 700, 560, 14, color=INK)
s.text("EastWest stores and ATMs serve the same\ncustomers and are untouched here.\n\nKomo, the digital-only bank, runs on its own\napp and is a separate piece of work.",
       1110, 726, 560, 13, color=BODY, align="left")

# ---------------------------------------------------------------- legend
s.legend_row(60, 880, ["platform", "security", "external"], services=True)
s.text("Sources: EastWest EasyWay FAQ and komo.ph \u00b7 Temenos press release, 22 May 2025 \u00b7 Temenos Regional Forum, Manila",
       60, 922, 1300, 11, color="#94A3B8", align="left")

s.write("01-context.excalidraw")
