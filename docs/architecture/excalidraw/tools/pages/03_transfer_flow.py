"""Page 3 -- one InstaPay transfer, end to end.

Seven steps. The page exists for step 5: the moment our service stops deciding
anything and the core decides. Steps 1-4 and 7 are ours; 5 and 6 are not.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("transfer-flow")

s.header(
    60, 50,
    "How an InstaPay Transfer Works",
    "Seven steps. The one that matters is step 5, where our service stops deciding and the core decides.",
    "PAGE 3 of 4  \u00b7  TRANSFER FLOW",
    "Activity flow \u00b7 one use case",
    w=1700,
)

EDGE = SEM["edge"][1]
PLAT = SEM["platform"][1]
EXT = SEM["external"][1]


def step(n, x, y, w, h, icon, title, sub, sem, *, sw=2):
    c = s.card(x, y, w, h, icon, title, sem, sub=sub, sw=sw)
    stroke = SEM[sem][1]
    s.ellipse(x - 14, y - 14, 28, 28, sem, fill="#FFFFFF", stroke=stroke, sw=2)
    s.text(str(n), x - 14, y - 9, 28, 14, color=stroke, align="center",
           role="badge")
    return c


# ---------------------------------------------------------------- ours
s.text("The request comes in", 60, 186, 700, 14, color=INK)
a1 = step(1, 60, 220, 380, 110, "browser", "Customer starts a transfer",
          "picks the account, the amount\nand the recipient bank", "external")
a2 = step(2, 480, 220, 380, 110, "frontdoor", "Front Door and WAF",
          "TLS and WAF rules checked\nbefore anything else", "edge")
a3 = step(3, 900, 220, 380, 110, "apim", "API Management",
          "validates the access token,\napplies a rate limit", "platform")
a4 = step(4, 1320, 220, 380, 110, None, "Transfer service checks it",
          "format, daily limit,\ntrusted device", "platform")

s.arrow([(444, 275), (476, 275)], src=a1, dst=a2, color=SUBTLE)
s.arrow([(864, 275), (896, 275)], src=a2, dst=a3, color=EDGE)
s.arrow([(1284, 275), (1316, 275)], src=a3, dst=a4, color=PLAT)

# ---------------------------------------------------------------- the core, then back
s.text("The core and the rails \u2014 not ours", 60, 386, 700, 14, color=INK)
b5 = step(5, 60, 420, 515, 110, None, "Temenos posts the transfer",
          "debits the account and returns a\nreference. This answer is final.",
          "external", sw=3)
b6 = step(6, 622, 420, 515, 110, None, "The rails carry it out",
          "InstaPay, through the bank's\nexisting payment gateway", "external")
b7 = step(7, 1184, 420, 515, 110, None, "We record it and notify",
          "write our own copy, queue an SMS\nand a push through Infobip", "platform")

s.arrow([(579, 475), (618, 475)], src=b5, dst=b6, color=EXT)
s.arrow([(1141, 475), (1180, 475)], src=b6, dst=b7, color=EXT)

s.arrow([(1510, 332), (1510, 375), (317, 375), (317, 416)], src=a4, dst=b5,
        color=PLAT, sharp=True)
s.text("all checks passed", 700, 352, 240, 11, color=PLAT, align="left")

# ---------------------------------------------------------------- the point
s.text("Where the boundary sits", 60, 590, 700, 14, color=INK)
s.text("Steps 1 to 4 and step 7 are ours. Step 5 is Temenos and step 6 is the rails.\n\nOur service never moves money itself. It asks the core to, and records what the core\nanswers. If the core rejects the request we show the customer the reason and write\nnothing of our own.",
       60, 618, 1000, 13, color=BODY, align="left")

s.text("What we did not build", 1120, 590, 580, 14, color=INK)
s.text("No ledger and no settlement logic of our own.\nTemenos already does that, and rebuilding it\nwould be exactly the kind of customisation the\nbank is trying to move away from.\n\nThe thick border on step 5 marks the handover.",
       1120, 618, 580, 13, color=BODY, align="left")

s.legend_row(60, 780, ["edge", "platform", "external"])
s.text("Source: EastWest EasyWay FAQ \u00b7 transfer features listed there include InstaPay and PESONet",
       60, 822, 1300, 11, color="#94A3B8", align="left")

s.write("03-transfer-flow.excalidraw")
