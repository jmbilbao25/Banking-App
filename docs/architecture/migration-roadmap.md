# Migration Roadmap

Sequenced by **risk reduction per unit of effort**, not by architectural tidiness. Phase 0
is deliberately not a migration — it is incident response, and it should start before any
Azure design work is approved.

---

## Phase 0 — Contain (days, not weeks)

Nothing here requires the target architecture. All of it is worth doing even if the
migration is never funded.

| # | Action | Finding |
|---|---|---|
| 1 | Rotate the Azure MySQL credential in both `Jenkinsfile`s. Audit MySQL access logs for use. Purge from git history with `git filter-repo`. | F-09 |
| 2 | Add authentication to `POST /api/orders/<id>/paid`, or block it at the proxy. It is currently an open endpoint that grants free merchandise. | F-01 |
| 3 | Resolve the payment amount server-side from the order instead of trusting the form field. | F-02 |
| 4 | Reorder the payment handler: commit the debit before notifying the merchant. | F-04 |
| 5 | Add a unique constraint on `transactions.order_id`. | F-05 |
| 6 | Replace hardcoded `app.secret_key` values with an environment variable; invalidate all sessions. | F-08 |
| 7 | Uncomment `USER appuser` in both Dockerfiles. | F-10 |
| 8 | Remove the silent SQLite fallback. Fail fast instead. | F-11 |
| 9 | Put TLS in front of both services. A managed certificate on any reverse proxy is sufficient as a stopgap. | — |

Phase 0 does not make the system compliant. It stops the bleeding.

---

## Phase 1 — Azure foundation (weeks 1–6)

Build the platform. Do not migrate workloads yet.

- Entra ID tenant structure, management group hierarchy, subscription vending.
- Terraform with Azure Verified Modules; remote state in Storage with locking.
- Hub-and-spoke VNets, Azure Firewall Premium, Bastion, Private DNS Resolver.
- Azure Policy assignments: CIS, Azure Security Benchmark, PCI DSS initiatives in
  **audit** mode first, then **deny**.
- Key Vault Premium + Managed HSM provisioning, key ceremony documented.
- ACR Premium, Log Analytics, Defender for Cloud, Sentinel onboarding.
- GitHub Actions OIDC federation — delete every stored cloud credential.

**Exit criteria:** a policy-compliant empty landing zone, provable from
Defender for Cloud secure score, with zero long-lived credentials anywhere in CI.

---

## Phase 2 — Lift to AKS (weeks 5–12, overlaps Phase 1)

Move the existing applications essentially as-is. Resist refactoring here — the goal is
to change one variable at a time.

- Multi-stage distroless images, non-root, read-only root filesystem.
- Private AKS clusters, Workload Identity, Secrets Store CSI driver.
- **MySQL 5.7 → PostgreSQL Flexible Server**, zone-redundant, private endpoint, CMK.
  Migrate schema with money columns converted to `NUMERIC(19,4)` (F-06). This is the one
  refactor worth doing during the lift, because a second data migration later is worse.
- Front Door Premium + WAF + APIM Premium in front. Delete every public IP.
- Decommission AWS EC2 and Docker Hub.
- Argo CD, Argo Rollouts, canary deploys.
- OpenTelemetry instrumentation and correlation IDs (F-14).

**Exit criteria:** identical functionality, zero public endpoints on data or compute,
zero-downtime deploys demonstrated, all traffic TLS 1.3.

---

## Phase 3 — Ledger and payment correctness (weeks 10–20)

The highest-value phase. This is where the platform stops being a prototype.

- Introduce `ledger-service`: append-only double-entry journal, zero-sum constraint,
  `SELECT ... FOR UPDATE`, `INSERT`-only grants.
- `balance-projection` CQRS read model; retire the mutable `balance` column.
- Service Bus Premium; transactional outbox + relay. **Delete the HTTP callback path
  entirely** (F-01, F-04).
- Redis-backed idempotency keys with 24 h TTL (F-05).
- `payment-orchestrator` saga with explicit compensation via `reversal-service`.
- `qrph-service`: EMVCo TLV, CRC16, detached JWS from Managed HSM (F-03).
- `reconciliation-service` EOD sweep asserting the zero-sum invariant.

**Exit criteria:** every payment reconciles; a deliberately injected failure at each saga
step leaves no orphaned state; the QR payload cannot be tampered with.

---

## Phase 4 — Identity, risk, compliance (weeks 16–26)

- Migrate authentication to Entra External ID; MFA, passkeys, Conditional Access
  (F-07, F-08). Retire all application-managed credentials.
- `fraud-service`: velocity rules, device fingerprinting, ML scoring, step-up auth.
- `aml-service`: sanctions/PEP screening, CTR and STR workflows.
- `audit-service`: hash-chained events → ADLS WORM with legal hold; Confidential Ledger
  anchoring.
- In-country archival replication to PH co-location.
- `reporting-service` for BSP and AMLC submissions.
- Move `ledger-service` onto the confidential compute node pool.

**Exit criteria:** an examiner's question — "show me everything that happened to this
account on this date, and prove the record has not been altered" — is answerable.

---

## Phase 5 — Resilience and assurance (weeks 24–32)

- Secondary region (East Asia): APIM multi-region unit, promotable read replica,
  Service Bus geo-DR pairing, Argo CD state pre-synced.
- Chaos Studio experiments: zone loss, DB failover, Service Bus throttling, region loss.
- Load testing to 5,000 TPS peak; SLO and error-budget definition.
- Documented DR drill with retained evidence.
- Third-party VAPT; remediation to closure.
- Azure Policy moved from audit to **deny** across all initiatives.

**Exit criteria:** measured RPO ≤ 60 s and RTO ≤ 15 min from an actual drill, not a
design assertion.

---

## Sequencing constraints

```
Phase 0  ██                                          (immediate, blocks nothing)
Phase 1  ────████████████                            (platform first)
Phase 2  ──────────████████████████                  (needs Phase 1 landing zone)
Phase 3  ────────────────────████████████████████    (needs Phase 2 PostgreSQL + Service Bus)
Phase 4  ──────────────────────────████████████████████
Phase 5  ────────────────────────────────────████████████████
```

Phase 3 cannot start before PostgreSQL and Service Bus exist. Phase 4's audit
immutability depends on the Phase 3 ledger producing events worth retaining. Phase 5
validates everything and therefore goes last.

---

## Parallel legal and regulatory track

These are not engineering tasks and they run alongside from day one. Any one of them can
block go-live regardless of technical readiness.

| Item | Owner |
|---|---|
| Cross-border data transfer basis under RA 10173 (Azure has no PH region) | Legal / DPO |
| Licensing position under Circular 1198 for merchant payment acceptance | Compliance |
| Technology outsourcing notification/approval under Circular 1140 | Compliance |
| QR Ph participation and merchant identifier registration | Payments / BSP liaison |
| AMLC registration and reporting channel setup | Compliance |
| Confirmation of all circular references in [bsp-compliance-matrix.md](bsp-compliance-matrix.md) | Compliance |
