# Consolidating a Two-Application Payment Prototype onto a Single Azure Platform

## A Proposal Paper on Cloud Consolidation, Database Engine Selection, and Network Segregation

**Subject system:** `jmbilbao25/Banking-App` — a QR-code payment prototype comprising a banking application and an e-commerce application
**Document type:** Proposal paper
**Version:** 1.1
**Status:** For review
**Date:** 11 August 2026 (all vendor documentation cited was accessed on this date)

---

## Executive Summary

This paper proposes the consolidation of two separately deployed Flask applications — a banking application and an e-commerce application — from three uncoordinated environments onto a single governed Microsoft Azure platform, and it resolves two questions that have blocked that consolidation.

**The first question is one of fact: do the two applications share a database?** They do not share a database, but they do share a database *server*, and the two answers have very different consequences. Each application owns a distinct logical database — `bankdb` and `ecomdb`. In local development each runs against its own MySQL 5.7 container on its own Docker network. In the Azure Container Instances deployment that is presently treated as production, both applications are pointed at **one shared Azure MySQL server**, using **one shared administrative credential that is committed to a public Git repository**. The isolation that exists in development does not exist in production. Section 4 documents this with file-level evidence.

**The second question is one of judgement: which database engine should the consolidated platform use?** Section 6 evaluates PostgreSQL, MySQL, and Azure SQL Database against seven declared, weighted criteria. **The result is a tie: MySQL 8.4 LTS and PostgreSQL both score 4.70 of 5.** Azure SQL is eliminated at 3.75.

The recommendation is nevertheless **Azure Database for PostgreSQL Flexible Server**, at **Moderate** confidence, and the reasoning is where the work is. The two candidates differ in essentially one criterion each: MySQL's entire advantage is migration cost, PostgreSQL's is auditability and version longevity. A migration cost is paid once; an audit obligation is discharged every day a supervised institution operates. That asymmetry is the tie-break, and it is a judgement rather than an arithmetic result — Section 6.5 shows PostgreSQL winning in only one of four weightings, and identifies the crossover point at which the recommendation reverses.

This also corrects the reasoning recorded in the repository's architecture notes, which justify PostgreSQL on the grounds of exact `NUMERIC` arithmetic and genuine `SELECT ... FOR UPDATE` semantics. Both are true of PostgreSQL and equally true of MySQL 8.x, so neither distinguishes them. The defects those claims were meant to address — money in floating-point columns, and an unserialised read-modify-write on balances — are application defects that survive any engine migration which does not also change the code.

**Recommended database topology:** two PostgreSQL Flexible Server instances, one per application, rather than one shared server hosting two databases. Section 7 sets out what that decision costs and what it buys.

The paper also proposes a target network topology — a hub-and-spoke virtual network with four spokes and no publicly reachable workload endpoint — which is presented as an accompanying diagram and summarised in Section 8.

Section 9 is deliberately adversarial. It records ten numbered findings that materially qualify the target design — plus six further open items in Section 9.10 — each verified against vendor documentation. Five of them identify parts of the previously documented design that are wrong as written, one of which is unbuildable. A proposal that suppressed these would not survive implementation.

---

## 1. Introduction

### 1.1 Background

The subject system is a functional prototype of a QR-code-initiated account-to-account payment flow. It comprises two independently deployed Python/Flask applications:

- a **banking application**, which authenticates a consumer, renders a payment confirmation page from a scanned QR code, and moves balances between a consumer account and a merchant account; and
- an **e-commerce application**, which maintains a product catalogue, creates orders, generates the payment QR code, and marks orders paid.

The two applications are coupled synchronously over plain HTTP. The banking application resolves the e-commerce application through an environment variable, `ECOM_CALLBACK_BASE`, and makes three outbound calls per payment: it fetches the order when rendering the confirmation page, fetches it again on submission, and posts a "paid" callback. Only after that callback returns does it adjust balances and write a transaction row.

The prototype demonstrates the intended user journey successfully. It was not, however, built to operate as a supervised payment service, and it is currently deployed in a way that would not withstand examination. Three environments exist in parallel, none of which is comparable to the others:

1. **two separate AWS EC2 hosts**, one per application (`3.83.82.3` for banking, `3.91.174.230` for e-commerce), each running Gunicorn published directly on port 80 with its own single-node MySQL 5.7 container, over plain HTTP on a public address. They must be separate hosts: both Compose files bind host port 80, so the two stacks cannot coexist. An nginx configuration exists in each application directory but is referenced by no Compose file, Dockerfile, or pipeline stage, so **nginx is not actually deployed** — and the configuration that exists proxies to ports 5001 and 5000 while the images serve on port 80, making it a third instance of the port mismatch recorded as P-5;
2. an **Azure Container Instances** deployment in the `centralindia` region, which is treated as production, in which both applications are configured against a single Azure MySQL server, reached by public hostname; and
3. a **Jenkins** pipeline that builds and pushes two tags (a commit SHA and `:latest`), unsigned and unscanned. Deployment to EC2 does not copy the image: the pipeline connects over SSH with host-key checking disabled and makes the host `git clone` or `git pull` from GitHub **at deploy time**, then `docker compose pull` the `:latest` tag. The running configuration is therefore whatever is on `main` at that instant rather than the artefact that was built and tested — a reproducibility defect distinct from, and worse than, the tag mutability. Deployment to Azure pins the SHA but deletes and recreates the container groups, so every release incurs an outage.

### 1.2 Rationale for consolidation

Consolidation is proposed for four reasons.

**Fragmentation is the root cause of the security posture, not a side effect of it.** Credentials are hardcoded in the pipeline because there is no shared secret store. The database has a public endpoint because there is no shared private network. Releases cause outages because there is no shared orchestrator. These are not independent defects; they are what happens when three environments are assembled separately under time pressure. A single platform with one identity provider, one network boundary, one secret store, and one deployment path removes the conditions that produced them.

**The regulatory position requires a defensible boundary.** A payment service operating in the Philippines falls within the supervisory perimeter of the Bangko Sentral ng Pilipinas. The controls that a supervised institution is expected to evidence — segregation of duties, privileged access management, network segmentation, immutable audit records, tested recovery, and a documented exit strategy — are properties of a platform. They cannot be evidenced for a system whose components are distributed across two public clouds and a public container registry.

**Supplier count and concentration risk pull in opposite directions, and both should be stated.** The estate today depends on AWS, Azure, Docker Hub, GitHub (which is in the deploy path at run time, per Section 1.1) and Jenkins. Consolidating reduces the number of independent third parties whose failure or compromise would affect a release. It simultaneously **raises** dependence on a single cloud provider to effectively total, which is the concentration risk a supervisor expects to see justified rather than reduced. These are different risks and consolidation trades one for the other; the trade is only acceptable because the exit strategy is credible, which is why engine portability carries its own criterion in Section 6 and why Azure SQL is eliminated there. Consolidation is not claimed here as a reduction in concentration risk.

**Cost and operability are presently unmeasurable.** Spend is spread across two providers with no tagging, no budgets, and no shared observability. Neither the run rate nor the failure modes of the current estate can be stated with confidence.

### 1.3 What this paper contributes

This paper does four things that the existing repository documentation does not:

1. it establishes, from the source code and deployment manifests, the factual position on database ownership and separation (Section 4);
2. it evaluates the database engine decision explicitly, with declared criteria and weights, and corrects the reasoning previously offered for it (Section 6);
3. it treats the one-server-versus-two-servers question as a decision in its own right, with a cost consequence (Section 7); and
4. it records the technical findings that qualify the target design, including those that invalidate parts of it (Section 9).

---

## 2. Statement of the Problem

### 2.1 General problem statement

The system is deployed across three uncoordinated environments with no common identity, network, secret-management, or release boundary. In consequence it cannot demonstrate the control environment expected of a payment service under BSP supervision, it cannot be operated or recovered predictably, and its data-tier separation is asserted in configuration rather than enforced by the platform.

### 2.2 Specific problems

The problems below are grouped by the layer at which they must be resolved, and each is traceable to a specific artefact in the repository. Where a claim is an inference from an artefact rather than a reading of it, the evidence column says so.

Severity is assigned by this paper on the following scale, which is **not** identical to the one used in `critical-findings.md` (that document uses CVSS-style reasoning). Three ratings are deliberately higher here than there, and the departures are listed so the two documents can be reconciled: D-2 (credential in public history) is Critical here against High there; D-5 (silent SQLite fallback) is High here against Medium there; P-2 and P-3 are High here against Medium there.

| Severity | Definition |
|----------|------------|
| **Critical** | Permits unauthorised movement of funds, unauthorised access to funds data, or undetected loss of funds data. |
| **High** | Permits privilege escalation or data divergence, or leaves the system unable to evidence a control a supervised institution must evidence. |
| **Medium** | Degrades operability, recoverability, or maintainability without directly exposing funds or funds data. |

#### 2.2.1 Data-tier problems

| ID | Problem | Evidence | Severity |
|----|---------|----------|----------|
| D-1 | Both applications are configured against a single shared Azure MySQL server **using the same server-administrator login**, so a compromise of the e-commerce application yields administrative access to banking data. The shared host alone would not do this; the shared login does. | Both `Jenkinsfile`s pass an identical `DB_HOST` and `DB_USER`, differing only in `DB_NAME` | Critical |
| D-2 | A live database hostname, administrative username, and password are committed to a public repository and passed as non-secure container environment variables, readable by anyone who can describe the container group. | Both `Jenkinsfile`s | Critical |
| D-3 | Monetary amounts are stored as double-precision floating point, so ledger totals are not guaranteed to reconcile. | `banking-app/models.py` — `db.Column(db.Float)` | High |
| D-4 | `order_id` carries no unique constraint and balance updates are not serialised, permitting a double-spend under concurrency. | `banking-app/models.py`, `banking-app/app.py` | High |
| D-5 | If the database host fails to resolve, the application silently falls back to a local SQLite file and continues to accept payments, converting a detectable outage into undetectable data divergence. **An attempt to disable this in production does not work:** both pipelines pass `USE_SQLITE=""`, and the empty string is falsy in Python, so `if not use_sqlite:` is true and the fallback remains armed. Someone tried to switch this off and the code ignored them. | `banking-app/app.py`, `ecommerce-app/app.py`, both `Jenkinsfile`s | High |
| D-6 | MySQL 5.7 reached community end-of-life in October 2023 and is no longer receiving community security fixes. | `docker-compose.bank.yml`, `docker-compose.ecom.yml` — `image: mysql:5.7` | High |

#### 2.2.2 Platform and network problems

