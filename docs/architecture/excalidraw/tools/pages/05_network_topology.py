"""Network topology -- hub and spoke, rewritten for comprehension.

A revision of the earlier hub-and-spoke page. The topology is the same in
outline; what changed is how much work the reader has to do, and which claims
the page is willing to make.

The earlier version put roughly twenty-five cards on the canvas with no reading
order, routed two arrows in long L-shapes across the whole page, placed the
"data" spoke far away from the services it fronted, and led every label with
vocabulary (IDPS, CSPM, UEBA, WORM, anycast). A reader who did not already know
the design could not recover it from the picture.

Four decisions drive this layout.

1. There is one numbered path, 1 to 7, and it is one banking payment from phone
   to database. The 1 -> 2 arrow is a single straight vertical, because the first
   thing a reader follows should not have a corner in it.

2. Everything real but off that path -- policy, monitoring, the registry,
   residency -- is in a right-hand column under a heading that says so. A reader
   who only wants the request path can stop at the gutter.

3. Labels lead with plain language and put the product name second. "checks the
   sign-in token first" earns its place; "validate-jwt" does not, because the
   reader who knows what it means did not need the diagram.

4. The page does not claim more than the platform delivers. Corrections carried
   in from the proposal paper's technical review, each verified against vendor
   documentation:

   * An internal Application Gateway now appears in the banking spoke. Front Door
     cannot use a VNet-injected classic API Management instance as a Private Link
     origin -- classic tiers must be in public mode for that -- so the earlier
     "Front Door -> Private Link -> APIM" path was unbuildable. An internal
     gateway in the spoke is the standard resolution, and it is also where
     merchant mutual TLS terminates, which Front Door does not support.
   * Two private-endpoint subnets, one per application, replace the single shared
     data spoke. A private endpoint installs a /32 system route that beats a
     0.0.0.0/0 user-defined route by longest-prefix match, so a shared endpoint
     subnet would have given each application a route to the other's database.
     Separation is enforced by separate subnets and deny-by-default rules, and
     the page says so rather than implying firewall inspection it does not get.
   * "the only public address" became "the only inbound path from the internet":
     the firewall, Bastion and the gateways all hold public addresses. What is
     true is that no *workload endpoint* is reachable from outside.
   * "inspects everything leaving" became "filters outbound traffic; inspects
     HTTP/S". Firewall Premium TLS inspection covers HTTP/S; PostgreSQL, Redis
     and AMQP get L4 rules and IDPS, not decryption.
   * The DNS card named the wrong product for its caption. Private endpoint names
     are resolved by Private DNS zones linked to each spoke; the DNS Private
     Resolver is the on-premises forwarding path. Both are named correctly now.
   * Azure Cache for Redis Enterprise retires in March 2027, so the cache is
     Azure Managed Redis.
   * The availability and cost figures are withdrawn rather than restated. A
     single 99.99% cannot be claimed for six components in series, and the
     published run rate omits the firewall, the DDoS plan, ExpressRoute and the
     recovery region.

The two database cards are named `bankdb` and `ecomdb`, and each has its own
endpoint and its own arrow. Which application owns which database is the single
most common question asked about this system, and the earlier draft answered it
in prose while the arrows said the opposite.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE

s = Scene("network-topology")

EDGE = SEM["edge"][1]
PLAT = SEM["platform"][1]
DATA = SEM["data"][1]
SECU = SEM["security"][1]
EXT = SEM["external"][1]

BADGE_FILL = "#1D4ED8"


def badge(n, x, y, d=32):
    """A numbered step marker on a card's top-left corner.

    Cards carrying one are inset 30px from their zone rather than 18px, so the
    badge clears the zone border and cannot be misread as labelling the zone.
    """
    s.ellipse(x, y, d, d, "platform", fill=BADGE_FILL, stroke=BADGE_FILL)
    s.text(str(n), x, y + (d - 18 * 1.25) / 2, d, 18, color="#FFFFFF",
           align="center", role="badge")


s.header(
    60, 50,
    "Network Topology \u2014 Hub and Spoke",
    "Follow the numbers 1 to 7: one banking payment, from phone to database. "
    "No workload endpoint is reachable from the internet, and each application reaches only its own database.",
    "CONSOLIDATION PROPOSAL  \u00b7  NETWORK TOPOLOGY",
    "Network connectivity diagram",
    w=1900,
)

# ----------------------------------------------------------------- 1. the edge
cust = s.icon("browser", 78, 205, 40)
s.text("Customer\nphone or browser", 48, 251, 100, 12, color=SUBTLE,
       align="center")

s.zone(180, 185, 520, 116, "Internet edge  \u2014  outside every network", "edge")
afd = s.card(210, 218, 460, 66, "frontdoor", "Front Door Premium", "edge",
             sub="WAF blocks bad requests. TLS ends here.\n"
                 "The only inbound path from the internet.")
badge(1, 194, 202)
s.arrow([(122, 236), (206, 236)], src=cust, dst=afd, color=EDGE)

# ------------------------------------------------------------- identity
s.zone(750, 185, 650, 116, "Identity  \u2014  who is asking", "security")
extid = s.card(768, 218, 300, 66, "externalid", "Entra External ID", "security",
               sub="customers sign in here:\nMFA, conditional access")
s.card(1088, 218, 294, 66, "entraid", "Entra ID and PIM", "security",
       sub="staff sign in here:\njust-in-time admin only")

# ------------------------------------------------------------------- region
s.zone(60, 420, 1370, 640,
       "Primary region: Southeast Asia (Singapore)  \u2014  three availability zones",
       "plain", label_size=16, label_align="right")

# spoke: banking
s.zone(90, 478, 400, 290, "Spoke: banking   10.1.0.0/16", "platform",
       label_size=14)
appgw = s.card(120, 512, 352, 60, "waf", "Application Gateway WAF v2",
               "platform", sub="internal; the Private Link origin")
apim = s.card(120, 600, 352, 60, "apim", "API Management Premium", "platform",
              sub="checks the sign-in token first")
aksb = s.card(120, 688, 352, 60, "aks", "AKS private cluster", "platform",
              sub="the banking app; no public API server")
badge(2, 104, 496)
badge(3, 104, 584)
badge(4, 104, 672)

# hub -- firewall last, so the arrows into the endpoint subnets leave the box
# that actually routes them, and both spokes reach it without crossing a sibling
s.zone(530, 478, 400, 330, "Hub VNet   10.0.0.0/16", "platform", label_size=14)
s.card(560, 512, 340, 60, "bastion", "Azure Bastion", "platform",
       sub="staff reach a jump host; no public SSH")
s.card(560, 586, 340, 60, "dns", "Azure DNS Private Resolver", "platform",
       sub="forwards DNS to and from on-premises")
er = s.card(560, 660, 340, 60, "expressroute", "ExpressRoute gateway",
            "platform", sub="private line to the PH datacentre")
fw = s.card(560, 738, 340, 60, "firewall", "Azure Firewall Premium", "platform",
            sub="filters outbound traffic; inspects HTTP/S")
badge(5, 544, 722)

# spoke: ecommerce
s.zone(1000, 478, 400, 200, "Spoke: ecommerce   10.2.0.0/16", "platform",
       label_size=14)
akse = s.card(1018, 512, 364, 60, "aks", "AKS private cluster", "platform",
              sub="the online shop")
s.card(1018, 586, 364, 60, None, "Order and catalog services", "platform",
       sub="our code; reads ecomdb only, never bankdb")

# the isolation rule, stated where the reader is looking at the spokes
s.text("The isolation rule", 100, 830, 380, 13, color=SUBTLE)
s.text("Route tables send each spoke's internet-bound\n"
       "traffic to the hub firewall.\n"
       "\n"
       "Spokes peer with the hub only, never with each\n"
       "other, so the two apps have no route between\n"
       "them.\n"
       "\n"
       "Each app has its own endpoint subnet with its\n"
       "own deny-by-default rules. That, not the\n"
       "firewall, is what keeps the two apart: Azure\n"
       "routes endpoint traffic directly unless a\n"
       "route-table policy says otherwise.",
       100, 852, 380, 12, color=BODY)

# private endpoint subnets -- one per application
# Label kept short and the cards' own text carries the meaning, so the two
# arrows entering from the firewall have clear air to the right of the label.
s.zone(530, 856, 400, 175, "Endpoint subnets", "platform", label_size=14)
pe_bank = s.card(560, 886, 160, 66, None, "Banking endpoint", "platform",
                 sub="reaches bankdb only")
pe_shop = s.card(740, 886, 160, 66, None, "Shop endpoint", "platform",
                 sub="reaches ecomdb only")
badge(6, 544, 870)

# spoke: shared services
s.zone(1000, 856, 400, 175, "Spoke: shared services   10.4.0.0/16", "platform",
       label_size=14)
s.card(1018, 886, 364, 54, "acr", "Container Registry Premium", "ops",
       sub="signed images only")
s.card(1018, 950, 364, 54, "loganalytics", "Log Analytics workspace", "ops",
       sub="every log and metric lands here")

# ------------------------------------------------------------- request path
# 1 -> 2. One straight vertical: the first thing a reader follows has no corner.
s.arrow([(440, 286), (440, 508)], src=afd, dst=appgw, color=EDGE)
# right-aligned so the ink ends beside the arrow it labels
s.text("Private Link \u2014 no public origin", 140, 372, 292, 11, color=EDGE,
       align="right")

# the shop's own inbound route, so the spoke is not left unreachable
s.arrow([(674, 251), (720, 251), (720, 440), (1300, 440), (1300, 508)],
        src=afd, dst=akse, color=EDGE, sharp=True)
s.text("shop traffic", 1230, 416, 160, 11, color=EDGE)

# 3 -> identity. Control-plane check, routed above the region.
s.arrow([(474, 618), (508, 618), (508, 350), (918, 350), (918, 286)],
        src=apim, dst=extid, color=SECU, style="dashed", sharp=True)
s.text("checks the token against Entra", 530, 322, 300, 11, color=SECU)

# 2 -> 3 -> 4, the hops the earlier draft left to adjacency
s.arrow([(296, 574), (296, 596)], src=appgw, dst=apim, color=PLAT)
s.arrow([(296, 662), (296, 684)], src=apim, dst=aksb, color=PLAT)

# 4 -> 5 and the shop's egress, into the same firewall
s.arrow([(474, 718), (518, 718), (518, 768), (556, 768)],
        src=aksb, dst=fw, color=PLAT, sharp=True)
s.arrow([(1016, 542), (950, 542), (950, 768), (904, 768)],
        src=akse, dst=fw, color=PLAT, sharp=True)

# 5 -> 6. Two arrows, because there are two endpoint subnets.
s.arrow([(700, 800), (700, 882)], src=fw, dst=pe_bank, color=PLAT)
s.arrow([(870, 800), (870, 882)], src=fw, dst=pe_shop, color=PLAT)

# 6 -> 7. Each endpoint reaches exactly one database, and each arrow is a single
# straight vertical landing inside the card it means. The earlier draft had one
# arrow ending in the gap between the two databases, bound to neither.
s.arrow([(700, 954), (700, 1151)], src=pe_bank, color=DATA)
s.arrow([(870, 954), (870, 1151)], src=pe_shop, color=DATA)

# ------------------------------------------------------------- on-premises
s.zone(60, 1120, 420, 240, "PH on-premises", "external")
core = s.card(78, 1155, 384, 62, "vm", "Core banking system", "external",
              sub="the system of record")
s.text("Reached only over ExpressRoute through the hub,\n"
       "never over the internet.\n"
       "\n"
       "An in-country copy of the audit record is kept\n"
       "here so a BSP examiner can inspect it locally.",
       78, 1235, 384, 12, color=BODY)
s.arrow([(558, 690), (498, 690), (498, 1080), (270, 1080), (270, 1151)],
        src=er, dst=core, color=EXT, sharp=True)
s.text("ExpressRoute \u2014 private line", 290, 1088, 220, 11, color=EXT)

# ------------------------------------------------------- managed data services
s.zone(530, 1120, 900, 240, "Azure managed data services", "data",
       label_align="right")
SVC = [
    ("postgres", "PostgreSQL: bankdb", "accounts, ledger, transactions", "data"),
    ("postgres", "PostgreSQL: ecomdb", "products, orders, stock", "data"),
    ("servicebus", "Service Bus Premium", "the only link between the apps", "data"),
    ("redis", "Azure Managed Redis", "sessions and idempotency keys", "data"),
    ("keyvault", "Key Vault and Managed HSM", "certificates and signing keys", "security"),
    ("storage", "ADLS Gen2", "immutable audit log, 7 years", "data"),
]
for i, (ik, title, sub, sem) in enumerate(SVC):
    s.card(560 + (i % 3) * 286, 1155 + (i // 3) * 76, 268, 62, ik, title, sem,
           sub=sub)
badge(7, 544, 1139)
s.text("Two separate servers, one for each app: the banking app has no route, no credential and no network path to ecomdb.\n"
       "Public network access is off on every one of these. The apps sign in with a managed identity, so there is no password to leak.",
       560, 1307, 840, 12, color=BODY)

# ------------------------------------------------------------- how to read
s.zone(1490, 185, 470, 220, "How to read this", "plain")
s.text("Follow the numbers 1 to 7: one banking\n"
       "payment, from phone to database.\n"
       "\n"
       "The shop has its own route into its own\n"
       "spoke, its own endpoint and its own database.\n"
       "\n"
       "Solid arrow = a request. Dashed = a check.\n"
       "Purple arrows end in stored data.\n"
       "\n"
       "Grey = outside our control. No icon = our\n"
       "own code, not an Azure service.",
       1508, 212, 434, 13, color=SUBTLE)

# --------------------------------------------------- off the request path
s.zone(1490, 478, 470, 255, "Always on, but off the request path", "ops")
GOV = [
    ("policy", "Azure Policy\nblocks non-compliant resources"),
    ("defender", "Defender for Cloud\nfinds misconfigurations"),
    ("sentinel", "Microsoft Sentinel\nsecurity alerting"),
    ("monitor", "Azure Monitor\ndashboards and SLOs"),
]
for i, (ik, label) in enumerate(GOV):
    s.stack(1607 + (i % 2) * 236, 515 + (i // 2) * 130, ik, label,
            icon_size=32, w=215, size=12)

# ------------------------------------------------------------- residency
s.zone(1490, 856, 470, 260, "Data residency and BSP examination", "external")
s.card(1508, 890, 434, 62, "storage", "In-country archive copy", "external",
       sub="replicated to the PH datacentre")
s.text("Processing happens in Singapore because Azure has\n"
       "no Philippine region. Singapore is about 30 to 40 ms\n"
       "from Manila and has three availability zones.\n"
       "\n"
       "This needs a cross-border transfer basis under\n"
       "RA 10173 and an outsourcing notification to the BSP.\n"
       "Confirm the current circular with compliance.",
       1508, 968, 434, 12, color=BODY)

# ------------------------------------------------------------- at a glance
s.zone(1490, 1180, 470, 180, "At a glance", "plain")
s.text("One region, one hub, four spokes.\n"
       "No workload endpoint is reachable from the internet.\n"
       "Two databases, two servers, one for each app.\n"
       "Internet-bound traffic leaves through one firewall.\n"
       "Availability and cost: see the proposal paper. The\n"
       "earlier 99.99% and USD 16k figures are withdrawn as\n"
       "unsupported; a corrected range is given there.",
       1508, 1208, 434, 12, color=SUBTLE)

# ------------------------------------------------------------------- legend
s.legend_row(60, 1420, ["edge", "platform", "data", "security", "ops",
                        "external"])
s.text("Source: docs/consolidation/CloudConsolidation_ProposalPaper.md  \u00b7  "
       "database ownership per banking-app/app.py and ecommerce-app/app.py",
       60, 1462, 1200, 11, color="#94A3B8")

s.write("05-network-topology.excalidraw")
