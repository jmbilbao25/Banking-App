"""Page 6 -- resilience and disaster recovery.

Side by side. Both regions are coloured by what each component IS, so a colour
never changes meaning between the two halves; ACTIVE versus WARM STANDBY is
carried by the border style and the region labels instead. That keeps the
distinction legible without colour, and keeps the shared taxonomy intact.

The stateful services face each other across the middle corridor so every
replication arrow is short and unambiguous about what replicates to what.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, BODY, SUBTLE, INK

s = Scene("resilience")

s.header(
    60, 50,
    "Resilience \u2014 Zone Redundancy and Regional Failover",
    "Zone-redundant inside Singapore (RPO 0) \u00b7 warm standby in Hong Kong (RPO 60 s or better, RTO 15 min) \u00b7 immutable backups outside both",
    "PAGE 6 of 6  \u00b7  RESILIENCE",
    "Availability and resilience map",
    w=2000,
)

EDGE = SEM["edge"][1]
DATA = SEM["data"][1]
RED = "#B91C1C"

# ---------------------------------------------------------------- edge
cust = s.icon("browser", 100, 200, 38)
s.text("Customers", 50, 244, 140, 12, color=SUBTLE, align="center")

afd = s.card(300, 190, 480, 64, "frontdoor", "Front Door Premium", "edge",
             sub="health probes, automatic origin failover")
s.arrow([(142, 219), (296, 219)], src=cust, dst=afd, color=EDGE)
s.text("Front Door decides. Singapore is priority 1; if its health probe fails, traffic moves to\nHong Kong without a DNS change and without a client-side retry.",
       820, 196, 900, 12, color=SUBTLE, align="left")

# ---------------------------------------------------------------- primary
s.zone(60, 350, 900, 400,
       "PRIMARY  \u00b7  Southeast Asia (Singapore)  \u00b7  ACTIVE", "plain", sw=3,
       label_size=15)
p_apim = s.card(80, 396, 420, 58, "apim", "API Management Premium", "platform",
                sub="multi-region unit")
s.card(80, 466, 420, 58, "aks", "AKS", "platform",
       sub="system and general pools across zones 1, 2, 3")
s.card(80, 536, 420, 58, "hsm", "Managed HSM", "security",
       sub="key shares spread across zones")
p_pg = s.card(520, 396, 420, 66, "postgres", "PostgreSQL Flexible", "data",
              sub="zone-redundant HA, synchronous standby\nRPO 0 inside the region")
p_rd = s.card(520, 474, 420, 58, "redis", "Cache for Redis Enterprise", "data",
              sub="zone-redundant")
p_sb = s.card(520, 544, 420, 58, "servicebus", "Service Bus Premium", "data",
              sub="geo-DR primary alias")

s.text("Losing one availability zone costs nothing here: the database fails over to its\nsynchronous standby, and the general pool already holds replicas in the other two\nzones. The confidential pool spans two zones, so a ledger replica keeps serving.",
       80, 626, 860, 12, color=BODY, align="left")
s.text("An availability zone is a separate datacentre with independent power and cooling,\nso this is real fault isolation rather than a rack label.",
       80, 694, 860, 12, color=BODY, align="left")

# ---------------------------------------------------------------- secondary
s.zone(1160, 350, 900, 400,
       "SECONDARY  \u00b7  East Asia (Hong Kong)  \u00b7  WARM STANDBY", "plain",
       sw=3, style="dashed", label_size=15)
s_pg = s.card(1180, 396, 420, 66, "postgres", "Read replica", "data",
              sub="asynchronous, promotable\nRPO 60 s or better", style="dashed")
s_rd = s.card(1180, 474, 420, 58, "redis", "Redis geo-replica", "data",
              sub="read-only until promoted", style="dashed")
s_sb = s.card(1180, 544, 420, 58, "servicebus", "Service Bus geo-DR", "data",
              sub="secondary namespace", style="dashed")
s_apim = s.card(1620, 396, 420, 58, "apim", "API Management Premium",
                "platform", sub="second gateway unit of the same resource",
                style="dashed")
s.card(1620, 466, 420, 58, "aks", "AKS", "platform",
       sub="minimum size, manifests synced by Argo CD", style="dashed")
s.card(1620, 536, 420, 58, "hsm", "Managed HSM", "security",
       sub="same security domain", style="dashed")

s.text("Warm, not idle. Argo CD keeps the manifests identical, so failover is a promote-and-\nscale operation rather than a rebuild.",
       1180, 626, 860, 12, color=BODY, align="left")
s.text("What this deliberately is not is active-active: two regions writing one ledger would\nneed consensus on every posting, and that latency is not worth paying here.",
       1180, 694, 860, 12, color=BODY, align="left")

# ---------------------------------------------------------------- traffic
s.arrow([(440, 256), (440, 392)], src=afd, dst=p_apim, color=EDGE)
s.text("priority 1", 452, 296, 140, 11, color=EDGE, align="left")

s.arrow([(782, 240), (1700, 240), (1700, 392)], src=afd, dst=s_apim,
        color=RED, style="dashed", sharp=True)
s.text("priority 2, on probe failure", 1710, 264, 300, 11, color=RED,
       align="left")

# ---------------------------------------------------------------- replication
for y, label in ((429, "asynchronous replication"), (503, "geo-replication"),
                 (573, "geo-DR pairing")):
    s.text(label, 962, y - 26, 200, 11, color=DATA, align="left")
s.arrow([(944, 429), (1176, 429)], src=p_pg, dst=s_pg, color=DATA,
        style="dashed")
s.arrow([(944, 503), (1176, 503)], src=p_rd, dst=s_rd, color=DATA,
        style="dashed")
s.arrow([(944, 573), (1176, 573)], src=p_sb, dst=s_sb, color=DATA,
        style="dashed")

# ---------------------------------------------------------------- backups
s.zone(60, 850, 1180, 220,
       "Backup and archive \u2014 a separate fault domain from both regions",
       "data")
b1 = s.card(80, 890, 350, 62, "backupvault", "Backup Vault", "data",
            sub="immutable, soft delete\npoint-in-time restore 35 days")
b2 = s.card(470, 890, 350, 62, "storage", "ADLS Gen2, WORM", "data",
            sub="legal hold\n7-year retention")
b3 = s.card(860, 890, 360, 62, "ledger", "Confidential Ledger", "data",
            sub="independent integrity anchor")
s.arrow([(434, 921), (466, 921)], src=b1, dst=b2, color=DATA)
s.arrow([(824, 921), (856, 921)], src=b2, dst=b3, color=DATA)
s.text("Immutability is the point: ransomware that reaches the subscription still cannot delete or rewrite these\ncopies, and the ledger anchor lets an examiner prove a receipt was never edited after the fact.",
       80, 980, 1140, 12, color=BODY, align="left")
s.text("A copy is replicated on to the PH co-location so a BSP examiner can inspect records in country.",
       80, 1024, 1140, 12, color=BODY, align="left")

# ---------------------------------------------------------------- targets
s.zone(1300, 850, 760, 220, "Targets, and how they are proven", "plain",
       label_size=15)
s.text("RPO    0 inside the region, 60 seconds or better cross-region\nRTO    15 minutes to serve traffic from Hong Kong",
       1320, 890, 720, 14, color=INK, align="left")
s.card(1320, 950, 720, 58, "chaos", "Azure Chaos Studio", "ops",
       sub="runs the failover drill quarterly and records the evidence")
s.text("The numbers above are measured by that drill rather than asserted in a document.",
       1320, 1024, 720, 12, color=BODY, align="left")

# ---------------------------------------------------------------- legend
s.legend_row(60, 1120, ["edge", "platform", "data", "security", "ops"])
s.text("Dashed border = warm standby, not serving traffic until promoted.",
       60, 1160, 700, 12, color=SUBTLE, align="left")
s.text("Source: docs/architecture/target-azure-architecture.md", 60, 1194, 900,
       11, color="#94A3B8", align="left")

s.write("06-resilience.excalidraw")
