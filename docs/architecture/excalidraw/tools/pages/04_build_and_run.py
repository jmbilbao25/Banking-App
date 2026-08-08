"""Page 4 -- how we build and run it.

Deliberately small. The right-hand column lists what we left out and why, which
is the honest half of a student design: we can only claim to have designed what
we could also operate.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("build-and-run")

s.header(
    60, 50,
    "How We Build and Run It",
    "A small pipeline we can actually operate: three environments, one registry, and alerts that reach a person.",
    "PAGE 4 of 4  \u00b7  BUILD AND RUN",
    "Process flow",
    w=1600,
)

OPS = SEM["ops"][1]
PLAT = SEM["platform"][1]

# ---------------------------------------------------------------- pipeline
s.zone(60, 220, 1000, 110, "Pipeline", "ops")
p1 = s.card(80, 245, 300, 60, "github", "GitHub", "ops",
            sub="pull request, one reviewer")
p2 = s.card(410, 245, 300, 60, "docker", "Build and test", "ops",
            sub="unit tests, then image build")
p3 = s.card(740, 245, 300, 60, "acr", "Container Registry", "ops",
            sub="stores the built image")
s.arrow([(384, 275), (406, 275)], src=p1, dst=p2, color=OPS)
s.arrow([(714, 275), (736, 275)], src=p2, dst=p3, color=OPS)

# ---------------------------------------------------------------- environments
s.zone(60, 420, 1000, 150, "Environments", "ops")
e1 = s.card(80, 450, 300, 60, None, "dev", "ops", sub="deploys automatically")
e2 = s.card(410, 450, 300, 60, None, "UAT", "ops", sub="business sign-off")
e3 = s.card(740, 450, 300, 60, None, "production", "ops",
            sub="manual approval first")
s.arrow([(384, 480), (406, 480)], src=e1, dst=e2, color=OPS)
s.arrow([(714, 480), (736, 480)], src=e2, dst=e3, color=OPS)
s.text("The same templates deploy all three. Dev and UAT run smaller sizes to keep the cost down.",
       80, 530, 980, 12, color=BODY, align="left")

# ---------------------------------------------------------------- running it
s.zone(60, 660, 1000, 150, "Running it", "ops")
r1 = s.card(80, 690, 300, 60, "aks", "AKS", "platform",
            sub="rolling deployment")
r2 = s.card(410, 690, 300, 60, "monitor", "Azure Monitor", "ops",
            sub="alerts the team")
r3 = s.card(740, 690, 300, 60, "loganalytics", "Log Analytics", "ops",
            sub="one place for logs")
s.arrow([(384, 720), (406, 720)], src=r1, dst=r2, color=PLAT)
s.arrow([(714, 720), (736, 720)], src=r2, dst=r3, color=OPS)
s.text("A failed health check stops the rollout before it reaches every customer.",
       80, 770, 980, 12, color=BODY, align="left")

s.arrow([(890, 309), (890, 360), (230, 360), (230, 446)], src=p3, dst=e1,
        color=OPS, style="dashed", sharp=True)
s.text("the same image is promoted, never rebuilt", 420, 336, 460, 11,
       color=OPS, align="left")

# ---------------------------------------------------------------- honesty
s.zone(1120, 220, 480, 350, "What we left out, on purpose", "plain",
       label_size=15)
s.text("No custom logic in the core. Configuration\nonly, following the bank's own back-to-core\napproach.\n\nNo second cloud. One provider and one region\nis already enough to learn properly.\n\nNo service mesh, no confidential computing,\nno image-signing pipeline. We could not have\noperated those, so we did not draw them.\n\nNo active-active across regions. If Southeast\nAsia is down, we are down. We would rather\nsay that than draw a second region we never\nsized or costed.\n\nThese are things we would read about next,\nnot things we are claiming to have built.",
       1140, 258, 450, 13, color=BODY, align="left")

s.zone(1120, 660, 480, 150, "If we had more time", "plain", label_size=15)
s.text("Add a second region for disaster recovery.\n\nAdd dependency and image scanning to the\nbuild, and a load test before UAT sign-off.",
       1140, 698, 450, 13, color=BODY, align="left")

s.legend_row(60, 870, ["platform", "ops"], services=True)
s.text("Assumption: the bank's existing pipeline and hub network would be reused. We designed only the part inside our scope.",
       60, 912, 1400, 11, color="#94A3B8", align="left")

s.write("04-build-and-run.excalidraw")
