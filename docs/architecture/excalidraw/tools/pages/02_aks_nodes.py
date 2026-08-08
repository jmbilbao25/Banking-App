"""Page 2 -- AKS cluster: node pools and workload placement.

Visual argument: the node pool IS the isolation boundary. Nesting
(cluster > pool > node > pod) carries the meaning, and the reader can see that
the ledger physically cannot share a kernel with anything else.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import (Scene, SEM, BODY, SUBTLE, INK, CODE_FG, CODE_ACCENT,
                   CODE_DIM, LH)

s = Scene("aks-nodes")

s.header(
    60, 50,
    "AKS Cluster \u2014 Node Pools & Workload Placement",
    "aks-bank-prod \u00b7 private cluster in spoke 10.1.0.0/16 \u00b7 Kubernetes 1.31 \u00b7 Istio mTLS STRICT \u00b7 three availability zones",
    "PAGE 2 of 6  \u00b7  KUBERNETES",
    w=2000,
)


def node(x, y, w, label, chips, *, h=90, chip_w=185, chip_sem="compute",
         gap=None):
    """One VM in a node pool: a plain box holding pod chips."""
    s.rect(x, y, w, h, "ext", fill="#FFFFFF", stroke="#94A3B8", sw=2)
    s.text(label, x + 12, y + 8, w - 24, 11, color=SUBTLE, align="left")
    n = len(chips)
    if gap is None:
        gap = (w - 30 - n * chip_w) / max(1, n - 1) if n > 1 else 0
    for i, (ik, name) in enumerate(chips):
        cx = x + 15 + i * (chip_w + gap)
        s.card(cx, y + 30, chip_w, 38, ik, name, chip_sem,
               icon_size=20, title_size=11)


# ------------------------------------------------ control plane + ingress
s.zone(60, 190, 1620, 110,
       "Managed control plane + ingress \u2014 Microsoft-managed, no public API endpoint",
       "net")
cp = [
    ("aks", "Private API server", "private endpoint only"),
    ("managedid", "Workload identity", "federated OIDC, no secrets"),
    ("policy", "Azure Policy add-on", "Gatekeeper admission"),
    ("apim", "APIM ingress", "north-south, mTLS"),
    ("istio", "Istio ingress gateway", "east-west, mTLS STRICT"),
]
for i, (ik, t, sub) in enumerate(cp):
    s.card(80 + i * 312, 222, 290, 58, ik, t, "net", sub=sub)

# ------------------------------------------------ pool: system
s.zone(60, 400, 470, 440, "Node pool:  system", "ext", label_size=14)
s.text("3 x Standard_D4s_v5  \u00b7  zones 1 \u00b7 2 \u00b7 3\ntaint  CriticalAddonsOnly=true:NoSchedule",
       76, 414, 440, 11, color=BODY, align="left")
node(80, 462, 430, "aks-sys-1  \u00b7  zone 1",
     [("kubernetes", "coredns"), ("istio", "istiod")],
     chip_w=200, chip_sem="ext")
node(80, 566, 430, "aks-sys-2  \u00b7  zone 2",
     [("kubernetes", "metrics-server"), ("opa", "gatekeeper")],
     chip_w=200, chip_sem="ext")
node(80, 670, 430, "aks-sys-3  \u00b7  zone 3",
     [("keyvault", "csi-secrets"), ("argo", "argocd-repo")],
     chip_w=200, chip_sem="ext")
s.text("System add-ons only. The taint keeps application pods\noff these nodes, so a noisy workload can never starve\nCoreDNS or the Istio control plane.",
       80, 776, 440, 11, color=BODY, align="left")

# ------------------------------------------------ pool: general
s.zone(570, 400, 650, 440, "Node pool:  general", "compute", label_size=14)
s.text("3 to 12 x Standard_D8s_v5  \u00b7  zones 1 \u00b7 2 \u00b7 3  \u00b7  autoscaler + KEDA\nlabel  workload=general",
       586, 414, 620, 11, color=BODY, align="left")
node(590, 462, 610, "aks-gen-1  \u00b7  zone 1",
     [("python", "bff-service"), ("python", "payment-orch"),
      ("python", "qrph-service")])
node(590, 566, 610, "aks-gen-2  \u00b7  zone 2",
     [("python", "fraud-service"), ("python", "aml-service"),
      ("python", "account-svc")])
node(590, 670, 610, "aks-gen-3  \u00b7  zone 3",
     [("python", "order-service"), ("python", "inventory-svc"),
      ("python", "notification")])
s.text("Stateless domain services. Every pod carries an Istio sidecar,\nso pod-to-pod traffic is mTLS whether or not the app knows it.\nKEDA scales this pool on Service Bus queue depth.",
       590, 776, 620, 11, color=BODY, align="left")

# ------------------------------------------------ pool: confidential
s.zone(1260, 400, 420, 440, "Node pool:  confidential", "sec", label_size=14)
s.text("2 x Standard_DC4as_v5  (AMD SEV-SNP)  \u00b7  zones 1 \u00b7 2\ntaint  workload=ledger:NoSchedule",
       1276, 414, 400, 11, color=BODY, align="left")
node(1280, 462, 380, "aks-conf-1  \u00b7  zone 1",
     [("python", "ledger-service"), ("python", "audit-service")],
     chip_w=175, chip_sem="sec")
node(1280, 566, 380, "aks-conf-2  \u00b7  zone 2",
     [("python", "ledger (replica)"), ("python", "audit (replica)")],
     chip_w=175, chip_sem="sec")
s.text("Only the ledger and audit services tolerate this\ntaint, so nothing else can ever be scheduled here.\nMemory is encrypted by the CPU \u2014 the host OS and\nthe hypervisor cannot read it. The QR signing key\nstays inside Managed HSM and is never loaded\ninto a pod.\n\nGuest attestation is verified before a pod starts;\na node that fails attestation is removed from the\npool instead of receiving traffic.",
       1280, 670, 390, 11, color=BODY, align="left")

# ------------------------------------------------ add-ons band
s.zone(60, 930, 1620, 152, "Platform add-ons running in the cluster", "ops")
addons = [
    ("istio", "Istio\nmTLS STRICT"),
    ("cilium", "Cilium\neBPF netpol"),
    ("keda", "KEDA\nqueue autoscale"),
    ("argo", "Argo CD\nGitOps sync"),
    ("opa", "Gatekeeper\nadmission policy"),
    ("prometheus", "Prometheus\nmetrics + SLO"),
    ("helm", "Helm\npackaging"),
    ("dapr", "Dapr\nsaga workflow"),
]
for i, (ik, label) in enumerate(addons):
    s.stack(160 + i * 200, 962, ik, label, icon_size=34, w=190, size=11)

# ------------------------------------------------ enforcement column
s.zone(1720, 190, 340, 892, "How placement is actually enforced", "plain",
       label_size=14)

s.code(1735, 240, 310, [
    ("spec:", CODE_FG),
    ("  template:", CODE_FG),
    ("    spec:", CODE_FG),
    ("      nodeSelector:", CODE_FG),
    ("        workload: ledger", CODE_ACCENT),
    ("      tolerations:", CODE_FG),
    ("      - key: workload", CODE_ACCENT),
    ("        value: ledger", CODE_ACCENT),
    ("        effect: NoSchedule", CODE_ACCENT),
    ("      securityContext:", CODE_FG),
    ("        runAsNonRoot: true", CODE_ACCENT),
    ("        readOnlyRootFilesystem: true", CODE_ACCENT),
], title="ledger-service \u00b7 deployment.yaml")

s.code(1735, 468, 310, [
    ("triggers:", CODE_FG),
    ("- type: azure-servicebus", CODE_ACCENT),
    ("  metadata:", CODE_FG),
    ("    topicName: payments", CODE_ACCENT),
    ("    messageCount: \"50\"", CODE_ACCENT),
    ("  authenticationRef:", CODE_FG),
    ("    name: azure-wi-auth", CODE_ACCENT),
], title="KEDA \u00b7 scale on queue depth")

s.code(1735, 620, 310, [
    ("minAvailable: 2", CODE_ACCENT),
    ("topologySpreadConstraints:", CODE_FG),
    ("- maxSkew: 1", CODE_ACCENT),
    ("  topologyKey:", CODE_FG),
    ("    topology.kubernetes.io/zone", CODE_ACCENT),
    ("  whenUnsatisfiable:", CODE_FG),
    ("    DoNotSchedule", CODE_ACCENT),
], title="PDB + zone spread")

s.text("A pod with no toleration is rejected by the\nscheduler, not merely discouraged. Gatekeeper\nadditionally denies any pod that has no resource\nlimit, runs as root, or references an image that\nNotation did not sign.",
       1735, 776, 320, 11, color=BODY, align="left")

s.text("Grey chip = platform add-on \u00b7 blue = domain service\namber = confidential workload.\nUpgrades roll one node at a time and honour the PDB,\nso two replicas keep serving during an image upgrade.",
       1735, 856, 330, 11, color=BODY, align="left")

s.code(1735, 926, 310, [
    ("kind: CiliumNetworkPolicy", CODE_FG),
    ("endpointSelector:", CODE_FG),
    ("  matchLabels: {app: ledger}", CODE_ACCENT),
    ("ingress:", CODE_FG),
    ("- fromEndpoints:", CODE_FG),
    ("  - matchLabels:", CODE_FG),
    ("      app: payment-orchestrator", CODE_ACCENT),
    ("  toPorts: [{ports: [{port: \"8080\"}]}]", CODE_ACCENT),
], title="default-deny \u00b7 ledger reachable from one caller")

s.write("02-aks-nodes.excalidraw")