| ID | Problem | Evidence | Severity |
|----|---------|----------|----------|
| P-1 | The database server is reachable over the public internet. **This is an inference, not a reading:** the container groups are created with no virtual-network integration and connect by public hostname, from which public network access must be enabled. The server's firewall configuration was not inspected, as no running environment was accessed. | Inferred from both `Jenkinsfile`s (`az container create` with no VNet arguments, `DB_HOST` a public FQDN) | Critical |
| P-2 | The payment service is exposed directly to the internet by a load balancer with a public address, with no web application firewall and no rate limiting. | `banking-app/k8s/service.yaml` — `type: LoadBalancer` | High |
| P-3 | Kubernetes secrets are stored as plaintext `stringData` in a manifest in the repository. The committed values are placeholders (`securepassword`, `mysql-managed-service.url`), so no live credential is exposed by this file — but the pattern is established, and D-2 shows the same team committing a real one. | `banking-app/k8s/secret.yaml` | High |
| P-4 | Containers run as root; the non-root user directive is present but commented out. | both `Dockerfile`s | Medium |
| P-5 | The manifests target port 5001 while the container image serves on port 80, so the deployment could not pass its own health probes. | `Dockerfile` vs `k8s/deployment.yaml` | Medium |
| P-6 | Release replaces container groups by deletion, so every deployment causes an outage. | both `Jenkinsfile`s | Medium |
| P-7 | The two container instances per application provide **no availability benefit**. Each is created with its own `--dns-name-label ${instance}`, and there is no load balancer, Traffic Manager profile, or Front Door in front of them, so the two hostnames are independent single points of failure rather than replicas. The redundancy is nominal, which makes P-6's outage worse than it appears. | both `Jenkinsfile`s | High |
| P-8 | There is no centralised logging, metrics, or tracing. Diagnostics are predominantly `print()` to container stdout, with isolated use of `app.logger` in the e-commerce application; nothing is aggregated, retained, or queryable. | `banking-app/app.py`, `ecommerce-app/app.py` | Medium |

#### 2.2.3 Application-correctness problems

These are recorded because they bound what consolidation can achieve. Migrating this system unchanged would migrate these defects intact.

| ID | Problem | Evidence | Severity |
|----|---------|----------|----------|
| A-1 | The "mark order paid" endpoint is unauthenticated, so any caller can mark paid any order that is currently pending and unexpired. | `ecommerce-app/app.py` — `POST /api/orders/<id>/paid`, no authentication check | Critical |
| A-2 | The payment amount is taken from a client-submitted form field and never reconciled against the order total. | `banking-app/app.py` — `float(data.get('amount', 0))` | Critical |
| A-3 | The QR payload is an unsigned URL whose amount and merchant parameters can be edited before scanning. Unknown merchants fall back to a default rather than being rejected. | `ecommerce-app/app.py` (QR construction); `banking-app/app.py` (merchant fallback) | Critical |
| A-4 | The "paid" callback is issued *before* balances are debited, so a failure between the two leaves an order irreversibly marked paid with no funds moved and no compensating action. | `banking-app/app.py` — `requests.post(callback_url)` precedes `consumer.balance -= amount` | Critical |
| A-5 | Passwords are stored in plaintext and compared with `==`, in both applications. | `banking-app/models.py`, `banking-app/seed.py`, `ecommerce-app/models.py` — `password = db.Column(db.String(100))` | High |
| A-6 | The Flask session signing key is hardcoded in a public repository, permitting forgery of a session for a seeded account that carries the administrator flag, which grants access to a balance-crediting endpoint. | `banking-app/app.py` — `app.secret_key = 'super-secret-bank-key-for-prototype-only'`; `seed.py` — `alice-consumer ... is_admin=True`; `/admin/add_funds` | High |

**Two distinct attack chains, which should not be conflated.** The first needs no authentication at all: call `POST /api/orders/<id>/paid` directly and the order is marked paid with no funds moved (A-1 chaining into A-4). The second requires a bank session, because `/pay` redirects to login without one — but that session can be forged from the published signing key (A-6), after which the QR amount can be altered (A-3) and the debit taken for an arbitrary sum (A-2).

A third chain is created by D-5 and is the most alarming of the three: if the fallback engages, the application seeds a fresh SQLite database containing `alice-consumer` with the administrator flag, a positive balance, and the published default password — on an internet-facing endpoint.

### 2.3 The specific question this paper was asked to resolve

> *Which application uses which database, and do they share one?*

The question deserves its own treatment for three reasons. It has a different answer in development than in production, which is why informal answers conflict. The production answer is itself a Critical finding. And the answer determines the target topology, because a design cannot be said to isolate two trust zones while both zones authenticate to the same database server with the same credential.

Section 4 answers it from primary evidence.

### 2.4 Research questions

1. What is the factual state of database ownership, separation, and credential handling across the current environments?
2. Which database engine best serves a consolidated, BSP-supervised payment platform, and by what declared criteria?
3. Should the consolidated platform run one database server or one per application?
4. What target network topology satisfies the segregation and examination requirements, and what does it cost?
5. Which parts of the previously documented target design do not survive technical verification?

---

## 3. Scope and Delimitation

### 3.1 In scope

1. **Assessment of the current state** of both applications, their databases, container definitions, deployment manifests, and CI/CD pipelines, from the repository as the primary source.
2. **Database engine evaluation** — PostgreSQL, MySQL, and Azure SQL Database — against declared, weighted criteria, with a stated recommendation and confidence level.
3. **Database topology decision** — shared server versus dedicated server per application — including its cost consequence.
4. **Target network topology** — a hub-and-spoke virtual network with the region, address plan, segmentation model, and ingress and egress paths, delivered as an accompanying diagram.
5. **Data residency position** for a Philippine institution processing in a foreign Azure region, and the consequences that follow.
6. **Migration sequencing**, expressed as phases with explicit dependencies.
7. **Technical verification** of the target design against current vendor documentation, including findings that contradict it.

### 3.2 Out of scope

1. **Remediation of the application-correctness defects.** Problems A-1 to A-6 are recorded, and Section 10 sequences them, but their design is a separate body of work. This paper covers the platform they will run on.
2. **Core banking system selection or modification.** The core is treated as an external system of record reached over a private circuit.
3. **Infrastructure-as-code implementation.** Module structure is indicated; no Terraform or Bicep is delivered.
4. **Formal cost quotation.** Figures are indicative, at list price, and require confirmation against the Azure pricing calculator for the target region and reservation terms.
5. **Load and penetration testing.** Targets are stated; no test has been executed, so no target in this paper is evidenced by measurement.
6. **QR Ph interoperability implementation.** The current QR payload encodes an arbitrary HTTP URL and is not an EMVCo-based QR Ph payload. Achieving interoperability is noted as a prerequisite for licensed operation and is not designed here.
7. **Front-end and user-experience work.**

### 3.3 Delimitations and assumptions

**Delimitations.**

1. All findings derive from static reading of the repository at a single commit. No running environment was accessed, no database was queried, and no traffic was observed. Where behaviour is inferred from code rather than observed, the text says so.
2. The regulatory mapping is an engineering-side interpretation. It is not a legal opinion. Circular numbers, amendment status, and notification thresholds must be confirmed with the institution's compliance function; Section 9 records this as an open item rather than a closed one.
3. Cost figures cover the services drawn in the accompanying diagram. Section 9.9 identifies significant omissions in the previously published figure and gives a corrected range.
4. Performance and availability targets are design intents, not measurements.

**Assumptions.**

1. The institution has, or can obtain, an Azure Enterprise Agreement with the management-group hierarchy required for a landing zone.
2. A private circuit to a Philippine facility housing the core banking system can be provisioned.
3. Azure offers no Philippine region as at the date of this paper; Southeast Asia (Singapore) is the nearest region with three availability zones.
4. The credential identified in D-2 will be treated as compromised, rotated, and purged from Git history before any migration work begins.

---

## 4. Findings: The Database Question Answered

This section answers Section 2.3 from primary evidence. It is placed before the engine evaluation because the engine decision depends on it.

### 4.1 There are two applications, not one

The repository root contains two sibling application directories, `banking-app/` and `ecommerce-app/`, each with its own `app.py`, `models.py`, `Dockerfile`, `Jenkinsfile`, Compose file, Kubernetes manifests, templates, and static assets. The e-commerce application is easy to miss because the repository's top-level README describes a single Compose file and a single nginx configuration at the root; neither exists. The actual Compose files are per-application. Running `docker compose up` from the repository root, as the README instructs, does not work.

### 4.2 Each application owns a distinct logical database

Both applications construct their connection string from environment variables with per-application defaults.

**Banking application** (`banking-app/app.py`):

```python
db_user = os.environ.get('DB_USER', 'bankuser')
db_password = os.environ.get('DB_PASSWORD', 'devpass')
db_host = os.environ.get('DB_HOST', 'mysql')
db_name = os.environ.get('DB_NAME', 'bankdb')
...
if use_sqlite:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///banking.db"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
```

The `else` branch is retained in the quotation deliberately: the MySQL URI is **conditional**, and dropping the guard would understate the finding in Section 4.5.

**E-commerce application** (`ecommerce-app/app.py`) — the same construction, with different defaults:

```python
db_user = os.environ.get('DB_USER', 'ecomuser')
db_host = os.environ.get('DB_HOST', 'mysql')
db_name = os.environ.get('DB_NAME', 'ecomdb')
```

So: `bankdb` belongs to the banking application and holds two tables, `accounts` and `transactions`. `ecomdb` belongs to the e-commerce application and holds four: `users`, `products`, `orders`, and `order_items` — stock is a column on `products`, not a table. **The two logical databases are distinct, and neither application is written to read the other's.**

Two properties of `ecomdb` matter later and are recorded here. It holds a `users` table storing customer usernames and **plaintext passwords** (A-5), which makes any cross-border copy of it a personal-data question under Section 8.4 and not merely a commercial one. And it carries four of the six floating-point money columns in the system (`products.price`, `orders.total_amount`, `order_items.price`, `order_items.subtotal`), so D-3 is not confined to the banking application. Both use MySQL through the `PyMySQL` driver. There is no PostgreSQL anywhere in the codebase; `requirements.txt` lists `PyMySQL==1.1.0` and no PostgreSQL driver. PostgreSQL exists in this repository only as a recommendation in the architecture notes.

### 4.3 In development the two databases are on two separate servers

