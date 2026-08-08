"""Page 6 -- the transformation itself.

Visual argument: side-by-side comparison with a one-to-one mapping. Every row on
the left is a thing that exists in the repository today; the row facing it is
what replaces it. The table underneath names the specific defect each swap
closes, so the migration reads as remediation rather than as a rewrite.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("transformation")

s.header(
    60, 50,
    "Transformation \u2014 Prototype to Azure Native",
    "What the repository deploys today, what replaces it, and which reviewed defect each change closes",
    "PAGE 6 of 6  \u00b7  TRANSFORMATION",
    w=2000,
)

ROWS = [
    # (icon_now, title_now, sub_now, icon_target, title_target, sub_target)
    ("aws", "AWS EC2 \u00b7 dev and test", "public IP, HTTP on port 80, cleartext",
     "aks", "AKS private clusters", "three zones, three node pools, Istio mTLS"),
    ("aci", "Azure ACI \u00b7 production", "delete + create, so every deploy is an outage",
     "argo", "Argo CD + Argo Rollouts", "canary with automatic rollback, no downtime"),
    ("docker", "Docker Hub  :latest", "public, unsigned, never scanned",
     "acr", "ACR Premium", "Notation-signed, digest-pinned, quarantined"),
    ("jenkins", "Jenkins over SSH", "StrictHostKeyChecking=no, DB password in the Jenkinsfile",
     "github", "GitHub Actions + OIDC", "federated to Azure, no stored credential exists"),
    ("mysql", "MySQL 5.7, single node", "public endpoint, money stored in FLOAT columns",
     "postgres", "PostgreSQL Flexible", "private endpoint, NUMERIC(19,4), zone-redundant HA"),
    ("python", "Flask session cookies", "hardcoded secret_key, passwords compared with ==",
     "externalid", "Entra External ID", "OIDC, MFA, passkeys, no password in the app at all"),
]

s.zone(60, 220, 760, 560, "TODAY  \u2014  what the repository actually deploys",
       "bad", label_size=15)
s.zone(900, 220, 760, 560, "TARGET  \u2014  Azure native", "ops", label_size=15)

BAD = SEM["bad"][1]
for i, (i_now, t_now, s_now, i_tgt, t_tgt, s_tgt) in enumerate(ROWS):
    y = 260 + i * 86
    a = s.card(80, y, 720, 66, i_now, t_now, "bad", sub=s_now)
    b = s.card(920, y, 720, 66, i_tgt, t_tgt, "ops", sub=s_tgt)
    s.arrow([(804, y + 33), (916, y + 33)], src=a, dst=b, color=BAD)

s.text("The functions do not change \u2014 a customer still scans a QR code and a merchant still gets paid.\nWhat changes is that every one of these boxes stops being a place where money or credentials can leak.",
       60, 800, 1600, 12, color=SUBTLE, align="left")

# ---------------------------------------------------------- what stays
s.zone(1740, 220, 320, 560, "Kept, deliberately", "plain", label_size=15)
s.text("Python and Flask stay. The reviewed\ndefects are not caused by the language,\nand rewriting the application would add\nrisk without closing a single finding.",
       1758, 258, 300, 11, color=BODY, align="left")
s.stack(1900, 336, "python", "Python 3.11", icon_size=34, w=200, size=11)
s.stack(1900, 430, "kubernetes", "packaged for Kubernetes", icon_size=34,
        w=280, size=11)
s.text("The domain logic is refactored into\nservices with clear boundaries, but it\nis still the same stack the team\nalready knows how to operate.\n\nThe migration is therefore reviewable\nas a sequence of behaviour-preserving\nsteps, not as a rebuild.",
       1758, 530, 300, 11, color=BODY, align="left")

# ---------------------------------------------------------- defect table
s.zone(60, 860, 2000, 240, "Reviewed defects closed by this migration", "plain",
       label_size=15)

s.text("DEFECT IN THE CURRENT CODE", 80, 896, 430, 11, color=BODY, align="left")
s.text("CLOSED BY", 530, 896, 470, 11, color=BODY, align="left")
s.text("DEFECT IN THE CURRENT CODE", 1080, 896, 430, 11, color=BODY, align="left")
s.text("CLOSED BY", 1530, 896, 500, 11, color=BODY, align="left")

s.text("F-01   Unauthenticated /paid callback\n"
       "F-02   Amount taken from client input\n"
       "F-03   Unsigned, tamperable QR URL\n"
       "F-04   Callback commits before the debit\n"
       "F-05   Double-spend race, no idempotency\n"
       "F-06   Money stored as binary float\n"
       "F-07   Plaintext passwords, == comparison",
       80, 920, 440, 11, color="#B91C1C", align="left")
s.text("Service Bus event over a private endpoint\n"
       "order-service resolves the real amount\n"
       "EMVCo TLV QR Ph + JWS from Managed HSM\n"
       "transactional outbox: commit, then publish\n"
       "SELECT FOR UPDATE + Redis idempotency key\n"
       "NUMERIC(19,4) + SUM(dr) - SUM(cr) = 0 check\n"
       "Entra External ID, no credential in the database",
       530, 920, 480, 11, color="#047857", align="left")

s.text("F-08   Hardcoded Flask secret_key\n"
       "F-09   Live DB password in the Jenkinsfile\n"
       "F-10   Containers run as root\n"
       "F-11   Silent SQLite fallback in production\n"
       "F-12   Plaintext Kubernetes Secret in git\n"
       "F-13   No rate limiting, fraud or AML hooks\n"
       "F-14   No observability",
       1080, 920, 440, 11, color="#B91C1C", align="left")
s.text("OIDC JWTs validated at API Management\n"
       "GitHub OIDC federation + Entra token auth\n"
       "distroless, runAsNonRoot, enforced at admission\n"
       "fail fast, no implicit local database\n"
       "Key Vault CSI driver + workload identity\n"
       "APIM quotas + fraud-service + aml-service\n"
       "OpenTelemetry to Monitor, SLOs and error budgets",
       1530, 920, 510, 11, color="#047857", align="left")

s.text("F-09 is a live credential in a public repository. Rotate it and purge it from git history \u2014 this migration removes the pattern, but it does not undo the exposure.",
       80, 1052, 1960, 12, color="#B91C1C", align="left")

s.write("06-transformation.excalidraw")
