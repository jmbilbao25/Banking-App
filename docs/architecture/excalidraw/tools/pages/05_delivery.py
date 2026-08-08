"""Page 5 -- how code reaches the cluster.

The argument is the red line. Everything above it pushes and holds no credential
to the cluster; everything below it pulls. That single boundary is what makes a
compromised pipeline unable to reach production.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("delivery")

s.header(
    60, 50,
    "Delivery \u2014 Supply Chain and GitOps",
    "GitHub Actions federated to Azure with OIDC \u00b7 signed images in ACR \u00b7 Argo CD pulls \u00b7 canary with automatic rollback",
    "PAGE 5 of 6  \u00b7  DELIVERY",
    "Process flow \u00b7 build and release",
    w=2000,
)

OPS = SEM["ops"][1]
PLAT = SEM["platform"][1]
RED = "#B91C1C"

# ============================================================ push
s.text("PUSH  \u00b7  continuous integration", 60, 168, 700, 15, color=INK)

s.zone(60, 230, 560, 200, "1   Review and pre-merge gates", "ops")
s.card(80, 266, 520, 64, "github", "Pull request", "ops",
       sub="two reviewers, CODEOWNERS, protected branch")
s.card(80, 340, 520, 64, "github", "Gates that block the merge", "ops",
       sub="secret scanning, CodeQL, SCA, tests, Terraform policy")

s.zone(680, 230, 620, 200, "2   Build, scan and sign", "ops")
s.card(700, 266, 580, 64, "docker", "Distroless image, non-root", "ops",
       sub="built by GitHub Actions over OIDC \u2014 no stored credential")
s.card(700, 340, 580, 64, "notary", "Scanned, then signed", "ops",
       sub="Trivy and Defender, then Notation with a key in Managed HSM")

s.zone(1360, 230, 700, 200, "3   Registry", "ops")
acr = s.card(1380, 266, 660, 64, "acr", "Azure Container Registry Premium",
             "ops", sub="quarantine until scanned, geo-replicated")
s.text("Images are addressed by digest, never by a mutable tag, so what was\nsigned and scanned is exactly what runs. An SBOM and SLSA level 3\nprovenance are attached to that digest.",
       1380, 348, 660, 12, color=BODY, align="left")

s.arrow([(624, 298), (676, 298)], color=OPS)
s.arrow([(1304, 298), (1356, 298)], color=OPS)

# ============================================================ the boundary
s.line([(60, 500), (2060, 500)], color=RED, sw=3, style="dashed")
s.text("Nothing above this line holds a credential to the cluster  \u00b7  the cluster pulls, CI never pushes to it",
       60, 512, 2000, 14, color=RED, align="center")

# ============================================================ pull
s.text("PULL  \u00b7  GitOps reconciliation", 60, 560, 700, 15, color=INK)

s.zone(60, 620, 560, 250, "4   Git is the only source of truth", "ops")
s.card(80, 656, 520, 64, "github", "Config repository", "ops",
       sub="one overlay per environment")
argo = s.card(80, 730, 520, 64, "argo", "Argo CD", "ops",
              sub="runs in the cluster, reconciles continuously")
s.text("Argo CD reaches out, so there is no inbound firewall rule and no\nservice principal in GitHub with rights to the cluster.",
       80, 810, 520, 12, color=BODY, align="left")

# environments as a timeline -- a different pattern from the cards above,
# because promotion is a sequence rather than a set of components
s.zone(680, 620, 620, 250, "5   Progressive delivery", "ops")
s.line([(710, 700), (1270, 700)], color=OPS, sw=2)
ENVS = [(760, "dev", "auto-sync"), (930, "sit", "integration + DAST"),
        (1100, "uat", "performance + VAPT"), (1250, "prod", "approval + CAB")]
for x, name, sub in ENVS:
    s.ellipse(x - 6, 694, 12, 12, "ops", fill=OPS, stroke=OPS, sw=1)
    s.text(name, x - 60, 666, 120, 14, color=INK, align="center")
    s.text(sub, x - 85, 714, 170, 11, color=BODY, align="center")
s.text("Every environment is its own subscription running the same policy set at\na smaller SKU. Promotion is a git commit, so each deploy has an author,\na diff, and a revert that takes one merge.",
       700, 780, 590, 12, color=BODY, align="left")

s.zone(1360, 620, 700, 250, "6   Canary with automatic rollback", "ops")
roll = s.card(1380, 656, 300, 64, "argo", "Argo Rollouts", "ops",
              sub="10 / 50 / 100 percent")
aks = s.card(1760, 656, 280, 64, "aks", "AKS", "platform",
             sub="signature checked at admission")
mon = s.card(1760, 750, 280, 64, "monitor", "Azure Monitor", "ops",
             sub="SLO error budget")
s.arrow([(1682, 688), (1756, 688)], src=roll, dst=aks, color=OPS)
s.arrow([(1900, 722), (1900, 746)], src=aks, dst=mon, color=OPS)
s.arrow([(1758, 782), (1530, 782), (1530, 724)], src=mon, dst=roll, color=RED,
        style="dashed", sharp=True)
s.text("SLO breach rolls it back", 1546, 756, 220, 11, color=RED, align="left")
s.text("The rollback is driven by the error budget, not by someone watching a dashboard.\nChaos Studio injects faults on a schedule, so that path is exercised, not assumed.",
       1380, 830, 660, 12, color=BODY, align="left")

# the one relationship that crosses the boundary, drawn in the pull direction
s.arrow([(604, 762), (640, 762), (640, 460), (1340, 460), (1340, 298),
         (1376, 298)], src=argo, dst=acr, color=OPS, style="dashed",
        sharp=True)
s.text("Argo CD pulls the signed digest", 700, 436, 340, 11, color=OPS,
       align="left")

# ============================================================ legend
s.legend_row(60, 930, ["ops", "platform"])
s.text("Source: docs/architecture/target-azure-architecture.md", 60, 972, 900,
       11, color="#94A3B8", align="left")

s.write("05-delivery.excalidraw")