`banking-app/docker-compose.bank.yml` defines a `mysql:5.7` service named `mysql`, container name `bank-mysql`, on a bridge network `bank-net`, with volume `bank_mysql_data`. `ecommerce-app/docker-compose.ecom.yml` mirrors it structurally: a `mysql:5.7` service also named `mysql`, but with container name `ecom-mysql`, on `ecom-net`, with volume `ecom_mysql_data`. The application service is named `ecommerce` rather than `banking`, and the cross-application environment variable is reversed (`BANK_PUBLIC_BASE` pointing at a hardcoded `3.83.82.3`, against the banking file's `ECOM_CALLBACK_BASE` pointing at `3.91.174.230`). Both files publish host port 80, which is why the two stacks cannot share a host.

Because each Compose service is named `mysql` inside its own network, the identical setting `DB_HOST=mysql` resolves to a **different server in each stack**. Locally, therefore: two logical databases, two physical servers, two networks, two volumes. This is a reasonable separation, and it is the source of the widespread but incorrect belief that the deployed system is separated the same way.

### 4.4 In the deployed environment both databases are on one shared server

Both `Jenkinsfile`s deploy to Azure Container Instances with an identical host, an identical administrative login, and an identical password, differing **only** in the database name:

```groovy
# banking-app/Jenkinsfile
--environment-variables DB_HOST=testestste.mysql.database.azure.com \
    DB_USER=jmbilbao25 DB_PASSWORD='@dreamCS2025' DB_NAME=bankdb USE_SQLITE="" \

# ecommerce-app/Jenkinsfile
--environment-variables DB_HOST=testestste.mysql.database.azure.com \
    DB_USER=jmbilbao25 DB_PASSWORD='@dreamCS2025' DB_NAME=ecomdb USE_SQLITE="" \
```

Four observations follow, in ascending order of seriousness.

1. **The separation present in development is absent in deployment.** Both applications authenticate to one Azure MySQL server. The boundary between them is a `DB_NAME` string, not a network boundary, not a server boundary, and not an identity boundary.
2. **Both applications use the same login**, which is the server administrator. Neither is restricted to its own schema. A SQL-injection defect or a compromised container in the e-commerce application yields administrative access to `bankdb`.
3. **The credential is in a public Git repository**, and it is passed via `--environment-variables` rather than `--secure-environment-variables`, so it is also recoverable from the container group's metadata by anyone with read access to the subscription. It must be treated as compromised, rotated, and purged from history — including from the pipeline logs of every prior build.
4. **`USE_SQLITE=""` is a failed attempt to disable the fallback described in Section 4.5.** The empty string is falsy in Python, so `if not use_sqlite:` evaluates true and the DNS-probe fallback stays armed. Someone recognised the hazard, tried to switch it off in production, and the code silently ignored them. A control that appears to be configured and is not is worse than one that was never attempted, because it removes the incentive to look again.

### 4.5 A third possibility: no server at all

Both applications resolve the database host before connecting, and fall back to SQLite if resolution fails:

```python
use_sqlite = os.environ.get('USE_SQLITE')
if not use_sqlite:
    try:
        socket.gethostbyname(db_host)
    except socket.error:
        print(f"Warning: Could not resolve DB_HOST '{db_host}'. Falling back to SQLite.")
        use_sqlite = True
```

In a container that cannot resolve its database, the application starts successfully, creates a local SQLite file, seeds it, and accepts payments into storage that is destroyed when the container is replaced. The failure is announced only by a line on stdout. Under the ACI deployment model, where container groups are deleted and recreated on every release, this converts a transient DNS failure into silent and unrecoverable divergence between what customers were told and what was recorded. Of all the findings in this paper this is the one most likely to cause loss without anyone noticing.

### 4.6 Summary of the answer

| Question | Answer |
|----------|--------|
| Is there one application or two? | Two: a banking application and an e-commerce application. |
| Do they use the same database engine? | Yes — MySQL, via PyMySQL, with no PostgreSQL driver present. Version 5.7 is evidenced for the development containers (`image: mysql:5.7`); the deployed Azure server's version is not stated anywhere in the repository and was not inspected. |
| Do they use the same *database*? | No. `bankdb` and `ecomdb` are distinct, and neither application reads the other's. |
| Do they use the same *server*? | **In development, no** — two separate MySQL containers. **In deployment, yes** — one shared Azure MySQL server, one shared administrative credential. |
| Is the separation enforced? | No. In deployment it rests on a database-name string, using a login with administrative rights over both. |
| Could either run without a server at all? | Yes. Both silently fall back to local SQLite if the host does not resolve. |

**The single most important consequence:** the statement "the banking and shopping data are separate" is true of the code and false of the deployment. The consolidation proposed here makes it true of both, by separating the two at the network layer, the server layer, the identity layer, and the encryption-key layer, so that separation becomes a property the platform enforces rather than a convention the configuration expresses.

---

## 5. Methodology

### 5.1 Approach

The work followed five stages.

**Stage 1 — Evidence gathering.** Static review of the repository: both applications' source, models, seed logic, Compose files, Dockerfiles, Kubernetes manifests, Jenkins pipelines, and existing architecture notes. Every factual claim in Sections 1, 2, and 4 cites the artefact it derives from. No running environment was accessed.

**Stage 2 — Structured technology evaluation.** The engine decision was made by weighted-criteria scoring rather than narrative preference: criteria and weights were declared *before* scoring, each option scored 1–5 per criterion with a written justification, and the weighted total computed. Declaring weights first is what prevents the conclusion from selecting its own criteria. The method also requires recording the confidence level and the conditions under which the recommendation would change (Sections 6.4 and 6.5).

**Stage 3 — Diagram revision for comprehension.** The existing network topology diagram was rebuilt against a stated audience — a review panel and institutional IT managers who are not Azure specialists — using three rules: a single numbered path through the request flow; plain-language labels with product names secondary; and everything off the request path moved into a separately headed column. Section 8.3 records the specific changes and why each was made.

**Stage 4 — Adversarial review.** Rather than self-review, the diagram and the design were reviewed from hostile perspectives with a standing instruction that finding no defect constitutes a failed review. Two independent passes were run: a design critique scoring comprehensibility against the previous version, and a technical critique in the posture of a cloud architect deciding whether the landing zone would be approved. The technical pass produced the findings in Section 9, several of which contradict the design it was reviewing.

**Stage 5 — Verification.** Every load-bearing technical claim arising from Stage 4 was checked against vendor documentation, accessed on the date on the title page, before being admitted to this paper. Seven findings carry a "verified" status in Section 9 and are cited in Section 12.2. Verification also cut the other way: it overturned two of this paper's own earlier scores in Section 6.3, and the correction erased the margin the earlier draft reported. Claims that could not be verified are marked open rather than asserted.

Because Section 9 turns entirely on retirement and support dates, **it has a shelf life**. Every finding there should be re-checked against vendor documentation before the paper is relied upon more than a few months after the date on the title page.

### 5.2 Evaluation criteria and weights

Criteria were derived from the problem statement, not from the candidate engines' feature lists. Weights reflect the consequence of getting each criterion wrong in a payment system under supervision.

| # | Criterion | Weight | Why this weight |
|---|-----------|--------|-----------------|
| C1 | Correctness controls for money and concurrency | 20% | Highest weight: failure means funds moved incorrectly. Covers exact decimal arithmetic, row-level locking, isolation levels, and constraint enforcement. |
| C2 | Auditability for examination | 15% | The institution must produce a defensible record of who did what to funds data. Statement-level audit capability is a platform property. |
| C3 | Azure managed-service posture | 15% | Private endpoint or injection, customer-managed keys, zone-redundant HA, Entra authentication, point-in-time restore. Determines whether the network design in Section 8 is achievable. |
| C4 | Version longevity | 15% | Each forced major migration is a project with an outage risk. The current estate is already stranded on an end-of-life version. |
| C5 | Migration cost from the present codebase | 15% | Real and immediate: driver, dialect, schema conversion, and test rework. |
| C6 | Portability and exit strategy | 10% | The supervisor expects a documented, credible exit from a material outsourcing arrangement. Engine portability is a substantial part of that. |
| C7 | Run cost | 10% | Material but the smallest weight: the difference between candidates is a small fraction of total platform cost. |

### 5.3 Limitations of the method

1. Static review cannot find defects that appear only under load or only in the deployed configuration. Section 4.5's conclusion about SQLite divergence is inferred from code, not observed.
2. Scoring is expert judgement. The weights are declared so that a reader who disagrees can substitute their own; Section 6.5 tests how much the weights actually matter.
3. Cost figures are indicative list prices, not quotations.
4. Verification confirms that a vendor documents a behaviour. It does not confirm the behaviour in the institution's tenant, at its scale.

---

## 6. Evaluation: PostgreSQL versus MySQL versus Azure SQL

### 6.1 Candidates

| Option | Service | Basis for inclusion |
|--------|---------|--------------|
| **A** | Azure Database for **MySQL** Flexible Server (current supported major version) | Incumbent engine. Lowest-friction path: the applications already speak MySQL. |
| **B** | Azure Database for **PostgreSQL** Flexible Server | Recommended by the repository's existing architecture notes. |
| **C** | **Azure SQL Database** | Azure's first-party relational engine, with capabilities relevant to audit integrity. |

Excluded without scoring: self-managed engines on virtual machines (transfers patching, backup, and HA to the institution for no benefit); MariaDB on Azure (the managed service has been retired); and non-relational stores (the workload is a double-entry ledger with strong integrity requirements).

### 6.2 Correcting the reasoning previously recorded

The repository's architecture notes justify PostgreSQL as follows:

> *PostgreSQL gives exact `NUMERIC`, real `SELECT ... FOR UPDATE` semantics, transactional DDL, `pgAudit`, and logical replication for the outbox relay.*

Two of those five reasons do not survive examination, and it matters that a proposal says so.

**"Exact `NUMERIC`" does not differentiate.** MySQL's `DECIMAL` is a fixed-point exact type, as is SQL Server's. The actual defect (D-3) is that the application declares money as `db.Column(db.Float)`, which maps to double-precision floating point on *every* engine. Migrating to PostgreSQL while leaving that declaration unchanged reproduces the defect exactly. The fix is `NUMERIC(19,4)` — or `DECIMAL(19,4)` — in the model, and it is required regardless of which engine is chosen.

**"Real `SELECT ... FOR UPDATE`" does not differentiate either.** InnoDB has supported `SELECT ... FOR UPDATE` for many years, and MySQL 8.0 added `SKIP LOCKED` and `NOWAIT`. What the prototype lacks is not an engine capability but *any* locking: it reads a balance, computes a new one, and writes it back without a lock, a version check, or a unique constraint on `order_id` (D-4). That is an application defect on any engine.

There is a narrower, defensible version of the argument. MySQL's default configuration historically coerced invalid values toward the nearest valid value rather than rejecting them, and strict behaviour depends on server SQL mode; PostgreSQL rejects such values outright. A platform that fails loudly on bad data is preferable for a ledger. That is a real difference, but it is a difference of degree, and it is not what the notes claimed.

The three remaining reasons — transactional DDL, `pgAudit`, and logical replication — do hold, and they are joined by two the notes omitted: version longevity and portability. Those five carry the recommendation.

### 6.3 Scored comparison

Scores are 1 (poor) to 5 (excellent). Candidate A is evaluated as **MySQL 8.4 LTS**, because Section 6.1 defines the option as the current supported major version and 8.4 is the current long-term-support release, generally available on Flexible Server. Scoring 8.0 would penalise the option for a version nobody would now choose.

| Criterion | Weight | A: MySQL 8.4 | B: PostgreSQL | C: Azure SQL |
|-----------|--------|:------------:|:-------------:|:------------:|
| C1 Correctness controls | 20% | 5 | 5 | 5 |
| C2 Auditability | 15% | 4 | 5 | 5 |
| C3 Azure managed posture | 15% | 5 | 5 | 4 |
| C4 Version longevity | 15% | 4 | 5 | 5 |
| C5 Migration cost from present code | 15% | 5 | 3 | 1 |
| C6 Portability and exit | 10% | 5 | 5 | 3 |
| C7 Run cost | 10% | 5 | 5 | 2 |
| **Weighted total** | **100%** | **4.70** | **4.70** | **3.75** |

**C1 — Correctness controls: 5 / 5 / 5, and this is a finding in itself.** Section 6.2 disposed of the two arguments usually offered here, and once they are gone nothing is left with which to separate the engines. All three provide exact fixed-point decimal types. All three provide row-level locking; MySQL has had `SELECT ... FOR UPDATE` for years and gained `SKIP LOCKED` and `NOWAIT` in 8.0.1. All three enforce `CHECK` constraints — MySQL from 8.0.16, which is four years behind the version being scored. All three offer a serialisable isolation level. **The highest-weighted criterion in this evaluation does not discriminate between the candidates.** An earlier draft of this paper scored MySQL 4 here on the grounds that its `SERIALIZABLE` is implemented by promoting plain reads to locking reads. That deduction has been withdrawn: two-phase locking is the textbook-correct means of achieving serialisability and is more conservative than the optimistic alternative, so describing the mechanism does not establish a deficiency.

**C2 — Auditability: 4 / 5 / 5.** PostgreSQL's `pgAudit` classifies audit records by statement category, which maps directly onto the question an examiner asks ("show me every statement that altered funds data"). Azure Database for MySQL's audit log classifies by event class instead, and the class broad enough to capture the equivalent detail is impractically verbose at payment volumes. That is a real but narrow difference, and it is scored as one point rather than two. Azure SQL scores 5, and its ledger tables provide cryptographically verifiable history in addition. **A caveat that cuts against PostgreSQL:** `pgAudit` writes to the server log. It is a logging feature, not a tamper-evident store, so it does not by itself satisfy the immutable-audit requirement in Section 8.4 — that requirement is met by the archive, not by the database.

**C3 — Azure managed posture: 5 / 5 / 4.** Section 5.2 defines this criterion as "private endpoint **or** injection". Both MySQL and PostgreSQL Flexible Server can be injected into a delegated subnet inside a spoke; Azure SQL Database offers private endpoints only. Azure SQL therefore scores 4 on the criterion's own wording. All three provide customer-managed keys, zone-redundant high availability, point-in-time restore, and Microsoft Entra authentication. An earlier draft deducted a point from MySQL here on the basis of logical decoding versus binary-log capture; that argument has been removed, because it is an argument about change-data-capture architecture rather than managed-service posture, and it was already being counted in Section 6.2.

**C4 — Version longevity: 4 / 5 / 5.** This criterion was scored wrongly in an earlier draft, and the correction matters more than any other single change in this section. MySQL 8.4 is a long-term-support release: Oracle's lifetime support policy gives an LTS series five years of premier support and three of extended support, placing 8.4 at roughly April 2029 and April 2032 respectively. It is generally available on Azure Database for MySQL Flexible Server. So the claim in the earlier draft — that choosing MySQL means committing to a second major migration shortly after the first — is false. MySQL is marked down one point only because the 5.7 to 8.4 hop is compulsory now, and because moving between MySQL majors is a migration rather than an in-place upgrade. PostgreSQL scores 5 for a predictable annual major with five years of support each and a supported in-place major upgrade path. Azure SQL scores 5 for having no customer-managed version at all.

**C5 — Migration cost: 5 / 3 / 1.** MySQL's advantage, and the largest single differentiator in the table. Remaining on MySQL is a version upgrade: driver, dialect, and SQL are unchanged. PostgreSQL requires a driver change (`PyMySQL` to `psycopg`), a dialect change, schema conversion, and a data migration — scored 3 rather than lower because SQLAlchemy absorbs most of the application-level difference and the schemas are small (two tables in banking; four in e-commerce). Azure SQL scores 1: a different SQL dialect, different identity and type semantics, a different driver and ODBC layer, and no team experience.

**C6 — Portability and exit: 5 / 5 / 3.** Both open-source engines run unchanged on any cloud and on premises, so an exit is a restore rather than a rewrite. Azure SQL scores 3, not 1: the SQL Server engine runs on-premises, in containers, on other clouds' managed offerings, and on Azure SQL Managed Instance, so an exit is bounded work rather than an engine change. It is still the weakest of the three, because the Database-tier surface is not fully portable and the nearest destinations remain Microsoft products.

**C7 — Run cost: 5 / 5 / 2.** At equivalent compute, storage, and high-availability configuration, MySQL and PostgreSQL Flexible Server are priced closely enough that inventing a difference between them would be false precision. Azure SQL is materially more expensive at comparable capability.

### 6.4 The matrix does not decide it

**The baseline result is a tie: MySQL 8.4 and PostgreSQL both score 4.70.** Azure SQL is eliminated at 3.75.

This is the honest output of the declared method, and it is a more useful result than the one an earlier draft reported. That draft returned PostgreSQL 4.60 against MySQL 3.80 and called it "a clear result rather than a close call, Confidence: High". Two of the scores producing that margin were wrong — C1 penalised MySQL for a `CHECK` constraint limitation that the scored version does not have, and C4 penalised it for an end-of-life horizon that MySQL 8.4 LTS does not have. Correcting both erases the margin entirely.

So the recommendation cannot be read off the total. It has to be argued, and the shape of the tie tells us how.

**Where the two candidates differ is almost entirely in one criterion each.** MySQL's whole advantage is C5, migration cost. PostgreSQL's whole advantage is C2 and C4, auditability and version longevity. Everything else is level. The question is therefore not "which engine is better" but **"which kind of advantage is worth more to a supervised institution over the life of the system?"**

Put that way it answers itself. **A migration cost is paid once. An audit obligation is discharged every day the service operates, and an examination can be called at any point in that period.** MySQL's advantage is a one-off saving in a project that is already committed to a compulsory 5.7 migration; PostgreSQL's advantage recurs for as long as the institution is supervised. The same asymmetry applies to C4: MySQL's LTS horizon is genuinely long, but PostgreSQL's in-place upgrade path means the institution never again faces a cross-major data migration on a live ledger, which is the specific operation this system is least equipped to survive.

**Recommendation: adopt Azure Database for PostgreSQL Flexible Server. Confidence: Moderate.**

Moderate, not High, and the downgrade is deliberate. The engines tie on the declared criteria; the recommendation rests on a judgement about the relative durability of two kinds of advantage, and a reader who weights delivery risk more heavily than examination readiness will reach the opposite conclusion and will not be making an error. Section 6.5 identifies exactly where that crossover lies.

**The reasons that survive, stated so they can be challenged:**

1. **Auditability is a perpetual obligation, migration cost is a one-off.** This is the tie-break, and it is the whole argument.
2. **Transactional DDL.** Schema change is where regulated systems break. A multi-statement migration that either fully applies or fully rolls back is a materially better property for a ledger than MySQL's per-statement atomic DDL with an implicit commit at each boundary. Two honest qualifications: this does not distinguish PostgreSQL from Azure SQL, which also has transactional DDL; and it does not cover the specific task in Section 6.6 step 3, because `CREATE UNIQUE INDEX CONCURRENTLY` is one of the few PostgreSQL statements that cannot run inside a transaction block and leaves an invalid index behind if it fails.
3. **No further cross-major data migration** on the ledger, per C4.
4. **Portability satisfies the exit-strategy expectation** without qualification. This is why Azure SQL loses despite tying on four criteria.

**Two reasons have been withdrawn from the earlier draft, and it is worth saying why.**

*Exact decimal arithmetic and row-level locking* were withdrawn in Section 6.2 because they do not differentiate. *Serialisable snapshot isolation* is withdrawn here for the same reason, applied consistently. An earlier draft listed it as a decisive reason while conceding in the same sentence that correct concurrency "remains an application responsibility" — which is precisely the test Section 6.2 used to disqualify the locking argument. The prototype sets no isolation level and opens no explicit transaction around the read-modify-write, so the strongest available isolation level is exactly as irrelevant to the actual defect as `FOR UPDATE` is. Worse, serialisable snapshot isolation is optimistic: it aborts conflicting transactions with a serialisation failure and therefore **requires application retry logic that this codebase does not have**. On the paper's own standard that makes it a migration cost, not a benefit.

**Adopt these two changes with the migration, not after it:**

- money columns become `NUMERIC(19,4)`; and
- `order_id` acquires a unique constraint, and balance mutation acquires an explicit lock and an idempotency key.

Neither is an engine feature. Both are the defects the engine choice was mistakenly credited with fixing. Migrating without them yields a modern database holding the same unreconcilable data.

### 6.5 Sensitivity of the result

A weighted score is only as good as its weights, so the full weight vector for each scenario is published below and every total is computed from it. An earlier draft stated scenario totals without publishing the vectors; three of those rows were arithmetically unattainable for any non-negative weighting, which made the analysis unauditable. That is corrected here.

| Weight | Baseline | S2 delivery-driven | S3 compliance-driven | S4 cost-driven |
|--------|:--------:|:------------------:|:--------------------:|:--------------:|
| C1 Correctness | 20 | 20 | 15 | 20 |
| C2 Auditability | 15 | 15 | **25** | 10 |
| C3 Azure posture | 15 | 15 | 15 | 15 |
| C4 Version longevity | 15 | 7.5 | 15 | 5 |
| C5 Migration cost | 15 | **30** | 5 | 15 |
| C6 Portability | 10 | 2.5 | **20** | 10 |
| C7 Run cost | 10 | 10 | 5 | **25** |
| **Sum** | **100** | **100** | **100** | **100** |

| Scenario | MySQL 8.4 | PostgreSQL | Azure SQL | Outcome |
|----------|:---------:|:----------:|:---------:|---------|
| Baseline | 4.700 | 4.700 | 3.750 | **Tie** |
| S2 delivery-driven | **4.775** | 4.400 | 3.300 | MySQL, by 0.375 |
| S3 compliance-driven | 4.600 | **4.900** | 4.100 | PostgreSQL, by 0.300 |
| S4 cost-driven | **4.850** | 4.700 | 3.300 | MySQL, by 0.150 |

**This is the most important table in the paper, and it does not support the recommendation on its own.** PostgreSQL wins in exactly one of the four weightings: the one that treats auditability and exit strategy as dominant. MySQL wins whenever delivery effort or run cost is weighted above the baseline. Azure SQL wins nowhere and is eliminated.

The crossover is computable. Holding the other weights at baseline, PostgreSQL leads while C5 is weighted **below about 15%** and MySQL leads above it. The baseline sits exactly on that boundary, which is why the baseline ties.

**What this means for the recommendation.** PostgreSQL is recommended because for a BSP-supervised institution the S3 weighting is the correct one — auditability and a credible exit strategy are regulatory obligations, not preferences that can be traded against sprint capacity. That is a defensible position and it is stated as a position, not as an arithmetic result. It is also falsifiable: an institution that is not supervised, or one under a delivery deadline too short to absorb an engine change, should choose **MySQL 8.4 LTS**, and this paper's own numbers say so.

**The recommendation would change if:** the institution's compliance function accepted Azure Database for MySQL's audit log as sufficient examination evidence, which would level C2 and hand the baseline to MySQL; or the migration had to complete inside a window too short for an engine change, which is scenario S2.

### 6.6 What migration involves

| Step | Work | Notes |
|------|------|-------|
| 1 | Convert schema | Two tables in banking (`accounts`, `transactions`); four in e-commerce (`users`, `products`, `orders`, `order_items`). Small. |
| 2 | Change money columns to `NUMERIC(19,4)` | Required regardless of engine. Six columns: `accounts.balance`, `transactions.amount`, `products.price`, `orders.total_amount`, `order_items.price`, `order_items.subtotal`. |
| 3 | Add unique constraint on `order_id`; add idempotency keys | Will fail if duplicates already exist — treat discovery as a finding, not a blocker to be worked around. On a live table use `CREATE UNIQUE INDEX CONCURRENTLY` then `ALTER TABLE ... ADD CONSTRAINT ... USING INDEX`; note this cannot run in a transaction and leaves an invalid index on failure. |
| 4 | Replace driver | `PyMySQL` to `psycopg`; change the SQLAlchemy URL scheme. |
| 5 | Remove the SQLite fallback | D-5. Fail fast and loudly instead. Non-negotiable. |
| 6 | Replace credentials with managed identity | Non-trivial with `psycopg` and SQLAlchemy: an Entra token must be acquired per connection through a `do_connect` hook, with pool recycling tuned below the token lifetime. Removes D-2 as a class of defect. |
| 7 | Migrate data | Small dataset at present volumes; an offline cutover with a defined window, abort criteria, and a tested rollback is acceptable. |
| 8 | Enable `pgAudit`, CMK, zone-redundant HA, private networking | Per Section 8. |
| 9 | Verify | Reconcile row counts exactly. Monetary totals **cannot** be reconciled to the cent, because the source columns are floating point (D-3): define a tolerance, a rounding rule (half-up), and a documented adjustment entry for the residual. |

## 7. Decision: One Database Server, or One per Application?

Engine choice and server topology are separate decisions, and the second is the one that actually answers Section 2.3.

### 7.1 Options

**Option 1 — one server, two databases, two logins.** Both applications connect to a single PostgreSQL Flexible Server; each owns a database and a restricted role.

**Option 2 — two servers, one per application.** The banking application connects to a server in the banking spoke's private path; the e-commerce application connects to its own.

### 7.2 Comparison

| Consideration | Option 1: shared server | Option 2: server per application |
|---------------|------------------------|----------------------------------|
| Blast radius of a compromised application | Both databases sit behind one server endpoint and one administrative plane. | A compromise reaches one database. |
| Administrative separation | A server administrator, and Azure's administrative role, can read both databases. Separation is a permission that can be granted. | No shared administrative identity exists. Separation is structural. |
| Availability coupling | One maintenance window, one failover, one noisy-neighbour pool for both applications. Shopping traffic can degrade payments. | Independent maintenance and failover. |
| Encryption-key separation | One customer-managed key, or added complexity to have two. | One key per server; a key revocation affects one application. |
| Audit stream | One `pgAudit` stream to separate by database. | One stream per application, separable at source. |
| Network enforceability | Both applications must reach the same private endpoint, so "the shop cannot reach the ledger" cannot be enforced by routing. | Separate endpoints in separate paths; enforceable by network policy and endpoint approval. |
| Right-sizing | Both applications share one compute tier. | Each sized to its own load; the shop can run smaller. |
| Cost | Lower — one HA-enabled server. | Higher — approximately double the database compute line. |
| Operational surface | One server to patch and monitor. | Two. |

### 7.3 Decision

**Adopt Option 2 — one PostgreSQL Flexible Server per application.**

The reasoning is the direct consequence of Section 4.4. The system's central security failure today is that two trust zones share one database server and one administrative login. Option 1 preserves the shape of that failure while improving its implementation: it replaces a shared administrative credential with two restricted roles, which is a real improvement, but the separation still rests on a permission grant, and a permission that can be granted can be granted by mistake.

**What Option 2 does and does not deliver, stated precisely.** An earlier draft of this paper claimed Option 2 makes the separation "a structural fact — there is no route, no credential, and no shared administrative plane." That claim was wrong on all three counts and is withdrawn:

- **"No route" is not a property of the topology.** Section 9.3 establishes that a private endpoint installs a /32 system route which propagates across peering and defeats a `0.0.0.0/0` user-defined route by longest-prefix match. If both servers' endpoints sit in one shared data spoke, the e-commerce spoke has a route to the banking database's endpoint by default. **This paper therefore places each server's private endpoint in its own application spoke, not in a shared data spoke** (Section 8.1), with private-endpoint network policies enabled and deny-by-default network security groups on each endpoint subnet. The separation is then enforced, but it is enforced *by those controls*, not by the mere existence of two servers.
- **"No shared administrative plane" is false.** Both servers live in one tenant. Any principal holding Owner or Contributor at subscription or resource-group scope can reset either server's administrator, alter either firewall, or restore either backup. Azure role-based access control *is* a shared administrative plane. The residual risk is managed by scoping roles to resource groups and requiring just-in-time elevation, not eliminated.
- **"No credential" is false.** A managed identity is a credential; it is merely one that no human holds and no file contains.

**The defensible claim** is therefore: *separation is enforced by separate network paths, per-endpoint approval, deny-by-default subnet rules, separate customer-managed keys, and separate audit streams, with a residual shared control-plane risk mitigated by role scoping and privileged access management.* That is weaker than "structural fact" and it is what the design actually delivers.

Option 2 also carries an availability argument: a payment service should not enter a maintenance window because a product catalogue needed one. One honest qualification — the mitigation below waives zone-redundant high availability on the e-commerce server initially, and a server without it has no automatic failover, so that benefit accrues to the banking side only until the waiver is lifted.

**The cost.** The database compute line roughly doubles. On the indicative figures in the cited architecture notes, where the PostgreSQL line is about USD 1,100 a month, the increment is on the order of **USD 500 to 1,100 a month**, because the e-commerce server can run a materially smaller tier and need not carry zone-redundant high availability at the outset.

To be clear about proportion, since an earlier draft called this "the largest single cost consequence of any recommendation in this paper" — **it is not.** Section 9.9 establishes that the previously published platform figure omits the firewall, a DDoS protection plan, ExpressRoute and its cross-connect and co-location, Bastion, the entire recovery region, and realistic log retention, and that a corrected figure is plausibly 1.7 to 2.5 times the published one. Each of those omissions individually exceeds this topology decision. Against a corrected platform run rate the increment here is on the order of **2 to 4 per cent**.

**Judgement.** A few per cent of platform cost buys the one property this system most conspicuously lacks, and buys it in the layer where the current failure actually sits. It should be spent.

### 7.4 Before and after

| | Development today | Deployment today | Proposed |
|---|---|---|---|
| Engine | MySQL 5.7 | MySQL (Azure, shared) | PostgreSQL Flexible Server |
| `bankdb` location | `bank-mysql` container | shared server | dedicated server, banking path |
| `ecomdb` location | `ecom-mysql` container | **same shared server** | dedicated server, e-commerce path |
| Network exposure | Docker bridge network | **public endpoint** | private endpoint only; public access disabled |
| Credential | `devpass` in Compose | **admin password in public Git** | Entra managed identity; no password |
| Separation enforced by | two Docker networks | a `DB_NAME` string | network path, identity, and separate keys |
| Money type | `Float` | `Float` | `NUMERIC(19,4)` |
| Fallback behaviour | silent SQLite | **silent SQLite** | fail fast, alert |

---

## 8. Proposed Target Architecture

### 8.1 Network topology

The consolidated platform is a hub-and-spoke virtual network in one Azure region, with a second region for recovery.

| Network | Address space | Contents |
|---------|--------------|----------|
| Hub | 10.0.0.0/16 | Azure Firewall Premium, Azure Bastion (private-only) and a management jump host, Azure DNS Private Resolver, ExpressRoute gateway |
| Spoke: banking | 10.1.0.0/16 | Internal Application Gateway (WAF v2), API Management, AKS private cluster, **and the banking database's private endpoint** |
| Spoke: e-commerce | 10.2.0.0/16 | AKS private cluster running the shop, order and catalogue services, **and the e-commerce database's private endpoint** |
| Spoke: shared services | 10.4.0.0/16 | Container registry, Log Analytics workspace behind an Azure Monitor Private Link Scope, and the build-agent subnet |

**There is deliberately no shared data spoke.** An earlier version of this design placed every private endpoint in a common 10.3.0.0/16 spoke. Section 9.3 explains why that cannot stand: a private endpoint's /32 system route propagates across peering and defeats a default user-defined route, so a shared endpoint spoke gives each application a route to the other's database by default — destroying the separation Section 7.3 depends on. Each database's endpoint therefore sits in its own application spoke, with private-endpoint network policies enabled and deny-by-default network security groups on the endpoint subnet. A subnet-level address plan is required before implementation and is out of scope here (Section 3.2).

**Region.** Primary: **Southeast Asia (Singapore)** — the nearest region to Manila with three availability zones, at roughly 30–40 ms round trip. Azure has no Philippine region, which is the single fact that drives the residency position in Section 8.4. Recovery: a paired region, with the choice subject to Section 9.7.

**Ingress.** One inbound path from the internet: **Azure Front Door Premium (with its WAF policy) → Private Link → an internal Application Gateway WAF v2 in the banking spoke → API Management (classic Premium, internal mode) → the workload.**

The Application Gateway is not decoration. Section 9.1 establishes, from vendor documentation, that Front Door's Private Link origin feature and classic API Management virtual-network injection are mutually exclusive: a classic instance must be in public mode to be a Private Link origin, and a VNet-injected classic instance does not support inbound private endpoints. An internal load-balanced resource in the spoke is the standard way to resolve this, and it additionally terminates merchant mutual TLS, which Front Door does not support. Front Door → Private Link → VNet-injected API Management, as drawn in the earlier design, **cannot be built**, and this section no longer proposes it.

Origin lockdown is a named control, not an assumption: API Management public network access disabled, and on any residual public path a network security group restricted to the Front Door backend service tag plus origin-header validation at the gateway.

No *workload endpoint* is reachable from the internet. Platform components — the firewall's outbound addresses, the ExpressRoute gateway, and Bastion unless the private-only tier is used — do hold public addresses, and Section 9.4 explains why the stronger phrasing used earlier was withdrawn.

**Egress and segregation.** Route tables direct each spoke's internet-bound traffic to the hub firewall. Spokes peer with the hub only, never with each other, so the banking and e-commerce networks have no route between them. Section 9.3 records an important qualification concerning private-endpoint traffic.

**Data tier.** The managed data services are Azure-managed and sit outside the virtual networks; each is reached through a private endpoint, which is a network interface in the subscriber's own subnet. Public network access is disabled on every one of them, and applications authenticate with a managed identity, so no database password exists to leak — noting that the authentication model differs per service (Entra authentication must be explicitly enabled on PostgreSQL Flexible Server; Managed HSM has its own local role model and a customer-held security domain, and is not governed by the same data plane).

Two controls are load-bearing and easy to omit. **Private DNS zones**, centrally hosted and linked to every spoke with policy-driven automatic registration, resolve the endpoint names; without them this design silently resolves to public addresses or fails outright (Section 9.5). And **private-endpoint network policies** must be enabled on each endpoint subnet, or endpoint traffic bypasses the firewall by longest-prefix match (Section 9.3). Neither is optional, and neither is visible in a topology drawing.

### 8.2 The accompanying diagram

The topology is delivered as a diagram in two forms:

- `docs/architecture/excalidraw/05-network-topology.excalidraw` — editable source, openable directly at excalidraw.com
- `docs/architecture/excalidraw/preview/05-network-topology.png` — rendered preview
- `docs/architecture/excalidraw/tools/pages/05_network_topology.py` — the script that generates it

The diagram is generated from code rather than drawn by hand. Layout is authored explicitly, text is width-checked at build time so no label can silently overflow, and a geometry linter rejects overlapping cards, arrows crossing labels they do not belong to, and elements escaping their containers. The build is deterministic: regenerating produces a byte-identical file, so a version-control diff shows only real changes. The diagram passes the linter with zero issues.

### 8.3 What was changed in the diagram, and why

The previous version placed roughly twenty-five components on the canvas with no reading order, routed two connectors in long L-shapes across the full width, positioned the data spoke far from the services it fronted, and led most labels with vocabulary. Under blind comparison against the revision on six comprehensibility criteria for a non-specialist audience, the earlier version scored 21 of 60 against the revision's 43 in one pass and 23 against 39.5 in a second, independent pass. Both passes were automated critic reviews, not a human panel; the rubric is the six criteria listed in Section 5.1 Stage 3, and the figures should be read as indicative rather than as a measurement (see the disclosure in Section 12.4).

| Change | Reason |
|--------|--------|
| A single numbered path, 1 to 6, tracing one payment from phone to database | Gives the reader an entry point and an order. This was the largest single improvement. |
| The first connector is one straight vertical | The first thing a reader follows should not have a corner in it. |
| Plain language first, product name second — "checks the sign-in token first" rather than "validate-jwt" | A reader who knows the jargon did not need the diagram. |
| Everything off the request path moved to a column headed "Always on, but off the request path" | Lets a reader who only wants the request path stop at the gutter. |
| An explicit "How to read this" panel | Defines the arrow and colour conventions in place, rather than assuming them. |
| Databases named `bankdb` and `ecomdb` on separate cards | Section 2.3 is the most frequently asked question about this system. The previous diagram showed one database box for two applications, which implied the opposite of the design. |
| The e-commerce spoke given its own inbound connector | Previously the only connector touching it was one leaving it, which left the shop unreachable on a page whose edge component claimed to be the only way in. |
| A connector added between API Management and the cluster | Previously left to adjacency. In a numbered walkthrough a missing link teaches the reader that numbers substitute for connectors. |
| The firewall moved to the foot of the hub | So the connector into the data spoke leaves the component that actually routes it. |
| Three claims corrected (Section 9.4, 9.2, 9.3) | The previous wording overstated what the platform does. |
| The DNS component renamed and its purpose corrected | It named the wrong product for the job it was labelled with (Section 9.5). |

### 8.4 Data residency

Processing occurs in Singapore because Azure offers no Philippine region. Two consequences follow, and both are legal rather than technical:

1. a **cross-border transfer basis** is required under the Data Privacy Act of 2012 (Republic Act 10173), and the specific mechanism relied upon must be named rather than gestured at; and
2. an **outsourcing notification** to the BSP is required, whose current circular reference and threshold must be confirmed with the compliance function.

To preserve the supervisor's right to examine records in country, an in-country copy of the immutable audit record is replicated to a Philippine facility. Section 9.6 records an unresolved tension between that immutability and erasure rights under RA 10173 which requires a documented position.

### 8.5 Non-functional targets

These are design intents. **None is evidenced by measurement**, and two are withdrawn rather than restated, because Section 9.8 establishes that they cannot be supported as written.

| Property | Position |
|----------|----------|
| Availability | **Withdrawn pending a composite objective.** A single 99.99% figure cannot be claimed for a path traversing the edge, gateway, cluster, database, broker, and key store in series; serially dependent components each at 99.95–99.99% multiply to below 99.9%. What must be published instead is a composite objective with a named measurement point (the Front Door edge), the explicit dependency chain, and an error budget. |
| Latency | P95 below 250 ms for the payment path — design intent, unmeasured. Note that hairpinning application-to-database traffic through the firewall adds to this. |
| Throughput | **Unsubstantiated.** The figures carried in the earlier design (2,000 per second sustained, 5,000 peak) have no stated basis — no customer count, no merchant count, no peak-to-mean ratio — and are irreconcilable with this paper's own description of the dataset as small enough for an offline cutover. A volumetric basis is required before any capacity or cost figure derived from it can be relied upon. |
| Recovery point | 0 within region via zone-redundant high availability. The cross-region figure is **not** bounded: PostgreSQL Flexible Server cross-region replication is asynchronous with no guaranteed lag, so "under 60 seconds" is an expectation, not a commitment. |
| Recovery time | **Withdrawn pending a drill.** The earlier 15-minute target presumes replica promotion, key-store restoration with security-domain custody, and a gateway secondary. It must be derived from a documented exercise, not asserted. |
| Audit retention | 7 years, immutable, via locked time-based retention (not legal hold alone — see Section 9.6). |

---

## 9. Technical Findings That Qualify This Proposal

This section exists because a proposal that presents only its own strengths is not usable. Each finding was raised by adversarial review of the target design and then checked against vendor documentation, accessed on the date on the title page. Findings 9.1 to 9.5 identify parts of the previously documented design that are wrong as written; 9.1 is the only one that is strictly unbuildable, while 9.3 and 9.5 describe designs that deploy successfully and then fail to do what they claim. Section 9.10 lists a further six items that remain open.

**Every correction below has been propagated** to Section 8, to Section 6, and to the accompanying diagram. That propagation is the point of the section: an earlier draft recorded these findings and then left the superseded claims standing in the design, which is a worse failure than not having found them.

### 9.1 Front Door with a Private Link origin does not compose with a VNet-injected API Management instance

**Status: verified. Severity: Critical — the ingress design is unbuildable as previously drawn.**

The design specifies Front Door Premium reaching API Management over Private Link, with API Management injected into the banking spoke. Microsoft's documentation for connecting Front Door Premium to an API Management origin over Private Link states that for the v1 (classic) tiers the instance must be deployed in public mode and not in virtual network mode. The API Management documentation states the same from the other side: in the classic tiers, inbound private endpoints are not supported on instances injected into an internal or external virtual network.

These two requirements cannot both be met. A classic Premium instance in *internal* mode has no public gateway for Front Door to reach; in *external* mode the gateway is public, which defeats the purpose.

**Resolution — one of:**

1. **API Management Premium v2**, where inbound private endpoints and virtual-network integration coexist. Constrained by Section 9.2.
2. **Keep classic Premium in internal mode and place an internal Application Gateway (WAF v2) in the spoke** as the Private Link origin, with API Management behind it. This is the conventional pattern for a regulated institution and it also provides the mutual-TLS termination that Front Door cannot.
3. **Classic Premium in external mode**, restricted by network security group to the Front Door backend service tag with header validation at the gateway. Buildable, but the phrase "no public origin" must then be removed from the design.

Option 2 is recommended.

### 9.2 Why resolution 1 was not chosen

**Status: verified. Severity: informational — this records a rejected alternative.**

Multi-region deployment of the API Management gateway is not available in the v2 tiers. Resolution 1 above therefore trades a multi-region gateway for the private endpoint, and also gives up instance backup and restore. Because this paper adopts **resolution 2** (classic Premium in internal mode behind an internal Application Gateway), the multi-region gateway is retained and this constraint does not apply to the proposed design. It is recorded so that a reader who prefers resolution 1 on simplicity grounds understands what it costs.

### 9.3 Private-endpoint traffic bypasses the firewall unless specifically prevented

**Status: verified. Severity: Critical — this is the most misleading claim in the previous design.**

The design states that route tables send every spoke's traffic to the hub firewall first, and the numbered path shows application traffic reaching the database through the firewall. As stated, this is false.

A private endpoint installs a /32 system route, which propagates across peering. A user-defined default route of 0.0.0.0/0 loses to a /32 route by longest-prefix match. Microsoft's troubleshooting guidance lists this explicitly as a cause of traffic bypassing firewall or network-appliance inspection in a hub-and-spoke topology. The consequence in operation is worse than the misstatement: traffic flows and works, so nothing appears broken, but the firewall never sees it and produces no logs for it — and an examiner reviewing an inspection claim would find no evidence supporting it.

**Resolution, and it is structural.** This paper takes the second of the two available options and takes it explicitly. **Each database's private endpoint is placed in its own application spoke** (Section 8.1) rather than in a shared data spoke, private-endpoint network policies are enabled on those subnets, and separation between the two applications is enforced by deny-by-default network security groups with application security groups — not by a claim of firewall inspection. Application-to-database traffic is consequently **not** firewall-inspected, and the design says so rather than implying otherwise.

The alternative — keeping a shared endpoint spoke and adding explicit /32 user-defined routes to the firewall in every consuming subnet — was rejected on operability grounds: it requires tracking endpoint addresses as they change, runs into the per-route-table route limit, needs symmetric return routing or the stateful firewall discards the reply, and puts a shared inspection hop on the synchronous payment path.

Section 8.1 and the accompanying diagram both now carry this qualification explicitly, and Section 7.3's separation claim has been rewritten to rest on these controls rather than on the existence of two servers.

### 9.4 "No public IP address" was not true

**Status: verified by inspection of the design's own components. Severity: High — an overclaim on a document a regulator may read.**

The previous diagram asserted that the edge component was "the only public address". Public addresses are required or implied by several components of this very design: the firewall needs at least one for outbound source translation; Bastion requires one unless the private-only Premium configuration is used; classic API Management virtual-network injection requires a standard public IP resource; and the ExpressRoute gateway holds one.

**The defensible formulation, now used:** no *workload endpoint* is reachable from the internet; the only inbound path is through Front Door; outbound traffic is source-translated through the firewall's public addresses; and platform components hold public addresses that terminate no workload traffic.

### 9.5 The DNS component was the wrong product for the labelled job

**Status: verified. Severity: Critical for implementation.**

The design named a "Private DNS Resolver" and captioned it as resolving private addresses. Two errors. The product is **Azure DNS Private Resolver**, and its purpose is conditional forwarding between on-premises and Azure — not private-endpoint name resolution. Private-endpoint names are resolved by **Azure Private DNS zones**, linked to each spoke's virtual network, and no such zones appeared anywhere in the design.

Without them the "private endpoints only" design resolves to public addresses or fails outright. This is a common first-day private-networking outage. A centrally hosted zone set, linked to every spoke, with policy-driven automatic registration of endpoints, is required. Both components are now named correctly and the diagram states that Private DNS zones do the resolving.

### 9.6 Seven-year immutability conflicts with erasure rights

**Status: open. Requires a documented legal position, not an engineering decision.**

The audit archive relies on immutable storage with a locked time-based retention policy. That is the correct control for the retention requirement — and it means that data cannot be deleted for seven years, including in response to a data-subject erasure request under RA 10173. A legal hold alone does not deliver the same guarantee, since it can be removed by a holder of the relevant permission.

The institution needs a written position reconciling statutory retention with erasure rights before this control is implemented. Silence is not a position.

### 9.7 The recovery region choice should be made by compliance, not by latency

**Status: open. Severity: Medium.**

The nearest paired region satisfies the technical requirement for a separate geography with availability zones. For an institution defending a cross-border transfer basis, however, the lawful-access regime of the recovery jurisdiction is a material consideration, and alternatives may be easier to defend.

There is also a concrete trap: geo-redundant storage replicates automatically to the paired region. The immutable audit archive should therefore be configured as **zone-redundant** so that it remains in the primary region, with the in-country copy handled separately, rather than being replicated across a border as a side effect of a storage default.

### 9.8 The availability and recovery targets are not supportable as stated

**Status: verified by analysis. Severity: High.**

A single 99.99% figure cannot be claimed for a path that traverses the edge, the gateway, the cluster, the database, the message broker, and the key store in series. Serially dependent components each at 99.95–99.99% multiply to *below* 99.9%. Publishing the higher number invites a finding.

The 15-minute recovery target is similarly unevidenced: it presumes replica promotion, key-store restoration with security-domain custody, and a gateway secondary that — per Section 9.2 — may not be a multi-region service at all.

**Resolution.** Publish a composite service-level objective with a named measurement point, an explicit dependency chain, and an error budget; and derive the recovery time from a documented drill rather than from an assumption.

### 9.9 Two service selections are stale, and the cost figure is materially understated

**Status: verified. Severity: Medium to High.**

**The cache selection is on a retirement path that precedes the platform's own rollout.** Azure Cache for Redis Enterprise retires in **March 2027**, and the Basic, Standard, and Premium tiers retire in **September 2028**; **Azure Managed Redis** is the forward path. Selecting a retiring tier for a component that holds idempotency keys and distributed locks means a forced migration of a payment-critical component within the first year of production. The design now specifies Azure Managed Redis.

**The key-management justification no longer holds.** The design justified a dedicated Managed HSM partly on the grounds that Key Vault Premium offered a lower FIPS validation level. Following a 2025 firmware update, **both Azure Managed HSM and Azure Key Vault Premium are validated to FIPS 140-3 Level 3**. Managed HSM remains defensible — on single tenancy, customer-held security domain, HSM-local role-based access control, and non-exportable key policy — but it must be argued on those grounds, because roughly a fifth of the previously stated monthly run rate rested on a distinction that no longer exists.

**The cost figure omits significant lines.** The previously published figure of approximately USD 16,000 per month excludes the firewall's base and per-gigabyte processing charges, a DDoS protection plan (a fixed monthly charge in the low thousands, on its own a material share of the stated total), the ExpressRoute circuit together with provider cross-connect and co-location, Bastion, the entire recovery region, and a realistic log-ingestion and seven-year-retention figure for an institution ingesting firewall, WAF, network-flow, cluster, and database audit logs.

**Resolution.** Present cost as a range with assumptions itemised per line. A realistic figure is plausibly **1.7 to 2.5 times** the published one, i.e. of the order of USD 27,000 to 40,000 a month. That multiplier is itself an estimate and this paper does not price the individual lines — doing so requires the volumetric basis that Section 8.5 records as missing, because firewall and log-ingestion charges are both consumption-based. **A multiplier without line items is a better-informed guess, not a costing**, and the proposal should not be approved on it. What can be said with confidence is the direction and the rough magnitude, and that the DDoS plan alone is a fixed four-figure monthly charge which on its own exceeds the entire cost consequence of the two-server decision in Section 7.3.

### 9.10 Findings that remain open

For completeness, and because a proposal should say what it has not resolved:

- **No network security groups appear in the design.** For a supervised institution this is normally the first control examined, and per Section 9.3 it may be the actual enforcement mechanism for the separation claim in Section 7.3.
- **No backup or long-term-retention objects are specified.** Point-in-time restore for 35 days does not satisfy a seven-year statutory retention requirement; these are different controls.
- **A single ExpressRoute circuit** to the system of record is an unmitigated single point of failure.
- **The pipeline contradicts the network model.** Hosted build agents cannot reach a private endpoint, so database migrations require agents inside a spoke.
- **The design and the earlier notes disagree on scope** — several services appear in one and not the other. They should be reconciled before submission, because the discrepancy reads as evidence that the design is unsettled.
- **A synchronous cross-domain call** appears in the payment saga in the earlier notes, which contradicts the claim that the two applications have no network route between them. Either the claim or the saga must change; projecting order totals into the banking domain as a read model via Service Bus is the stronger resolution, and it is the one this paper assumes.
- **The decision to consolidate onto Azure was not itself evaluated** with the declared-criteria rigour applied to the engine choice. Do-nothing, remediate-in-place, consolidate-onto-AWS (where development already runs), and consolidate onto a Philippine provider — the option most responsive to the residency problem in Section 8.4 — are not scored. This is the largest methodological gap in the paper and an examiner is entitled to lead with it.
- **Azure SQL Managed Instance is absent from the option set** in Section 6.1. It supports virtual-network injection and is directly portable to SQL Server on premises, so it would score better on C3 and materially better on C6 than Azure SQL Database. Its exclusion is not justified and it is the option most likely to change the ranking.
- **No connection pooling is specified.** With a Flask and Gunicorn process model against PostgreSQL, PgBouncer or the built-in pooler is a first-order sizing decision and it is absent.
- **No subnet-level address plan, no network-security-group rule matrix, no risk register, no phase durations or effort estimates, and no rollback plan** beyond the note in Section 6.6 step 7. Section 9.10's first bullet is the most serious of these, because Section 7.3's separation claim now depends on those rules.
- **The target CI/CD platform is never named.** Jenkins is criticised throughout and no replacement is specified, while Section 8.1 now requires a build-agent subnet inside a spoke.

---

## 10. Migration Sequencing

Phases are ordered by dependency, not by convenience. Phase 0 is not optional and does not wait for the rest.

| Phase | Objective | Key dependency |
|-------|-----------|----------------|
| **0. Contain** | Rotate the exposed credential and purge it from Git history and build logs. Remove the SQLite fallback. Disable the database's public endpoint. Treat as incident response, not project work. | None. Begin immediately. |
| **1. Foundation** | Landing zone, management groups, hub-and-spoke network, Private DNS zones, policy in audit mode, pipeline identity federation. | Phase 0 |
| **2. Consolidate and migrate the data tier** | Two PostgreSQL Flexible Servers; `NUMERIC(19,4)`; unique constraint on `order_id`; managed-identity authentication; private endpoints with the route policy from Section 9.3. | Phase 1 |
| **3. Move the workloads** | Both applications to private AKS clusters in their own spokes; ingress per Section 9.1; retire the ACI and EC2 deployments. | Phase 2 |
| **4. Payment correctness** | Ledger service, transactional outbox, idempotency, saga with compensation. Delete the synchronous HTTP callback. Resolves A-1 to A-4. | Phase 2 — cannot start before the data tier exists |
| **5. Identity, risk, compliance** | Customer and staff identity separation, privileged access management, fraud and AML controls, audit archive with in-country copy. | Phases 3 and 4 |
| **6. Assurance** | Chaos testing, load testing to the stated throughput, penetration testing, policy moved from audit to deny, recovery drill to evidence the recovery-time objective. | All |

A legal and regulatory track runs in parallel from Phase 0: the cross-border transfer basis, the licensing position, the outsourcing notification, the retention-versus-erasure position from Section 9.6, and QR Ph registration.

---

## 11. Conclusion

The system examined here is a working prototype of a payment flow, deployed in a way that cannot be operated or examined. Its defects are not independent: credentials sit in the pipeline because there is no secret store, the database is publicly reachable because there is no private network, and releases cause outages because there is no orchestrator. Those are the symptoms of three environments assembled separately. Consolidation onto one governed platform is proposed because it removes the conditions that produced them, rather than patching them individually.

On the question that prompted this paper: **the two applications do not share a database, but in the deployed environment they share a database server and a single administrative credential that is published in a public repository.** The separation that exists in development does not exist where it matters. The proposal replaces a shared server reached with a shared password by two servers reached with managed identities over separate private paths, so that the statement "the shopping application cannot reach the ledger" becomes something the platform enforces rather than something the configuration asserts.

On the engine: **PostgreSQL Flexible Server**, but not because the numbers say so. **They tie.** MySQL 8.4 LTS and PostgreSQL both score 4.70, and of four weightings tested PostgreSQL wins one — the weighting that treats auditability and exit strategy as dominant. An earlier draft of this paper reported a comfortable 4.60-to-3.80 margin at High confidence; two of the scores producing it were wrong, and correcting them erased the margin. Confidence is now Moderate and the recommendation is argued rather than computed: the two candidates differ in one criterion each, MySQL's advantage is a migration cost paid once, PostgreSQL's is an audit obligation discharged every day the institution is supervised, and for a supervised institution that asymmetry decides it. An institution that is not supervised, or one under a delivery deadline too short to absorb an engine change, should choose MySQL 8.4 — and this paper's own table says so.

The reasoning matters more than the result here. Three of the arguments usually offered for PostgreSQL in this project do not survive: exact decimal arithmetic, row-level locking, and serialisable isolation are all either equally available in MySQL or irrelevant to the actual defect. The defects they were credited with fixing — floating-point money, and an unserialised balance update — live in the application code and must be fixed there, during the migration, or the platform will hold the same unreconcilable data on a newer engine.

Section 9 is the part of this paper most likely to be useful. Adversarial review found that the ingress design as previously drawn cannot be built, that the central claim about firewall inspection is false by default for exactly the traffic the diagram highlighted, that the DNS component named the wrong product for the job it was labelled with, that a headline security claim was an overstatement, that a selected cache tier retires before the platform would finish rolling out, that a key-management justification had been overtaken by a firmware update, and that the cost figure is understated by a factor somewhere between 1.7 and 2.5.

Each of those corrections has been carried back into Section 8, Section 6, and the diagram — including a change of topology, because the private-endpoint routing finding in Section 9.3 destroyed the separation argument in Section 7.3 and could only be answered by moving each database's endpoint into its own spoke. That propagation is the test. A document that records its own errors and then leaves the superseded claims standing elsewhere has not been rigorous, it has been rigorous-sounding; the availability and cost figures in Section 8.5 are withdrawn rather than restated for exactly that reason.

The recommendation survives. Its confidence does not, and that is the honest outcome: this is a proposal for a platform on which the remaining problems can be fixed and the fixes evidenced, not a claim that they are already solved. Section 9.10 lists what is still missing, and the largest item on it is that the decision to consolidate onto Azure was never subjected to the same scrutiny as the choice of database engine.

---

## 12. References

### 12.1 Primary sources — the repository under assessment

All factual claims about current behaviour derive from these files.

| Reference | Used for |
|-----------|----------|
| `banking-app/app.py` | Connection string construction; `bankdb` defaults; SQLite fallback; payment handler ordering; cross-application coupling |
| `ecommerce-app/app.py` | Connection string construction; `ecomdb` defaults; SQLite fallback |
| `banking-app/models.py` | `Float` money columns; absence of a unique constraint on `order_id` |
| `banking-app/seed.py` | Seed accounts; plaintext passwords; administrator flag |
| `banking-app/docker-compose.bank.yml`, `ecommerce-app/docker-compose.ecom.yml` | MySQL 5.7; separate servers, networks, and volumes in development |
| `banking-app/Jenkinsfile`, `ecommerce-app/Jenkinsfile` | Shared database host; hardcoded credential; delete-and-recreate deployment |
| `banking-app/k8s/*.yaml` | Plaintext secret; public load balancer; port mismatch |
| `banking-app/Dockerfile`, `ecommerce-app/Dockerfile` | Commented-out non-root user; serving port |
| `banking-app/nginx/nginx.conf`, `ecommerce-app/nginx/nginx.conf` | Present but referenced by no Compose file or pipeline stage; proxy to ports 5001/5000 against images serving on 80 |
| `ecommerce-app/models.py` | The four `ecomdb` tables; the `users` table with plaintext passwords; four of the six floating-point money columns |
| `ecommerce-app/k8s/*.yaml` | Second instance of the manifest defects in P-2 and P-5 |
| `banking-app/requirements.txt`, `ecommerce-app/requirements.txt` | `PyMySQL` present, no PostgreSQL driver |
| `README.md` | Describes a root `docker-compose.yml`, a root `nginx/`, and an Adminer service, none of which exist |
| `docs/architecture/target-azure-architecture.md` | Previously documented target design, address plan, service selection, cost table |
| `docs/architecture/critical-findings.md` | Cross-referenced for severity comparison in Section 2.2. Mapping to this paper's identifiers: F-01→A-1, F-02→A-2, F-03→A-3, F-04→A-4, F-05→D-4, F-06→D-3, F-07→A-5, F-08→A-6, F-09→D-2, F-10→P-4, F-11→D-5, F-12→P-2 and P-3, F-13→(out of scope, application risk controls), F-14→P-8 |
| `docs/architecture/bsp-compliance-matrix.md` | Source of the regulatory instrument list in Section 12.3 |

### 12.2 Vendor documentation

Consulted for Section 9. Each was checked directly; content is summarised rather than quoted.

1. Microsoft, *Connect Front Door Premium to an Azure API Management origin with Private Link* — https://learn.microsoft.com/azure/frontdoor/standard-premium/how-to-enable-private-link-apim (Section 9.1)
2. Microsoft, *Set up an inbound private endpoint for Azure API Management* — https://learn.microsoft.com/azure/api-management/private-endpoint (Section 9.1)
3. Microsoft, *Azure API Management v2 tiers overview* — https://learn.microsoft.com/azure/api-management/v2-service-tiers-overview (Section 9.2)
4. Microsoft, *Troubleshoot private endpoint connectivity failures* — https://learn.microsoft.com/troubleshoot/azure/private-link/troubleshoot-private-endpoint-connectivity-failure (Section 9.3)
5. Microsoft, *Manage network policies for private endpoints* — https://learn.microsoft.com/azure/private-link/disable-private-endpoint-network-policy (Section 9.3)
6. Microsoft, *Azure Firewall scenarios to inspect traffic destined to a private endpoint* — https://learn.microsoft.com/azure/private-link/inspect-traffic-with-azure-firewall (Section 9.3)
7. Microsoft, *Azure Bastion configuration settings* — https://learn.microsoft.com/azure/bastion/configuration-settings/ (Section 9.4)
8. Microsoft, *Frequently asked questions on the retirement of Azure Cache for Redis* — https://learn.microsoft.com/azure/azure-cache-for-redis/retirement-faq (Section 9.9)
9. Microsoft, *Azure Cache for Redis product page* — retirement dates and the Azure Managed Redis forward path — https://azure.microsoft.com/products/cache (Section 9.9)
10. Microsoft, *Azure Managed HSM and Azure Key Vault Premium are now FIPS 140-3 Level 3* — https://techcommunity.microsoft.com/blog/microsoft-security-blog/azure-managed-hsm-and-azure-key-vault-premium-are-now-fips-140-3-level-3/4418975 (Section 9.9)
11. Microsoft, *HSM firmware update for Azure Key Vault Managed HSM and Azure Key Vault Premium* — https://learn.microsoft.com/azure/key-vault/managed-hsm/firmware-update (Section 9.9)
12. Microsoft, *Azure Database for MySQL version support policy* — https://learn.microsoft.com/azure/mysql/concepts-version-policy (Sections 6.3, 6.4)
13. Microsoft, *Announcing Extended Support for Azure Database for MySQL* — https://techcommunity.microsoft.com/blog/adformysql/announcing-extended-support-for-azure-database-for-mysql/4442924 (Section 6.4)
14. Microsoft, *Azure Database for PostgreSQL Flexible Server* — audit logging with pgAudit, customer-managed keys, high availability — https://learn.microsoft.com/azure/postgresql/flexible-server/ (Section 6.3)
15. Oracle, *MySQL 8.0 Reference Manual* — `SELECT ... FOR UPDATE`, `SKIP LOCKED`, `NOWAIT`, `CHECK` constraint support from 8.0.16, and SQL-mode-dependent handling of invalid values — https://dev.mysql.com/doc/refman/8.0/en/ (Sections 6.2, 6.3)
16. The PostgreSQL Global Development Group, *PostgreSQL Documentation* — transactional DDL, serialisable snapshot isolation, `NUMERIC`, logical replication — https://www.postgresql.org/docs/ (Sections 6.2, 6.3)
17. The PostgreSQL Global Development Group, *Versioning Policy* — annual major releases with five years of support — https://www.postgresql.org/support/versioning/ (Section 6.3)

*Content from vendor documentation was rephrased for compliance with licensing restrictions.*

### 12.3 Regulatory and statutory instruments

Listed as the engineering-side mapping used in this paper. **This is not a legal opinion.** Circular numbers, amendment status, and applicability must be confirmed with the institution's compliance function; Section 9 records this as an open item.

| Instrument | Relevance |
|-----------|-----------|
| BSP Circular No. 1055 (2019) — National QR Code Standard (QR Ph) | The present QR payload encodes an arbitrary URL and is not an EMVCo-based QR Ph payload |
| BSP Circular No. 1198 (2024) — Merchant Payment Acceptance Activities | Licensing position, settlement, AML obligations, end-user protection |
| BSP Circular No. 1140 (2022) and related memorandum — technology outsourcing | Notification, right to examine, exit strategy |
| BSP Circular No. 982 (2017) — information security management | Control expectations — confirm current amended text |
| BSP Circular No. 808 (2013) — IT risk management | Control expectations — confirm current amended text |
| BSP Manual of Regulations for Banks, Appendix 75 | Information technology risk management |
| Republic Act No. 10173 — Data Privacy Act of 2012 | Cross-border transfer basis; erasure rights (Section 9.6) |
| Republic Act No. 11127 — National Payment Systems Act | Payment system operator obligations |
| Republic Act No. 9160 as amended — Anti-Money Laundering Act | Registration and reporting |
| Republic Act No. 8792 — Electronic Commerce Act | Electronic records and signatures |

PCI DSS is not currently in scope: the flow is account-to-account and no card data is processed. Should card acceptance be added, using a tokenising acquirer would keep the cardholder data environment outside this platform.

### 12.4 Method

The three sources below are **prompt and workflow libraries, not scholarly method references.** They are cited because they are what was actually used, and they are flagged as such because a reader is entitled to know that this paper's method has a practitioner rather than an academic provenance. A formal treatment would ground the weighted-criteria approach in multi-attribute decision analysis (Keeney and Raiffa; Saaty on the analytic hierarchy process) and the isolation-level discussion in the primary literature (Berenson et al., *A Critique of ANSI SQL Isolation Levels*, SIGMOD 1995; Cahill, Röhm and Fekete, *Serializable Isolation for Snapshot Databases*, TODS 2009; Ports and Grittner, *Serializable Snapshot Isolation in PostgreSQL*, VLDB 2012 — the primary source for the mechanism discussed in Section 6.3). Those works are named here as required reading for a formal revision, not cited as having been consulted.

18. `alirezarezvani/claude-skills` — https://github.com/alirezarezvani/claude-skills. The `tech-stack-evaluator` workflow supplied the structure used in Section 6: declare criteria and weights before scoring, justify each score, run a sensitivity analysis, state a confidence level.
19. `alirezarezvani/claude-skills`, `adversarial-reviewer` workflow — hostile-persona review with mandatory findings and severity classification, on the standing rule that finding nothing constitutes a failed review. Applied to both the diagram and the target design; Section 9 is the output, as are the score corrections in Section 6.3.
20. `duolahypercho/gauntlet-loop` — https://github.com/duolahypercho/gauntlet-loop. Iterative fan-out with an independent critic and blind side-by-side comparison against a named reference, repeated rather than run once. Applied to the diagram revision; Section 8.3 reports the comparison.

**Disclosure.** This paper was drafted with AI assistance. The evidence in Sections 2 and 4 was read from the repository source files listed in Section 12.1 and each claim checked against them; the vendor-documentation claims in Section 9 were each verified against the pages cited in Section 12.2 on the date on the title page. The weighted scores in Section 6.3 are expert judgement and are published with their weights so that a reader can substitute their own. Section 8.3's comparison scores were produced by an independent review pass rather than by the author of the revision, but not by a human panel, and they should be read as an indicative rubric rather than a measurement — the inter-rater reliability is unknown and no human validation was performed.
