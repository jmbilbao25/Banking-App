"""Page 5 -- resilience and disaster recovery.

Visual argument: side-by-side comparison. The two regions are drawn with
different weight -- primary in full colour, secondary in grey -- so the reader
sees at a glance that this is warm standby, not active-active. The stateful
services face each other across the middle corridor, so each replication arrow
is short and unambiguous about what replicates to what.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import (Scene, SEM, BODY, SUBTLE, INK, CODE_FG, CODE_ACCENT,
                   CODE_DIM)

s = Scene("dr-resilience")

s.header(
    60, 50,
    "Resilience \u2014 Zone Redundancy and Regional Failover",
    "Zone-redundant inside Singapore (RPO 0) \u00b7 warm standby in Hong Kong (RPO 60 s, RTO 15 min) \u00b7 in-country archive for BSP examination",
    "PAGE 5 of 6  \u00b7  RESILIENCE & DR",
    w=2000,
)

E = SEM["edge"][1]
D = SEM["data"][1]
RED = "#B91C1C"

# ------------------------------------------------------------ edge
cust = s.icon("browser", 100, 196, 34)
s.text("Customers", 60, 236, 120, 12, color=SUBTLE, align="center")

afd = s.card(300, 190, 460, 58, "frontdoor", "Front Door Premium", "edge",
             sub="health probes \u00b7 automatic origin failover")
s.arrow([(138, 213), (296, 215)], src=cust, dst=afd, color=E)

s.text("Front Door decides. Priority 1 is Singapore; if its health probe fails, traffic moves to\nHong Kong without a DNS change and without a client-side retry.",
       800, 264, 900, 12, color=SUBTLE, align="left")

# ------------------------------------------------------------ PRIMARY (stateful on the right, facing the corridor)
s.zone(60, 340, 900, 400,
       "PRIMARY  \u00b7  Southeast Asia (Singapore)  \u00b7  ACTIVE", "ops",
       sw=3, label_size=15)
p_apim = s.card(80, 392, 420, 56, "apim", "APIM Premium", "ops",
                sub="multi-region unit")
p_aks = s.card(80, 470, 420, 56, "aks", "AKS", "ops",
               sub="node pools across zones 1 \u00b7 2 \u00b7 3")
p_hsm = s.card(80, 548, 420, 56, "hsm", "Managed HSM", "ops",
               sub="3 of 5 key shares, multi-zone")
p_pg = s.card(520, 392, 420, 66, "postgres", "PostgreSQL Flexible", "ops",
              sub="zone-redundant HA \u00b7 sync standby\nRPO = 0 inside the region")
p_rd = s.card(520, 470, 420, 66, "redis", "Redis Enterprise", "ops",
              sub="zone-redundant\nidempotency keys survive a zone loss")
p_sb = s.card(520, 548, 420, 56, "servicebus", "Service Bus Premium", "ops",
              sub="geo-DR primary alias")

s.text("Losing one availability zone costs nothing: the database fails over to its synchronous\nstandby, the node pools already have replicas in the other two zones, and the\nPodDisruptionBudget keeps two ledger replicas serving.",
       80, 626, 880, 12, color=BODY, align="left")
s.text("An availability zone is a separate datacentre with independent power and cooling, so\nthis is real fault isolation rather than a rack label.",
       80, 684, 880, 12, color=BODY, align="left")

# ------------------------------------------------------------ SECONDARY (stateful on the left, facing the corridor)
s.zone(1160, 340, 900, 400,
       "SECONDARY  \u00b7  East Asia (Hong Kong)  \u00b7  WARM STANDBY", "ext",
       sw=3, label_size=15)
s_pg = s.card(1180, 392, 420, 66, "postgres", "Read replica", "ext",
              sub="asynchronous \u00b7 promotable\nRPO 60 s or better")
s_rd = s.card(1180, 470, 420, 66, "redis", "Redis geo-replica", "ext",
              sub="active geo-replication\nread-only until promoted")
s_sb = s.card(1180, 548, 420, 56, "servicebus", "Service Bus geo-DR", "ext",
              sub="secondary namespace")
s_apim = s.card(1620, 392, 420, 56, "apim", "APIM Premium", "ext",
                sub="same gateway configuration")
s_aks = s.card(1620, 470, 420, 56, "aks", "AKS", "ext",
               sub="scaled to minimum, synced by Argo CD")
s_hsm = s.card(1620, 548, 420, 56, "hsm", "Managed HSM", "ext",
               sub="same security domain, restored")

s.text("Warm, not idle. Argo CD keeps the manifests identical, so failover is a promote-and-scale\noperation rather than a rebuild.\n\nWhat this deliberately is NOT is active-active: two regions writing one ledger would need\nconsensus on every posting, and that latency cost is not worth paying for this workload.",
       1180, 626, 880, 12, color=BODY, align="left")

# ------------------------------------------------------------ traffic + replication
s.arrow([(450, 250), (450, 388)], src=afd, dst=p_apim, color=E)
s.text("priority 1", 460, 286, 140, 11, color=E, align="left")

s.arrow([(762, 219), (1700, 219), (1700, 388)], src=afd, dst=s_apim,
        color=RED, style="dashed")
s.text("priority 2\non probe failure", 1710, 264, 300, 11, color=RED,
       align="left")

s.arrow([(944, 425), (1176, 425)], src=p_pg, dst=s_pg, color=D, style="dashed")
s.text("async replication", 962, 400, 200, 11, color=D, align="left")
s.arrow([(944, 503), (1176, 503)], src=p_rd, dst=s_rd, color=D, style="dashed")
s.text("geo-replication", 968, 478, 190, 11, color=D, align="left")
s.arrow([(944, 576), (1176, 576)], src=p_sb, dst=s_sb, color=D, style="dashed")
s.text("geo-DR pairing", 968, 551, 190, 11, color=D, align="left")

# ------------------------------------------------------------ backup chain
s.zone(60, 820, 1000, 240,
       "Backup and archive \u2014 independent of both regions", "data")
b1 = s.card(80, 860, 300, 62, "backupvault", "Backup Vault", "data",
            sub="immutable \u00b7 soft delete\nPITR 35 days")
b2 = s.card(420, 860, 300, 62, "storage", "ADLS Gen2 (WORM)", "data",
            sub="legal hold \u00b7 7 year retention")
b3 = s.card(760, 860, 280, 62, "ledger", "Confidential Ledger", "data",
            sub="independent integrity anchor")
s.arrow([(382, 891), (416, 891)], src=b1, dst=b2, color=D)
s.arrow([(722, 891), (756, 891)], src=b2, dst=b3, color=D)
arch = s.card(80, 946, 660, 46, "vm",
              "In-country archival copy \u00b7 PH co-location", "ext",
              sub="replicated from ADLS for BSP examination access")
s.arrow([(560, 926), (560, 942)], src=b2, dst=arch, color=D, style="dashed")
s.text("Immutability is the point: ransomware that reaches the subscription still cannot delete or rewrite\nthese copies, and the ledger anchor lets an examiner prove a receipt was never edited.",
       80, 1006, 960, 12, color=BODY, align="left")

# ------------------------------------------------------------ targets
s.zone(1120, 820, 940, 240, "Targets and how they are proven", "plain",
       label_size=14)
s.text("RPO    0 inside the region  \u00b7  60 s cross-region\nRTO    15 minutes to serve traffic from Hong Kong\nDrills quarterly, evidence retained for the examiner",
       1140, 858, 600, 13, color=INK, align="left")

s.code(1140, 934, 900, [
    ("az postgres flexible-server replica promote  \\", CODE_ACCENT),
    ("   --name pg-bank-ea --resource-group rg-data-ea", CODE_FG),
    ("# then scale the AKS node pools, flip the Service Bus alias, and let", CODE_DIM),
    ("# Front Door's probe move traffic. Chaos Studio runs this on a schedule,", CODE_DIM),
    ("# so the number above is measured rather than asserted.", CODE_DIM),
], title="failover runbook \u00b7 executed by Chaos Studio, not by a wiki page")

s.write("05-dr-resilience.excalidraw")
