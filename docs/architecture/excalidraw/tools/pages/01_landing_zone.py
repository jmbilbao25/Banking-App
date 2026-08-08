"""Page 1 -- Azure landing zone and network topology.

Visual argument: the network hierarchy IS the security model. Containment
(region > hub > spokes) carries the meaning; the reader can see that nothing in
a payment spoke has a public address, and that all egress is funnelled through
one firewall.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK, CODE_FG, CODE_ACCENT, CODE_DIM

s = Scene("landing-zone")

s.header(
    60, 50,
    "Azure Landing Zone \u2014 Network Topology",
    "QR payment platform (banking + e-commerce) \u00b7 hub-and-spoke, single Entra tenant, no public IP in any payment spoke",
    "PAGE 1 of 6  \u00b7  PLATFORM & NETWORK",
    w=2000,
)

# ---------------------------------------------------------------- actors
s.note(60, 168, 240, "External actors", size=13, color=BODY)
cust = s.icon("browser", 133, 196, 34)
s.text("Customer\nweb + mobile", 75, 236, 150, 12, color=SUBTLE, align="center")
merch = s.icon("devices", 133, 286, 34)
s.text("Merchant POS", 75, 326, 150, 12, color=SUBTLE, align="center")

# ---------------------------------------------------------------- edge
s.zone(360, 180, 660, 170, "Azure global edge \u2014 anycast, outside every VNet", "edge")
ddos = s.card(380, 214, 280, 58, "ddos", "DDoS Network Protection", "edge",
              sub="per-VNet telemetry, cost protection")
afd = s.card(690, 214, 310, 58, "frontdoor", "Front Door Premium", "edge",
             sub="WAF OWASP CRS 3.2 \u00b7 TLS 1.3 \u00b7 bot rules")
s.note(380, 288, 620,
       "Geo-filter PH-first \u00b7 rate limiting \u00b7 Private Link to origin.\n"
       "No public IP exists anywhere behind this edge.")

# ---------------------------------------------------------------- identity
s.zone(1060, 180, 440, 170, "Identity", "sec")
extid = s.card(1080, 214, 400, 58, "externalid", "Entra External ID", "sec",
               sub="OIDC \u00b7 MFA \u00b7 passkeys \u00b7 Conditional Access")
s.card(1080, 282, 400, 58, "managedid", "Workload identity federation", "sec",
       sub="no secrets in the cluster or the pipeline")

# ---------------------------------------------------------------- region
s.zone(60, 420, 1440, 620,
       "Primary region \u2014 Southeast Asia (Singapore) \u00b7 availability zones 1 \u00b7 2 \u00b7 3",
       "plain", label_size=16)

# hub
s.zone(90, 470, 470, 250, "Hub VNet   10.0.0.0/16", "net", label_size=13)
fw = s.card(110, 500, 205, 58, "firewall", "Firewall Premium", "net",
            sub="TLS inspection \u00b7 IDPS")
s.card(335, 500, 205, 58, "bastion", "Bastion", "net", sub="JIT via Entra PIM")
er = s.card(110, 568, 205, 58, "expressroute", "ExpressRoute GW", "net",
            sub="to PH core banking")
s.card(335, 568, 205, 58, "dns", "Private DNS Resolver", "net",
       sub="private endpoint DNS")
s.note(110, 646, 430,
       "Every spoke's default route (0.0.0.0/0) points here.\n"
       "Egress is FQDN-allowlisted; nothing leaves unfiltered.")

# banking spoke
s.zone(600, 470, 300, 250, "Spoke: banking   10.1.0.0/16", "compute", label_size=13)
apim = s.card(620, 500, 260, 58, "apim", "APIM Premium", "net",
              sub="validate-jwt \u00b7 quota \u00b7 mTLS")
aksb = s.card(620, 610, 260, 58, "aks", "AKS private cluster", "compute",
              sub="banking domain")

# ecommerce spoke
s.zone(940, 470, 270, 140, "Spoke: ecommerce   10.2.0.0/16", "compute", label_size=13)
akse = s.card(955, 500, 240, 58, "aks", "AKS private cluster", "compute",
              sub="storefront \u00b7 orders")

s.note(90, 724, 480,
       "Both clusters are private: the API server has no public endpoint.\n"
       "Spoke-to-spoke traffic is peered through the hub, never the internet.")

# data spoke
s.zone(90, 790, 1110,
       220, "Spoke: data   10.3.0.0/16 \u2014 private endpoints only, public network access disabled",
       "data", label_size=13)
cols = [110, 380, 650, 920]
row1 = [
    ("postgres", "PostgreSQL Flexible", "zone-redundant HA \u00b7 CMK"),
    ("redis", "Redis Enterprise", "idempotency \u00b7 locks"),
    ("servicebus", "Service Bus Premium", "topics \u00b7 sessions \u00b7 DLQ"),
    ("eventhubs", "Event Hubs", "capture to ADLS"),
]
row2 = [
    ("keyvault", "Key Vault Premium", "certificates \u00b7 secrets"),
    ("hsm", "Managed HSM", "FIPS 140-3 L3 \u00b7 QR signing key"),
    ("storage", "ADLS Gen2", "WORM \u00b7 legal hold \u00b7 7 years"),
    ("ledger", "Confidential Ledger", "receipt hash anchor"),
]
for x, (ik, t, sub) in zip(cols, row1):
    s.card(x, 825, 250, 58, ik, t, "data", sub=sub)
for x, (ik, t, sub) in zip(cols, row2):
    s.card(x, 900, 250, 58, ik, t, "data", sub=sub)
s.note(110, 972, 1070,
       "Access is private endpoint + managed identity only \u2014 no access keys, no public network access, no shared secrets.")

# shared services spoke
s.zone(1240, 790, 240, 220, "Spoke: shared   10.4.0.0/16", "ops", label_size=13)
acr = s.card(1252, 825, 216, 58, "acr", "ACR Premium", "ops",
             sub="signed \u00b7 quarantined")
law = s.card(1252, 900, 216, 58, "loganalytics", "Log Analytics", "ops",
             sub="workspace")

# ---------------------------------------------------------------- governance rail
s.zone(1560, 180, 500, 1110,
       "Governance, security & operations \u2014 subscription-wide", "plain", label_size=16)
rail = [
    ("policy", "Azure Policy", "PCI-DSS \u00b7 CIS \u00b7 ASB", "ops"),
    ("defender", "Defender for Cloud", "CSPM \u00b7 containers \u00b7 DB", "ops"),
    ("sentinel", "Microsoft Sentinel", "SIEM \u00b7 SOAR \u00b7 UEBA", "ops"),
    ("compliance", "Compliance evidence", "BSP \u00b7 NPC \u00b7 PCI", "ops"),
    ("monitor", "Azure Monitor", "OpenTelemetry traces", "ops"),
    ("grafana", "Managed Grafana", "SLO dashboards", "ops"),
    ("chaos", "Chaos Studio", "quarterly DR drills", "ops"),
    ("backupvault", "Backup Vault", "immutable \u00b7 PITR 35 d", "ops"),
]
sentinel_card = None
for i, (ik, t, sub, sem) in enumerate(rail):
    x = 1580 if i % 2 == 0 else 1828
    y = 216 + (i // 2) * 72
    c = s.card(x, y, 232, 58, ik, t, sem, sub=sub)
    if ik == "sentinel":
        sentinel_card = c

s.note(1580, 516, 480,
       "Policy is preventive, not advisory: a non-compliant\n"
       "resource fails at deployment and an unsigned image\n"
       "fails at admission.")

s.note(1580, 578, 300, "Colour key", size=13, color=INK)
s.legend(1580, 602, [
    ("edge", "Edge / internet"),
    ("net", "Network + gateway"),
    ("compute", "Compute (AKS)"),
    ("data", "Data + state"),
    ("sec", "Identity + keys"),
    ("ops", "Ops + supply chain"),
    ("ext", "External / on-prem"),
    ("bad", "Retired"),
], w=300)

s.note(1580, 830, 480,
       "Solid arrow = request path.\nDashed arrow = control or trust relationship.")

# evidence: the "no public endpoint" claim is a real deployment setting
s.code(1580, 890, 480, [
    ("resource azurerm_kubernetes_cluster {", CODE_FG),
    ("  private_cluster_enabled       = true", CODE_ACCENT),
    ("  api_server_access_profile {", CODE_FG),
    ("    authorized_ip_ranges = []", CODE_ACCENT),
    ("  }", CODE_FG),
    ("}", CODE_FG),
    ("resource azurerm_postgresql_flexible_server {", CODE_FG),
    ("  public_network_access_enabled = false", CODE_ACCENT),
    ("}", CODE_FG),
], title="enforced in Terraform \u00b7 platform repo")

s.code(1580, 1078, 480, [
    ("deny   public IP on any payment-spoke NIC", CODE_FG),
    ("deny   storage account with public access", CODE_FG),
    ("deny   image not signed by Notation", CODE_FG),
    ("deny   data resource without CMK", CODE_FG),
    ("audit  TLS below 1.2 anywhere", CODE_DIM),
], title="Azure Policy \u00b7 deny effects in the initiative")

# ---------------------------------------------------------------- on-premises
s.zone(60, 1120, 640, 170,
       "PH on-premises / co-location \u2014 reached over ExpressRoute", "ext")
core = s.card(80, 1155, 290, 58, "vm", "Core Banking System", "ext",
              sub="system of record")
s.card(390, 1155, 290, 58, "storage", "In-country archive", "ext",
       sub="BSP examination access")
s.note(80, 1228, 600,
       "Production data is processed in Singapore, so the design carries an explicit\n"
       "cross-border transfer basis (RA 10173) plus BSP outsourcing notification.")

# ---------------------------------------------------------------- retired
s.zone(760, 1120, 740, 170, "Retired by this design", "bad")
s.note(780, 1150, 340, "REMOVED", size=11, color="#B91C1C")
s.note(1140, 1150, 340, "REPLACED BY", size=11, color="#047857")
s.text("AWS EC2 (dev/test)\nDocker Hub  :latest\nAzure ACI (prod)\nJenkins + SSH keys\nMySQL 5.7",
       780, 1172, 340, 12, color=SUBTLE, align="left")
s.text("AKS \u2014 one tenant, one policy plane\nACR Premium \u2014 signed, digest-pinned\nAKS zone-spread, rolling + canary\nGitHub Actions OIDC \u2014 no stored creds\nPostgreSQL Flexible \u2014 NUMERIC(19,4)",
       1140, 1172, 360, 12, color=SUBTLE, align="left")

# ---------------------------------------------------------------- arrows
E = SEM["edge"][1]
N = SEM["net"][1]
C = SEM["compute"][1]
D = SEM["data"][1]
S = SEM["sec"][1]
O = SEM["ops"][1]
X = SEM["ext"][1]

s.arrow([(172, 213), (376, 226)], src=cust, dst=ddos, color=E)
s.arrow([(172, 303), (376, 254)], src=merch, dst=ddos, color=E)
s.arrow([(663, 243), (687, 243)], src=ddos, dst=afd, color=E)

s.arrow([(800, 274), (800, 497)], src=afd, dst=apim, color=E)
s.note(600, 352, 190, "Private Link\nno public origin", size=11, color=E)

s.arrow([(750, 560), (750, 608)], src=apim, dst=aksb, color=N)
s.note(762, 566, 90, "mTLS", size=11, color=N)
s.arrow([(882, 529), (953, 529)], src=apim, dst=akse, color=N)
s.note(886, 503, 68, "mTLS", size=11, color=N)

s.arrow([(870, 498), (870, 360), (1040, 360), (1040, 243), (1078, 243)],
        src=apim, dst=extid, color=S, style="dashed")
s.note(890, 366, 290, "validate-jwt against Entra", size=11, color=S)

s.arrow([(655, 670), (655, 786)], src=aksb, color=D)
s.note(665, 730, 210, "private endpoints", size=11, color=D)
s.arrow([(1160, 560), (1160, 786)], src=akse, color=D)

# ACR distribution bus -- one hub instead of two long crossing arrows
s.line([(830, 752), (1452, 752)], color=O, sw=2, style="dashed")
s.arrow([(1452, 823), (1452, 754)], src=acr, color=O, style="dashed")
s.arrow([(830, 750), (830, 672)], dst=aksb, color=O, style="dashed")
s.arrow([(1130, 750), (1130, 562)], dst=akse, color=O, style="dashed")
s.note(860, 726, 250, "signed images only", size=11, color=O)

s.arrow([(108, 597), (74, 597), (74, 1184), (78, 1184)],
        src=er, dst=core, color=X)
s.note(86, 1058, 320, "ExpressRoute private peering", size=11, color=X)

_scy = sentinel_card["y"] + sentinel_card["height"] / 2
s.arrow([(1470, 929), (1520, 929), (1520, _scy), (1578, _scy)],
        src=law, dst=sentinel_card, color=O, style="dashed")
s.note(1250, 968, 220, "all logs stream to Sentinel", size=11, color=O)

s.write("01-landing-zone.excalidraw")
