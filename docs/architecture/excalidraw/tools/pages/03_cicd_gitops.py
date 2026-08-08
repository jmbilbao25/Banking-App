"""Page 3 -- CI/CD and the GitOps supply chain.

Visual argument: the red line. Everything above it PUSHES and holds no cluster
credential; everything below it PULLS. That single boundary is what removes the
"Jenkins holds prod SSH keys and DB passwords" failure mode (F-09).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import (Scene, SEM, BODY, SUBTLE, INK, CODE_FG, CODE_ACCENT,
                   CODE_DIM)

s = Scene("cicd-gitops")

s.header(
    60, 50,
    "Supply Chain \u2014 CI/CD and GitOps Delivery",
    "GitHub Actions federated to Azure with OIDC \u00b7 signed images in ACR \u00b7 Argo CD pulls \u00b7 canary with automatic rollback",
    "PAGE 3 of 6  \u00b7  CI/CD & GITOPS",
    w=2000,
)

# =========================================================== PUSH side
s.text("PUSH  \u00b7  continuous integration", 60, 164, 700, 14, color=INK)

s.zone(60, 220, 400, 230, "1   Author & review", "ext")
s.card(78, 256, 364, 52, "github", "Pull request", "ext",
       sub="2 reviewers \u00b7 CODEOWNERS \u00b7 protected branch")
s.card(78, 318, 364, 52, "terraform", "Terraform plan", "ext",
       sub="OPA / Conftest policy-as-code")
s.text("Infrastructure and application land through the\nsame review gate. No console changes in any\nenvironment above dev.",
       78, 382, 370, 11, color=BODY, align="left")

s.zone(500, 220, 520, 230, "2   Pre-merge gates  \u00b7  fail closed", "sec")
gates = [
    ("github", "Secret scanning", "push protection"),
    ("github", "CodeQL SAST", "fail on high"),
    ("trivy", "Dependabot + SCA", "CVE and licence"),
    ("python", "Unit + contract tests", "coverage gate"),
]
for i, (ik, t, sub) in enumerate(gates):
    s.card(518 + (i % 2) * 260, 256 + (i // 2) * 62, 235, 52, ik, t, "sec",
           sub=sub)
s.text("A failing gate blocks the merge; it does not warn.\nPush protection is what stops F-09 recurring.",
       518, 382, 484, 11, color=BODY, align="left")

s.zone(1060, 220, 560, 230, "3   Build, scan & sign", "ops")
build = [
    ("github", "Actions + OIDC", "federated, no stored creds"),
    ("docker", "Distroless build", "non-root, read-only rootfs"),
    ("trivy", "Trivy + Defender", "fail on HIGH / CRITICAL"),
    ("notary", "Notation signing", "key in Managed HSM"),
]
for i, (ik, t, sub) in enumerate(build):
    s.card(1078 + (i % 2) * 272, 256 + (i // 2) * 62, 255, 52, ik, t, "ops",
           sub=sub)
s.text("An SBOM (CycloneDX) and SLSA level 3 provenance are\nattached to the image digest, not to a tag.",
       1078, 382, 524, 11, color=BODY, align="left")

s.zone(1660, 220, 380, 230, "4   Registry", "ops")
s.card(1678, 256, 344, 52, "acr", "ACR Premium", "ops",
       sub="quarantine until scanned")
s.text("Geo-replicated Southeast Asia + East Asia.\n\nImages are addressed by digest, never by a\nmutable tag, so 'latest' cannot drift into\nproduction the way Docker Hub did.\n\nUntagged manifests are purged after 30 days.",
       1678, 322, 350, 11, color=BODY, align="left")

E = SEM["ext"][1]
S = SEM["sec"][1]
O = SEM["ops"][1]
C = SEM["compute"][1]

s.arrow([(462, 282), (498, 282)], color=E)
s.arrow([(1022, 282), (1058, 282)], color=S)
s.arrow([(1622, 282), (1658, 282)], color=O)

# =========================================================== the boundary
s.line([(60, 530), (2060, 530)], color="#DC2626", sw=3, style="dashed")
s.text("Nothing above this line holds a credential to the cluster  \u00b7  the cluster pulls, CI never pushes to it",
       60, 542, 2000, 13, color="#B91C1C", align="center")

# =========================================================== PULL side
s.text("PULL  \u00b7  GitOps reconciliation", 60, 576, 700, 14, color=INK)

s.zone(60, 640, 420, 270, "5   Git is the only source of truth", "ext")
s.card(78, 676, 384, 52, "github", "Config repo", "ext",
       sub="kustomize overlay per environment")
s.card(78, 738, 384, 52, "argo", "Argo CD", "ext",
       sub="reconciles every 3 minutes")
s.text("Argo CD runs inside the cluster and reaches out.\nThere is no inbound firewall rule and no service\nprincipal in GitHub with cluster rights, so a\ncompromised pipeline cannot reach production.",
       78, 802, 390, 11, color=BODY, align="left")

s.zone(520, 640, 700, 270, "6   Progressive delivery", "compute")
s.line([(540, 730), (1200, 730)], color=C, sw=2)
envs = [
    (580, "dev", "auto-sync"),
    (770, "sit", "integration + DAST"),
    (960, "uat", "perf + VAPT"),
    (1150, "prod", "approval + CAB"),
]
for x, name, sub in envs:
    s.ellipse(x - 6, 724, 12, 12, "compute", fill=C, stroke=C, sw=1)
    s.text(name, x - 60, 698, 120, 13, color=INK, align="center")
    s.text(sub, x - 70, 744, 140, 11, color=BODY, align="center")
s.text("Every environment is a separate subscription running the same policy\nset at a smaller SKU, so a change is proven against real controls before\nit reaches prod.\n\nPromotion is a git commit, so every deploy has an author, a diff and a\nrevert that takes one merge.",
       538, 790, 668, 11, color=BODY, align="left")

s.zone(1260, 640, 780, 270, "7   Canary with automatic rollback", "ops")
roll = s.card(1278, 676, 350, 52, "argo", "Argo Rollouts", "ops",
              sub="10 / 50 / 100 percent")
aks = s.card(1690, 676, 330, 52, "aks", "AKS", "ops",
             sub="Ratify + Gatekeeper verify")
mon = s.card(1690, 776, 330, 52, "monitor", "Azure Monitor SLO", "ops",
             sub="error budget burn rate")
chaos = s.card(1278, 776, 330, 52, "chaos", "Chaos Studio", "ops",
               sub="scheduled fault injection")
s.arrow([(1630, 702), (1688, 702)], src=roll, dst=aks, color=O)
s.arrow([(1855, 730), (1855, 774)], src=aks, dst=mon, color=O)
s.arrow([(1688, 802), (1618, 802), (1618, 730)], src=mon, dst=roll,
        color="#DC2626", style="dashed")
s.text("SLO breach = rollback", 1395, 748, 215, 11, color="#B91C1C",
       align="left")
s.arrow([(1610, 790), (1660, 790), (1660, 712), (1686, 712)],
        src=chaos, dst=aks, color=O, style="dashed")
s.text("The rollback is driven by the error budget, not by a human watching a dashboard.\nChaos Studio proves that claim on a schedule instead of assuming it.",
       1278, 848, 750, 11, color=BODY, align="left")

# =========================================================== evidence
s.code(60, 990, 640, [
    ("permissions:", CODE_FG),
    ("  id-token: write", CODE_ACCENT),
    ("  contents: read", CODE_FG),
    ("- uses: azure/login@v2", CODE_FG),
    ("  with:", CODE_FG),
    ("    client-id: ${{ vars.AZURE_CLIENT_ID }}", CODE_ACCENT),
    ("    tenant-id: ${{ vars.AZURE_TENANT_ID }}", CODE_ACCENT),
    ("    # no client-secret exists to leak", CODE_DIM),
], title="F-09 fixed \u00b7 OIDC federation replaces the committed DB password")

s.code(740, 990, 640, [
    ("securityContext:", CODE_FG),
    ("  runAsNonRoot: true", CODE_ACCENT),
    ("  readOnlyRootFilesystem: true", CODE_ACCENT),
    ("  allowPrivilegeEscalation: false", CODE_ACCENT),
    ("  capabilities: {drop: [ALL]}", CODE_ACCENT),
    ("# Gatekeeper denies the pod outright if any of", CODE_DIM),
    ("# these are missing, or the image is unsigned", CODE_DIM),
], title="F-10 fixed \u00b7 enforced at admission, not trusted to the Dockerfile")

s.code(1420, 990, 640, [
    ("images:", CODE_FG),
    ("- name: banking-app", CODE_FG),
    ("  newName: acrbankprod.azurecr.io/banking-app", CODE_ACCENT),
    ("  digest: sha256:9f2c4b7e...e41a", CODE_ACCENT),
    ("# Argo CD refuses to sync a mutable tag, so what", CODE_DIM),
    ("# was signed and scanned is exactly what runs", CODE_DIM),
], title="digest pinning \u00b7 tags are never deployed")

s.write("03-cicd-gitops.excalidraw")
