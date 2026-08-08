"""Page 2 -- network topology.

Hub and spoke, with the hub in the middle so both workload spokes sit next to
the firewall they egress through.

The important accuracy point: the managed data services are NOT inside a subnet.
They live outside every VNet and are reached through private endpoints, so they
are drawn outside the region boundary with the private endpoint subnet as the
only way in.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("network")

s.header(
    60, 50,
    "Network Topology \u2014 Hub and Spoke",
    "One region: a hub and four spokes. No public inbound path to a workload, and the managed data services sit outside every VNet behind private endpoints.",
    "PAGE 2 of 6  \u00b7  NETWORK",
    "Network connectivity diagram",
    w=2000,
)

EDGE = SEM["edge"][1]
PLAT = SEM["platform"][1]
DATA = SEM["data"][1]
SECU = SEM["security"][1]
EXT = SEM["external"][1]

# ---------------------------------------------------------------- edge
cust = s.icon("browser", 110, 245, 38)
s.text("Customers", 60, 289, 140, 12, color=SUBTLE, align="center")

s.zone(240, 200, 760, 120,
       "Azure global edge \u2014 anycast, outside every VNet", "edge")
ddos = s.card(260, 232, 320, 64, "ddos", "DDoS Network Protection", "edge",
              sub="always-on mitigation")
afd = s.card(610, 232, 370, 64, "frontdoor", "Front Door Premium", "edge",
             sub="WAF (OWASP CRS 3.2), TLS 1.3")
s.arrow([(152, 264), (256, 264)], src=cust, dst=ddos, color=EDGE)
s.arrow([(583, 264), (607, 264)], src=ddos, dst=afd, color=EDGE)

# ---------------------------------------------------------------- identity
s.zone(1040, 200, 500, 120, "Identity", "security")
extid = s.card(1060, 232, 460, 64, "externalid", "Entra External ID",
               "security", sub="OIDC, MFA, Conditional Access")

# ---------------------------------------------------------------- region
s.zone(60, 410, 1480, 420,
       "Primary region \u2014 Southeast Asia (Singapore), availability zones 1, 2, 3",
       "plain", label_size=16, label_align="right")

# spoke: banking
s.zone(90, 465, 330, 250, "Spoke: banking   10.1.0.0/16", "platform",
       label_size=14)
apim = s.card(105, 500, 300, 58, "apim", "API Management Premium",
              "platform", sub="VNet-injected, validate-jwt, mTLS")
aksb = s.card(105, 566, 300, 58, "aks", "AKS private cluster", "platform",
              sub="banking domain")
s.text("Private cluster: the API server\nhas no public endpoint.",
       105, 636, 300, 12, color=BODY, align="left")

# hub -- centre, so both spokes are adjacent to the firewall
s.zone(460, 465, 330, 320, "Hub VNet   10.0.0.0/16", "platform", label_size=14)
fw = s.card(475, 500, 300, 58, "firewall", "Azure Firewall Premium",
            "platform", sub="TLS inspection, IDPS")
s.card(475, 566, 300, 58, "bastion", "Azure Bastion", "platform",
       sub="JIT access via Entra PIM")
s.card(475, 632, 300, 58, "dns", "Private DNS Resolver", "platform",
       sub="resolves the private endpoint names")
er = s.card(475, 698, 300, 58, "expressroute", "ExpressRoute gateway",
            "platform", sub="to the PH datacentre")

# spoke: commerce
s.zone(830, 465, 330, 250, "Spoke: ecommerce   10.2.0.0/16", "platform",
       label_size=14)
akse = s.card(845, 500, 300, 58, "aks", "AKS private cluster", "platform",
              sub="commerce domain")
s.text("A separate trust zone. It never\nreaches banking data directly,\nonly published events.",
       845, 570, 300, 12, color=BODY, align="left")

# spoke: data (private endpoints only)
s.zone(1200, 465, 320, 250, "Spoke: data   10.3.0.0/16", "platform",
       label_size=14)
pe = s.card(1215, 500, 290, 58, "privatelink", "Private endpoint subnet",
            "platform", sub="10.3.1.0/24")
s.text("This subnet holds only network\ninterfaces. The services they\nreach live outside every VNet.",
       1215, 570, 180, 12, color=BODY, align="left")

s.text("All spoke egress is forced through the hub firewall by a default route.",
       90, 800, 700, 12, color=BODY, align="left")

# ---------------------------------------------------------------- traffic
s.arrow([(795, 298), (795, 370), (340, 370), (340, 496)],
        src=afd, dst=apim, color=EDGE, sharp=True)
s.text("Private Link \u2014 no public origin", 350, 344, 340, 11, color=EDGE,
       align="left")

s.arrow([(390, 498), (390, 430), (1010, 430), (1010, 264), (1056, 264)],
        src=apim, dst=extid, color=SECU, style="dashed", sharp=True)
s.text("validate-jwt against Entra", 700, 408, 300, 11, color=SECU,
       align="left")

s.arrow([(407, 595), (440, 595), (440, 529), (473, 529)], src=aksb, dst=fw,
        color=PLAT, sharp=True)
s.arrow([(843, 529), (777, 529)], src=akse, dst=fw, color=PLAT)

s.arrow([(1420, 560), (1420, 876)], src=pe, color=DATA)
s.text("private endpoint", 1180, 800, 230, 11, color=DATA, align="right")

# ---------------------------------------------------------------- on-premises
s.zone(60, 880, 520, 220, "PH on-premises", "external")
core = s.card(80, 915, 480, 58, "vm", "Core banking system", "external",
              sub="system of record")
s.text("Reached over ExpressRoute through the hub, never over the\ninternet. An in-country archive copy is kept so a BSP\nexaminer can inspect records locally.",
       80, 985, 480, 12, color=BODY, align="left")
s.arrow([(625, 758), (625, 850), (320, 850), (320, 911)], src=er, dst=core,
        color=EXT, sharp=True)
s.text("ExpressRoute", 340, 852, 200, 11, color=EXT, align="left")

# ---------------------------------------------------------------- PaaS
s.zone(640, 880, 900, 220,
       "Azure PaaS \u2014 outside every VNet, reached only through a private endpoint",
       "data")
PAAS = [
    ("postgres", "PostgreSQL Flexible", "zone-redundant HA"),
    ("redis", "Redis Enterprise", "idempotency and locks"),
    ("servicebus", "Service Bus Premium", "topics and dead-letter"),
    ("keyvault", "Key Vault Premium", "certificates and secrets"),
    ("hsm", "Managed HSM", "FIPS 140-3 L3 signing key"),
    ("storage", "ADLS Gen2", "WORM, 7-year retention"),
]
KEYS = {"keyvault", "hsm"}
for i, (ik, t, sub) in enumerate(PAAS):
    s.card(660 + (i % 3) * 290, 920 + (i // 3) * 75, 280, 64, ik, t,
           "security" if ik in KEYS else "data", sub=sub)
s.text("Public network access is disabled on all six. Access is private endpoint plus workload identity, so there is no key to leak.",
       660, 1070, 860, 12, color=BODY, align="left")

# ---------------------------------------------------------------- governance
s.zone(1580, 410, 480, 150, "Spoke: shared services   10.4.0.0/16",
       "platform", label_size=14)
s.card(1600, 445, 440, 54, "acr", "Container Registry Premium", "ops",
       sub="signed images, geo-replicated")
s.card(1600, 505, 440, 54, "loganalytics", "Log Analytics workspace", "ops",
       sub="cluster and gateway telemetry")

s.zone(1580, 620, 480, 260, "Governance, subscription-wide", "plain",
       label_size=15)
GOV = [
    ("policy", "Azure Policy\nPCI-DSS and CIS"),
    ("defender", "Defender for Cloud\nCSPM and containers"),
    ("sentinel", "Microsoft Sentinel\nSIEM, SOAR, UEBA"),
    ("monitor", "Azure Monitor\nOpenTelemetry and SLOs"),
]
for i, (ik, label) in enumerate(GOV):
    s.stack(1700 + (i % 2) * 240, 655 + (i // 2) * 105, ik, label,
            icon_size=32, w=215, size=12)

# ---------------------------------------------------------------- residency
s.zone(1580, 910, 480, 190, "Data residency", "external")
s.card(1600, 945, 440, 54, "storage", "In-country archive", "external",
       sub="replicated for BSP examination")
s.text("Processing happens in Singapore, so the design carries a\ncross-border transfer basis under RA 10173 and a BSP\nnotification. Microsoft Purview classifies the data and\ntracks its residency lineage.",
       1600, 1008, 440, 12, color=BODY, align="left")

# ---------------------------------------------------------------- legend
s.legend_row(60, 1150, ["edge", "platform", "data", "security", "ops", "external"])
s.text("Source: docs/architecture/target-azure-architecture.md", 60, 1192, 900,
       11, color="#94A3B8", align="left")

s.write("02-network.excalidraw")
