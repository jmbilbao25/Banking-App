"""Page 2 -- the Azure architecture.

One region, one virtual network, three subnets. Every service on this page is one
we could explain and price. The one piece of real nuance we kept is that the
managed data services are not inside a subnet: a private endpoint puts a network
card in our subnet, the service itself stays Azure-managed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("azure-architecture")

s.header(
    60, 50,
    "Azure Architecture \u2014 Channel Layer",
    "One region (Southeast Asia), one virtual network, three subnets. EastWest already runs Azure Bot Service and Logic Apps in this region.",
    "PAGE 2 of 4  \u00b7  AZURE ARCHITECTURE",
    "High-level system diagram",
    w=1900,
)

EDGE = SEM["edge"][1]
PLAT = SEM["platform"][1]
DATA = SEM["data"][1]
OPS = SEM["ops"][1]
EXT = SEM["external"][1]

# ---------------------------------------------------------------- entry
cust = s.icon("browser", 110, 225, 38)
s.text("Customers", 60, 269, 140, 12, color=SUBTLE, align="center")
afd = s.card(240, 215, 340, 58, "frontdoor", "Azure Front Door", "edge",
             sub="WAF rules, TLS termination")
s.arrow([(152, 244), (236, 244)], src=cust, dst=afd, color=EDGE)
s.text("The only address open to the internet.", 620, 236, 500, 12,
       color=SUBTLE, align="left")

# ---------------------------------------------------------------- the VNet
s.zone(60, 360, 1360, 290,
       "Virtual network   10.10.0.0/16   \u00b7   Southeast Asia", "platform",
       label_size=16, label_align="right")

s.zone(90, 415, 400, 185, "Subnet: gateway   10.10.1.0/24", "platform",
       label_size=13)
apim = s.card(105, 450, 370, 58, "apim", "API Management", "platform",
              sub="one entry point for every API")
s.text("Also where the access token is\nchecked, before anything reaches the app.",
       105, 520, 370, 12, color=BODY, align="left")

s.zone(520, 415, 440, 185, "Subnet: apps   10.10.2.0/24", "platform",
       label_size=13)
aks = s.card(535, 450, 410, 58, "aks", "AKS cluster", "platform",
             sub="EasyWay API + transfer service")
s.text("2 node pools, 3 nodes each,\nspread across 3 availability zones.",
       535, 520, 280, 12, color=BODY, align="left")

s.zone(990, 415, 400, 185, "Subnet: private endpoints   10.10.3.0/24",
       "platform", label_size=13)
pe = s.card(1005, 450, 370, 58, "privatelink", "Private endpoints", "platform",
            sub="one for each service below")
s.text("A private endpoint is a network card\nin our subnet. The service itself\nstays Azure-managed.",
       1005, 520, 370, 12, color=BODY, align="left")

s.arrow([(410, 275), (410, 400), (290, 400), (290, 446)], src=afd, dst=apim,
        color=EDGE, sharp=True)
s.arrow([(479, 479), (531, 479)], src=apim, dst=aks, color=PLAT)
s.arrow([(949, 479), (1001, 479)], src=aks, dst=pe, color=PLAT)

# ---------------------------------------------------------------- data
s.zone(60, 730, 1360, 200,
       "Azure data and messaging \u2014 reached only through those private endpoints",
       "data")
SVC = [
    ("postgres", "Azure PostgreSQL", "channel data, not the ledger", "data"),
    ("redis", "Azure Cache for Redis", "sessions and rate limits", "data"),
    ("servicebus", "Azure Service Bus", "notification queue", "data"),
    ("storage", "Azure Blob Storage", "uploaded documents", "data"),
    ("keyvault", "Azure Key Vault", "secrets and certificates", "security"),
]
for i, (ik, t, sub, sem) in enumerate(SVC):
    s.card(80 + i * 270, 770, 255, 66, ik, t, sem, sub=sub)
s.text("None of these has a public endpoint. The app signs in with its managed identity, so there is no database password in our code.",
       80, 862, 1340, 12, color=BODY, align="left")
s.arrow([(1190, 602), (1190, 726)], src=pe, color=DATA)

# ---------------------------------------------------------------- outside
s.zone(1480, 360, 480, 290, "Outside our network", "external")
tem = s.card(1500, 400, 440, 66, None, "Temenos SaaS core banking", "external",
             sub="accounts and postings\nreached over a private link")
s.card(1500, 485, 440, 58, None, "InstaPay and PESONet", "external",
       sub="via the bank's payment gateway")
s.card(1500, 555, 440, 58, None, "Infobip and MoEngage", "external",
       sub="SMS and push delivery")
s.arrow([(1392, 470), (1440, 470), (1440, 433), (1496, 433)], src=pe, dst=tem,
        color=EXT, sharp=True)
s.text("private link", 1396, 492, 90, 11, color=EXT, align="left")

# ---------------------------------------------------------------- monitoring
s.zone(1480, 730, 480, 200, "Monitoring", "ops")
s.card(1500, 770, 440, 58, "monitor", "Azure Monitor", "ops",
       sub="metrics, logs and alerts")
s.card(1500, 840, 440, 58, "appinsights", "Application Insights", "ops",
       sub="request traces from the app")
s.arrow([(930, 602), (930, 690), (1720, 690), (1720, 726)], src=aks, color=OPS,
        style="dashed", sharp=True)
s.text("logs and metrics", 950, 666, 220, 11, color=OPS, align="left")

# ---------------------------------------------------------------- note
s.text("In production this network would sit as a spoke off the bank's existing hub. We drew one virtual network because that is the part we\ncould design and defend ourselves.",
       60, 960, 1400, 12, color=BODY, align="left")

s.legend_row(60, 1030, ["edge", "platform", "data", "security", "ops",
                        "external"])
s.text("Region confirmed from EastWest's own ESTA chatbot, which calls prod-04.southeastasia.logic.azure.com",
       60, 1072, 1300, 11, color="#94A3B8", align="left")

s.write("02-azure-architecture.excalidraw")
