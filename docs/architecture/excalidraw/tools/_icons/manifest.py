"""Curated icon manifest: logical key -> official Azure V24 icon filename.

Only real, official Microsoft Azure architecture icons (V24) plus CNCF/vendor
logos for non-Azure tools. No placeholders.
"""

# key -> exact filename inside the Azure_Public_Service_Icons tree
AZURE = {
    # ---- edge / network ----
    "frontdoor":    "10073-icon-service-Front-Door-and-CDN-Profiles.svg",
    "waf":          "10362-icon-service-Web-Application-Firewall-Policies(WAF).svg",
    "ddos":         "10072-icon-service-DDoS-Protection-Plans.svg",
    "firewall":     "10084-icon-service-Firewalls.svg",
    "vnet":         "10061-icon-service-Virtual-Networks.svg",
    "bastion":      "02422-icon-service-Bastions.svg",
    "expressroute": "10079-icon-service-ExpressRoute-Circuits.svg",
    "privatelink":  "00427-icon-service-Private-Link.svg",
    "dns":          "10064-icon-service-DNS-Zones.svg",
    "loadbalancer": "10062-icon-service-Load-Balancers.svg",
    "nsg":          "10067-icon-service-Network-Security-Groups.svg",
    "routetable":   "10082-icon-service-Route-Tables.svg",

    # ---- gateway / compute ----
    "apim":         "10042-icon-service-API-Management-Services.svg",
    "botservice":   "10165-icon-service-Bot-Services.svg",
    "logicapps":    "02631-icon-service-Logic-Apps.svg",
    "aks":          "10023-icon-service-Kubernetes-Services.svg",
    "acr":          "10105-icon-service-Container-Registries.svg",
    "vmss":         "10034-icon-service-VM-Scale-Sets.svg",
    "aci":          "10104-icon-service-Container-Instances.svg",
    "vm":           "10021-icon-service-Virtual-Machine.svg",

    # ---- data ----
    "postgres":     "10131-icon-service-Azure-Database-PostgreSQL-Server.svg",
    "mysql":        "10122-icon-service-Azure-Database-MySQL-Server.svg",
    "redis":        "10137-icon-service-Cache-Redis.svg",
    "servicebus":   "10836-icon-service-Azure-Service-Bus.svg",
    "eventhubs":    "00039-icon-service-Event-Hubs.svg",
    "storage":      "10086-icon-service-Storage-Accounts.svg",
    "ledger":       "02668-icon-service-Confidential-Ledgers.svg",
    "backupvault":  "02361-icon-service-Backup-Vault.svg",

    # ---- security / identity ----
    "keyvault":     "10245-icon-service-Key-Vaults.svg",
    "hsm":          "02322-icon-service-Dedicated-HSM.svg",
    "externalid":   "03425-icon-service-external-id.svg",
    "entraid":      "10230-icon-service-Users.svg",
    "managedid":    "10227-icon-service-Managed-Identities.svg",
    "defender":     "10241-icon-service-Microsoft-Defender-for-Cloud.svg",
    "sentinel":     "10248-icon-service-Azure-Sentinel.svg",
    "policy":       "10316-icon-service-Policy.svg",
    "compliance":   "00011-icon-service-Compliance.svg",

    # ---- management / governance ----
    "mgmtgroups":   "10011-icon-service-Management-Groups.svg",
    "subscription": "10002-icon-service-Subscriptions.svg",
    "resourcegroup":"10007-icon-service-Resource-Groups.svg",
    "monitor":      "00001-icon-service-Monitor.svg",
    "loganalytics": "00009-icon-service-Log-Analytics-Workspaces.svg",
    "appinsights":  "00012-icon-service-Application-Insights.svg",
    "grafana":      "02905-icon-service-Azure-Managed-Grafana.svg",
    "chaos":        "02223-icon-service-Azure-Chaos-Studio.svg",
    "devops":       "10261-icon-service-Azure-DevOps.svg",

    # ---- actors / clients ----
    "browser":      "10783-icon-service-Browser.svg",
    "clientapps":   "10331-icon-service-Client-Apps.svg",
    "devices":      "10332-icon-service-Devices.svg",
}

# simple-icons ship monochrome (black) paths -- give them their brand colour so
# they sit consistently beside the full-colour Azure and CNCF marks.
BRAND = {
    "github":     "#181717",
    "terraform":  "#844FBA",
    "postgresql": "#4169E1",
    "trivy":      "#1904DA",
    "python":     "#3776AB",
    "docker":     "#2496ED",
    "mysqllogo":  "#4479A1",
    # ---- target-architecture stack marks (page 6) ----
    "flask":           "#000000",
    "sonarqubeserver": "#4E9BCD",
    "flyway":          "#CC0200",
}

# key -> (url, filename) for non-Azure logos, fetched from official/CNCF sources
EXTERNAL = {
    "kubernetes": "https://raw.githubusercontent.com/cncf/artwork/master/projects/kubernetes/icon/color/kubernetes-icon-color.svg",
    "argo":       "https://raw.githubusercontent.com/cncf/artwork/master/projects/argo/icon/color/argo-icon-color.svg",
    "istio":      "https://raw.githubusercontent.com/cncf/artwork/master/projects/istio/icon/color/istio-icon-color.svg",
    "helm":       "https://raw.githubusercontent.com/cncf/artwork/master/projects/helm/icon/color/helm-icon-color.svg",
    "prometheus": "https://raw.githubusercontent.com/cncf/artwork/master/projects/prometheus/icon/color/prometheus-icon-color.svg",
    "opa":        "https://raw.githubusercontent.com/cncf/artwork/master/projects/open-policy-agent/icon/color/opa-icon-color.svg",
    "keda":       "https://raw.githubusercontent.com/cncf/artwork/master/projects/keda/icon/color/keda-icon-color.svg",
    "cilium":     "https://raw.githubusercontent.com/cncf/artwork/master/projects/cilium/icon/color/cilium_icon-color.svg",
    "dapr":       "https://raw.githubusercontent.com/cncf/artwork/master/projects/dapr/icon/color/dapr-icon-color.svg",
    "notary":     "https://raw.githubusercontent.com/cncf/artwork/master/projects/notary/icon/color/notary-project-icon-color.svg",
    "github":     "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/github.svg",
    "terraform":  "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/terraform.svg",
    "postgresql": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/postgresql.svg",
    "trivy":      "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/trivy.svg",
    "python":     "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/python.svg",
    "docker":     "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/docker.svg",
    "aws":        "https://raw.githubusercontent.com/devicons/devicon/master/icons/amazonwebservices/amazonwebservices-original-wordmark.svg",
    "jenkins":    "https://raw.githubusercontent.com/benc-uk/icon-collection/master/logos/jenkins.svg",
    "mysqllogo":  "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/mysql.svg",

    # ---- target-architecture stack marks (page 6, the tech stack) ----
    # The non-Azure tools named in the proposal paper's pipeline and workload.
    # simple-icons ships them monochrome; BRAND above restores each vendor's
    # documented colour so the row reads as one consistent set of flat logos
    # rather than a mix of drawing styles. Everything else on that page is an
    # official Azure V24 icon or a CNCF mark already listed above.
    "flask":           "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/flask.svg",
    "sonarqubeserver": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/sonarqubeserver.svg",
    "flyway":          "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/flyway.svg",
}
