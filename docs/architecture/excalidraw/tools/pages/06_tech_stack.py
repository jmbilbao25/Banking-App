"""Page 6 -- the tech stack of the Azure-native target architecture.

The simplest page in the set: no arrows, no topology, no numbered path. Seven
horizontal bands, one per domain, each holding the real vendor marks for the
technologies the proposal actually selects.

Two decisions drive the content.

1. The bands are the proposal paper's own cost domains -- internet edge and
   identity, network and security perimeter, application platform, data and
   messaging, secrets and keys, build and deploy, observe and govern. Using the
   paper's taxonomy rather than inventing one means the page cannot drift from
   the document it summarises, and a reader can move between the two.

2. This is the *target*, not the prototype. The legacy stack was MySQL, Jenkins,
   AWS EC2 and Azure Container Instances; none of those appear here. PostgreSQL
   replaces MySQL, Azure DevOps replaces Jenkins, and two private AKS clusters
   replace the EC2-and-ACI split. What carries forward is the workload itself:
   it is still a Python and Flask application in a container.

Band colour reuses the set's taxonomy unchanged: orange is the internet edge,
blue is on the request path, purple holds state, amber is identity and keys, and
green is off the request path.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, LH, BODY, SUBTLE, INK, text_width

s = Scene("tech-stack")

# ---------------------------------------------------------------- geometry
X = 60            # left edge of every band
W = 1400          # band width
PAD = 20          # band inner padding
SLOTS = 6         # widest band holds six logos; all bands share the columns
GAP = 50          # vertical gap between bands, leaves room for the label above

# Shared column centres, so a four-logo band lines up with a six-logo one.
COL = [X + PAD + (W - 2 * PAD) / SLOTS * (i + 0.5) for i in range(SLOTS)]

ICON = 46
LABEL_W = 206
ROW_H = 113       # top of band to bottom of the caption block
NOTE_TOP = 122    # top of the note block, measured from the band top
NOTE_SIZE = 12
NOTE_LH = NOTE_SIZE * LH


def badge(col, band_y, icon_key, name, detail):
    """One logo with its name and one line of detail, centred in a column."""
    cx = COL[col]
    s.icon(icon_key, cx - ICON / 2, band_y + 28, ICON)
    ty = band_y + 28 + ICON + 8
    s.text(name, cx - LABEL_W / 2, ty, LABEL_W, 13, color=INK,
           align="center", role="stacklabel")
    s.text(detail, cx - LABEL_W / 2, ty + 13 * LH + 1, LABEL_W, 11,
           color=BODY, align="center", role="stacklabel")


class Layout:
    """Stacks bands top to bottom, growing a band when it carries a note.

    The note is a full-width block under the logo row rather than text squeezed
    into the unused columns: at six columns an unused slot is only ~225px wide,
    which is too narrow for a sentence worth reading.
    """

    def __init__(self, top):
        self.y = top

    def band(self, label, sem, logos, note=None):
        n = len(note.split("\n")) if note else 0
        h = (NOTE_TOP + n * NOTE_LH + 14) if note else (ROW_H + 27)
        y = self.y
        s.zone(X, y, W, h, label, sem)
        for col, (icon_key, name, detail) in enumerate(logos):
            badge(col, y, icon_key, name, detail)
        if note:
            s.text(note, X + PAD, y + NOTE_TOP, W - 2 * PAD, NOTE_SIZE,
                   color=BODY, align="left")
        self.y = y + h + GAP
        return y


# ---------------------------------------------------------------- header
s.header(
    X, 50,
    "The Tech Stack \u2014 Azure-Native Target",
    "Every technology the consolidated design selects, grouped by the cost "
    "domain it belongs to. One region: Southeast Asia (Singapore), three "
    "availability zones.",
    "CONSOLIDATION PROPOSAL  \u00b7  TECH STACK",
    "Technology stack diagram",
    w=W,
)

L = Layout(200)

# ------------------------------------------------- 1. internet edge and identity
L.band("Internet edge and identity  \u2014  outside every network", "edge", [
    ("frontdoor", "Front Door Premium", "the only inbound path"),
    ("waf", "Application Gateway WAF v2", "internal Private Link origin"),
    ("apim", "API Management Premium", "VNet-injected, checks the token"),
    ("externalid", "Entra External ID", "customers, MFA and CA"),
    ("entraid", "Entra ID and PIM", "staff, just-in-time admin"),
], note=(
    "TLS ends at Front Door, and no workload endpoint is reachable from the "
    "internet. API Management validates the sign-in token before AKS ever sees "
    "the request."
))

# ------------------------------------------------- 2. network perimeter
L.band("Network and security perimeter  \u2014  hub and spoke", "platform", [
    ("firewall", "Azure Firewall Premium", "one hub firewall, inspects HTTP/S"),
    ("bastion", "Azure Bastion", "jump host, no public SSH"),
    ("dns", "DNS Private Resolver", "forwards DNS to on-premises"),
    ("expressroute", "ExpressRoute", "private line to the PH core"),
    ("privatelink", "Private Endpoints", "one endpoint subnet per app"),
], note=(
    "Hub 10.0.0.0/16 with four spokes: banking 10.1, e-commerce 10.2, shared "
    "services 10.4, plus dev 10.10 and staging 10.20.\n"
    "Spokes peer only with the hub and never with each other, so neither "
    "application has a network path to the other's database."
))

# ------------------------------------------------- 3. application platform
L.band("Application platform", "platform", [
    ("aks", "AKS", "two private clusters"),
    ("keda", "KEDA", "scales on Service Bus depth"),
    ("helm", "Helm", "charts deploy the workload"),
    ("docker", "Docker", "container images"),
    ("python", "Python", "the application language"),
    ("flask", "Flask", "banking and shop services"),
], note=(
    "Each cluster has a tainted system pool, an app pool for baseline load, and "
    "a burst pool that KEDA scales on queue depth; the burst pool can run on ACI "
    "virtual nodes to avoid waiting for node provisioning.\n"
    "The Horizontal Pod Autoscaler scales pods, the Cluster Autoscaler scales "
    "nodes, and every node pool spans three availability zones."
))

# ------------------------------------------------- 4. data and messaging
L.band("Data and messaging", "data", [
    ("postgres", "PostgreSQL: bankdb", "4 vCore, zone-redundant HA"),
    ("postgres", "PostgreSQL: ecomdb", "2 vCore, zone-redundant HA"),
    ("redis", "Azure Managed Redis", "sessions, idempotency keys"),
    ("servicebus", "Service Bus Premium", "the only link between apps"),
    ("storage", "ADLS Gen2", "immutable audit log, 7 years"),
    ("flyway", "Flyway", "versioned schema migrations"),
], note=(
    "Two separate servers, not two databases on one server: the banking app has "
    "no route, no credential and no network path to ecomdb. This is the "
    "difference between separation enforced by the platform and separation "
    "asserted in configuration.\n"
    "Public network access is off on every one of these, and the apps sign in "
    "with a managed identity, so there is no password to leak."
))

# ------------------------------------------------- 5. secrets and keys
L.band("Secrets, keys and certificates", "security", [
    ("keyvault", "Key Vault Premium", "one vault per application"),
    ("hsm", "Managed HSM", "FIPS 140-2 Level 3"),
    ("managedid", "Managed Identity", "no stored passwords"),
    ("notary", "Notation", "signs every image"),
], note=(
    "Managed HSM holds the payment signing and certificate authority keys. It is "
    "a dedicated, always-on hardware pool billed by the hour, and one of the "
    "largest single line items in the design.\n"
    "Credentials are never environment variables, which is the specific defect "
    "of the prototype this replaces."
))

# ------------------------------------------------- 6. build and deploy
L.band("Build and deploy  \u2014  off the request path", "ops", [
    ("github", "GitHub", "source of record, webhook"),
    ("devops", "Azure DevOps", "pipeline control plane"),
    ("vmss", "VMSS agent pool", "self-hosted, no public IP"),
    ("sonarqubeserver", "SonarQube", "SAST and quality gate"),
    ("trivy", "Trivy", "image and IaC scanning"),
    ("acr", "Container Registry", "Premium, signed images only"),
], note=(
    "Three environments in their own spokes: dev 10.10.0.0/16, staging "
    "10.20.0.0/16, production 10.1.0.0/16. The agent pool runs in the "
    "shared-services spoke and reaches every target over private endpoints "
    "through the hub firewall.\n"
    "Flyway applies schema migrations before pods roll. Promotion between "
    "environments is an image import, never a rebuild, and production needs "
    "just-in-time dual approval through Entra ID PIM."
))

# ------------------------------------------------- 7. observe and govern
L.band("Observe and govern  \u2014  off the request path", "ops", [
    ("monitor", "Azure Monitor", "dashboards, alerts, SLOs"),
    ("loganalytics", "Log Analytics", "every log and metric"),
    ("sentinel", "Microsoft Sentinel", "SIEM and security alerting"),
    ("defender", "Defender for Cloud", "finds misconfigurations"),
    ("policy", "Azure Policy", "blocks non-compliant resources"),
], note=(
    "Always on, but never on the request path. Continuous immutable audit "
    "logging and real-time alerting are what BSP examination requires, and their "
    "absence is the forensic void identified in the current prototype."
))

# ---------------------------------------------------------------- legend
LEGEND_Y = L.y - GAP + 40


def legend_h(x, y, items, *, size=12, swatch=15, gap=28):
    """Horizontal legend with wording specific to this page.

    The shared LEGEND wording is service-oriented -- "Azure service on the
    request path" -- which would be wrong here, because Flask, Helm and Trivy
    are on this page and are not Azure services.
    """
    cx = x
    for sem, label in items:
        s.rect(cx, y, swatch, swatch, sem, radius=3, sw=2)
        lw = text_width(label, size)
        s.text(label, cx + swatch + 7, y, lw + 4, size, color=SUBTLE,
               align="left", role="legendlabel")
        cx += swatch + 7 + lw + gap
    return cx


legend_h(X, LEGEND_Y, [
    ("edge", "Internet edge"),
    ("platform", "On the request path"),
    ("data", "Data and state"),
    ("security", "Identity, keys and secrets"),
    ("ops", "Off the request path"),
])

s.text(
    "Bands are the cost domains used in the proposal paper, so this page and the "
    "cost model name the same things in the same order.\n"
    "This is the target design, not the current prototype: the legacy stack was "
    "MySQL, Jenkins, AWS EC2 and Azure Container Instances, none of which appear "
    "here. Nothing on this page is deployed. Logos belong to their respective "
    "owners.",
    X, LEGEND_Y + 42, W, 11, color="#94A3B8", align="left")

s.write("06-tech-stack.excalidraw")
