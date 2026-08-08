"""Page 3 -- AKS cluster and node pools.

The node pool is the isolation boundary. Pods are drawn as plain named chips
rather than repeated logos: at pod size a logo is unreadable and adds nothing,
while the pool colour and the node label already carry the placement story.
The real technologies appear once, at a legible size, in the add-ons band.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import (Scene, SEM, BODY, SUBTLE, INK, CODE_FG, CODE_ACCENT,
                   CODE_DIM)

s = Scene("cluster")

s.header(
    60, 50,
    "AKS Cluster \u2014 Node Pools and Workload Placement",
    "aks-bank-prod \u00b7 private cluster in spoke 10.1.0.0/16 \u00b7 three availability zones \u00b7 the pool is the isolation boundary",
    "PAGE 3 of 6  \u00b7  CLUSTER",
    "Deployment diagram",
    w=2000,
)


def node(x, y, w, label, chips, sem, *, h=88, chip_w=270):
    """One VM in a pool, holding named pod chips."""
    s.rect(x, y, w, h, "external", fill="#FFFFFF", stroke="#94A3B8", sw=2)
    s.text(label, x + 12, y + 8, w - 24, 11, color=SUBTLE, align="left")
    for i, name in enumerate(chips):
        s.card(x + 15 + i * (chip_w + 15), y + 30, chip_w, 44, None, name, sem,
               title_size=14)


# ------------------------------------------------------------ control plane
s.zone(60, 200, 1480, 120,
       "Managed control plane \u2014 Microsoft-managed, no public API endpoint",
       "platform")
CP = [
    ("aks", "Private API server", "reached through a private endpoint"),
    ("managedid", "Workload identity", "federated OIDC, no cluster secrets"),
    ("policy", "Azure Policy add-on", "Gatekeeper admission control"),
]
for i, (ik, t, sub) in enumerate(CP):
    s.card(80 + i * 490, 232, 470, 64, ik, t, "platform", sub=sub)

# ------------------------------------------------------------ pool: system
s.zone(60, 420, 640, 430, "Node pool:  system", "ops", label_size=15)
s.text("3 nodes, system-reserved  \u00b7  zones 1, 2, 3\ntaint  CriticalAddonsOnly=true:NoSchedule",
       76, 434, 620, 12, color=BODY, align="left")
node(80, 485, 600, "aks-sys-1  \u00b7  zone 1", ["coredns", "istiod"], "ops")
node(80, 585, 600, "aks-sys-2  \u00b7  zone 2",
     ["metrics-server", "gatekeeper"], "ops")
node(80, 685, 600, "aks-sys-3  \u00b7  zone 3",
     ["secrets-store CSI", "argocd"], "ops")
s.text("Cluster add-ons only. The taint keeps application pods off these\nnodes, so a busy workload cannot starve CoreDNS.",
       80, 785, 620, 12, color=BODY, align="left")

# ------------------------------------------------------------ pool: general
s.zone(740, 420, 640, 430, "Node pool:  general", "platform", label_size=15)
s.text("3 to 12 x Standard_D4s_v5  \u00b7  zones 1, 2, 3  \u00b7  autoscaler + KEDA\nlabel  workload=general",
       756, 434, 620, 12, color=BODY, align="left")
node(760, 485, 600, "aks-gen-1  \u00b7  zone 1",
     ["bff-service", "payment-orchestrator"], "platform")
node(760, 585, 600, "aks-gen-2  \u00b7  zone 2",
     ["fraud-service", "aml-service"], "platform")
node(760, 685, 600, "aks-gen-3  \u00b7  zone 3",
     ["audit-service", "notification-service"], "platform")
s.text("Banking domain services only. Commerce runs in its own cluster in\nspoke 10.2.0.0/16. Every pod carries an Istio sidecar, so pod-to-pod\ntraffic is mTLS whether or not the application knows it.",
       760, 782, 620, 12, color=BODY, align="left")

# ------------------------------------------------------------ pool: confidential
s.zone(1420, 420, 640, 430, "Node pool:  confidential", "security",
       label_size=15)
s.text("2 x Standard_DC4as_v5 (AMD SEV-SNP)  \u00b7  zones 1, 2\ntaint  workload=ledger:NoSchedule",
       1436, 434, 620, 12, color=BODY, align="left")
node(1440, 485, 600, "aks-conf-1  \u00b7  zone 1", ["ledger-service"],
     "security", chip_w=570)
node(1440, 585, 600, "aks-conf-2  \u00b7  zone 2", ["ledger-service"],
     "security", chip_w=570)
s.text("ledger-service is the only workload that tolerates this taint, so\nnothing else can be scheduled here. Memory is encrypted by the\nCPU, so neither the host OS nor the hypervisor can read it.\n\nGuest attestation is checked before a pod starts. A node that fails\nattestation is removed from the pool instead of receiving traffic.",
       1440, 690, 620, 12, color=BODY, align="left")

# ------------------------------------------------------------ add-ons
s.zone(60, 900, 1200, 160, "Platform add-ons, running in every pool", "ops")
ADDONS = [
    ("istio", "Istio\nmTLS STRICT"),
    ("cilium", "Cilium\neBPF network policy"),
    ("keda", "KEDA\nscale on queue depth"),
    ("argo", "Argo CD\nGitOps reconcile"),
    ("opa", "Gatekeeper\nadmission policy"),
    ("prometheus", "Prometheus\nmetrics and SLOs"),
]
for i, (ik, label) in enumerate(ADDONS):
    s.stack(165 + i * 190, 928, ik, label, icon_size=36, w=185, size=12)
s.text("Default-deny network policy: a pod reaches only the peers its policy names, so the ledger accepts traffic from the orchestrator alone.",
       80, 1016, 1160, 12, color=BODY, align="left")

# ------------------------------------------------------------ evidence
s.code(1320, 900, 740, [
    ("nodeSelector:", CODE_FG),
    ("  workload: ledger", CODE_ACCENT),
    ("tolerations:", CODE_FG),
    ("- key: workload", CODE_ACCENT),
    ("  value: ledger", CODE_ACCENT),
    ("  effect: NoSchedule", CODE_ACCENT),
    ("securityContext:", CODE_FG),
    ("  runAsNonRoot: true", CODE_ACCENT),
    ("  readOnlyRootFilesystem: true", CODE_ACCENT),
    ("# a pod without this toleration is rejected by the scheduler,", CODE_DIM),
    ("# not merely discouraged from landing here", CODE_DIM),
], title="ledger-service \u00b7 how the isolation is actually enforced")

# ------------------------------------------------------------ legend
s.legend_row(60, 1150, ["platform", "security", "ops"], lines=False)
s.text("Source: docs/architecture/target-azure-architecture.md", 60, 1192, 900,
       11, color="#94A3B8", align="left")

s.write("03-cluster.excalidraw")
