# Critical Findings

These are specific, exploitable defects in the current code — not generic best-practice
advice. Each drives a corresponding control in the target architecture. Severity uses
CVSS-style reasoning: financial loss and authentication bypass rank highest.

---

## F-01 — Unauthenticated payment confirmation endpoint  🔴 CRITICAL

`ecommerce-app/app.py`:

```python
@app.route('/api/orders/<order_id>/paid', methods=['POST'])
def mark_paid(order_id):
    order = db.session.get(Order, order_id)
    ...
    order.status = "PAID"
```

There is **no authentication, no signature, and no source restriction** on this route.
In the ACI deployment the container publishes port 80 directly, so this is reachable from
the internet. Anyone who can guess or observe an 8-character order ID can mark an order
paid without any money moving:

```
POST http://<ecom-host>/api/orders/a1b2c3d4/paid
```

The order flips to `PAID`, stock is decremented, and the checkout page shows success.
**Direct, unauthenticated theft of goods.**

**Target control:** no public callback at all. Payment completion is an
Azure Service Bus event consumed by `order-service` over a private endpoint. If a
synchronous webhook is ever required, it must carry an HMAC signature over
`(order_id, amount, timestamp, nonce)` with replay rejection outside a 60-second window.

---

## F-02 — Payment amount is taken from client input  🔴 CRITICAL

`banking-app/app.py`, the POST branch of `/pay`:

```python
amount = float(data.get('amount', 0))
...
consumer.balance -= amount
merchant.balance += amount
```

`amount` originates in a hidden form field, which itself originates in the QR query
string. It is **never compared against the order total** held by `ecommerce-app`. The
`order_details` fetched earlier are used only for status checks and display.

An attacker edits the form field to `0.01`, submits, and:
1. `banking-app` calls `POST /api/orders/{id}/paid` → order marked `PAID` in full.
2. `banking-app` debits ₱0.01 and credits the merchant ₱0.01.

A ₱10,000 order is settled for one centavo. The merchant absorbs the loss.

**Target control:** the QR carries only an order reference. `payment-orchestrator`
resolves the authoritative amount server-side from `order-service` over the internal
mesh, and the ledger rejects any posting whose amount differs from the resolved order
total.

---

## F-03 — QR payload is unsigned and tamperable  🔴 CRITICAL

`ecommerce-app/app.py`:

```python
payment_url = f"{BANK_PUBLIC_BASE}/pay?order_id={order_id}&amount={order.total_amount}&merchant_account={MERCHANT_ACCOUNT}&expires={order.expires_at}"
```

Every security-relevant field — `amount`, `merchant_account`, `expires` — is an
unauthenticated URL parameter. Consequences:

- `amount` → see F-02.
- `merchant_account` → **funds can be redirected to an attacker-controlled merchant.**
  The handler compounds this with a silent fallback:
  `merchant = Account.query.get('jmb-grocery') or Account.query.get('techstart-grocery')`,
  so an invalid merchant ID does not fail the payment, it reassigns it.
- `expires` → the expiry check is `time.time() > int(expires)`, so the attacker simply
  raises the value and revives a dead QR.

**Target control:** BSP Circular 1055 mandates the QR Ph standard, which is EMVCo TLV
with a CRC16 checksum — not a URL. Target design emits a QR Ph TLV payload whose
merchant data is registered, plus a detached JWS signature produced by a
non-exportable P-256 key in Azure Key Vault Managed HSM. `qrph-service` verifies the
signature before a payment is admitted.

---

## F-04 — Callback precedes debit: money-losing ordering bug  🔴 CRITICAL

`banking-app/app.py` executes in this order:

1. `POST /api/orders/{order_id}/paid` — merchant-side state committed.
2. `consumer.balance -= amount` / `merchant.balance += amount`.
3. `db.session.add(tx)` / `db.session.commit()`.

If step 2 or 3 fails — DB failover, connection drop, pod eviction, insufficient-balance
race — the order is **already irreversibly `PAID`** with stock decremented, and no funds
moved. There is no compensating action anywhere in the codebase.

The inverse also exists: if the process dies between the commit at step 3 and the
response, the customer is debited with no confirmation and no reconciliation job to
detect it.

**Target control:** transactional outbox. The ledger posting and the outbox row are
written in one local transaction; a relay publishes to Service Bus at-least-once.
`payment-orchestrator` runs an explicit saga with a compensating reversal entry, and
`reconciliation-service` sweeps for orphans at end of day.

---

## F-05 — Double-spend race on concurrent payments  🟠 HIGH

```python
existing_tx = Transaction.query.filter_by(order_id=order_id).first()
if existing_tx: ...
# ... later ...
consumer.balance -= amount
```

Two concurrent requests both read `existing_tx is None`, both pass the
`consumer.balance < amount` check, and both debit. There is:

- no `SELECT ... FOR UPDATE` on the account row,
- no unique constraint on `transactions.order_id` (the column is
  `nullable=False` only — see `banking-app/models.py`),
- no `Idempotency-Key` handling.

Balance can be driven negative, and a single order can produce multiple transactions.

**Target control:** unique index on `(order_id)`; Redis-backed idempotency keys with a
24-hour TTL; and balances derived from an append-only double-entry ledger so no row is
ever mutated in place.

---

## F-06 — Money stored as binary floating point  🟠 HIGH

`banking-app/models.py` and `ecommerce-app/models.py`:

```python
balance = db.Column(db.Float, default=0.0)
amount  = db.Column(db.Float, nullable=False)
price   = db.Column(db.Float, nullable=False)
```

`Float` maps to IEEE-754 double. `0.1 + 0.2 != 0.3`. Over a transaction ledger this
produces balances that do not reconcile to the sum of their entries — an audit failure
independent of any attack, and a finding a BSP examiner would raise immediately.

**Target control:** store minor units as `BIGINT` centavos, or `NUMERIC(19,4)` in
PostgreSQL. Never float. Ledger invariant `SUM(debits) - SUM(credits) = 0` enforced by a
database constraint and asserted by the reconciliation job.

---

## F-07 — Plaintext password storage and comparison  🟠 HIGH

```python
if account and account.password == password:      # banking-app
if user and user.password == password:            # ecommerce-app
```

Passwords are stored as cleartext `String(100)` and compared with `==`, which is also
non-constant-time. `seed.py` seeds every account with `password123`. There is no
lockout, no MFA, and no password policy.

**Target control:** Microsoft Entra External ID as the CIAM system of record —
Argon2id/bcrypt is then not even the bank's concern. Conditional Access enforces MFA,
risk-based step-up, and passkeys. No credential material in the application database.

---

## F-08 — Hardcoded Flask secret keys  🟠 HIGH

```python
app.secret_key = 'super-secret-bank-key-for-prototype-only'   # banking-app
app.secret_key = 'super-secret-ecommerce-key'                 # ecommerce-app
```

Both are committed to a public repository. Flask session cookies are signed with this
key, so anyone reading the repo can forge a session for any account — including
`alice-consumer`, which `seed.py` creates with `is_admin=True`. Admin access grants
`/admin/add_funds`, i.e. **arbitrary balance creation.**

**Target control:** no application-managed sessions. Tokens are OIDC JWTs validated at
Azure API Management against Entra External ID. Any residual signing material comes from
Key Vault via the Secrets Store CSI driver, referenced by workload identity, never by
value.

---

## F-09 — Live database credentials committed in CI  🟠 HIGH

Both `Jenkinsfile`s contain:

```groovy
--environment-variables DB_HOST=testestste.mysql.database.azure.com \
  DB_USER=jmbilbao25 DB_PASSWORD='@dreamCS2025' DB_NAME=bankdb
```

A production Azure MySQL hostname, username and password are in version control on a
public repo. Because ACI environment variables are not marked `--secure-environment-variables`,
they are additionally readable via `az container show` by anyone with reader scope.

> **Action required regardless of this review:** treat this credential as compromised.
> Rotate it, audit MySQL access logs, and purge it from git history
> (`git filter-repo`) — rotation alone does not remove it from the public history.

**Target control:** GitHub Actions federated to Azure with OIDC — no stored cloud
credentials at all. Database access uses Entra ID token authentication via AKS workload
identity, so there is no database password to leak.

---

## F-10 — Containers run as root  🟡 MEDIUM

Both Dockerfiles:

```dockerfile
RUN useradd -m appuser && chown -R appuser /app
# USER appuser
```

The `USER` directive is commented out, so the user is created and never used. Combined
with a single-stage `python:3.11-slim` image carrying a full toolchain, a container
compromise starts with root and build tools available.

**Target control:** distroless multi-stage build, `runAsNonRoot: true`,
`readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, all dropped
capabilities — enforced cluster-wide by Azure Policy for AKS rather than trusted to the
Dockerfile.

---

## F-11 — Silent SQLite fallback in production  🟡 MEDIUM

```python
try:
    socket.gethostbyname(db_host)
except socket.error:
    print(f"Warning: Could not resolve DB_HOST '{db_host}'. Falling back to SQLite.")
    use_sqlite = True
```

A transient DNS failure in production causes the app to **silently start against an
empty, ephemeral, pod-local SQLite file.** `seed.py` then populates it with default
accounts and `password123`. The service returns HTTP 200, `/health` reports `ok`, and
every replica now holds a divergent ledger that vanishes on restart.

This is arguably the most dangerous availability defect in the codebase, because it
converts a detectable outage into silent, unrecoverable data divergence.

**Target control:** fail fast and loudly. No fallback driver. `/health` distinguishes
liveness from readiness and readiness fails closed on a broken DB dependency, so the pod
leaves the load-balancer rotation instead of serving wrong data.

---

## F-12 — Plaintext Kubernetes Secret in git  🟡 MEDIUM

`banking-app/k8s/secret.yaml` uses `stringData` with placeholder-but-real-shaped values,
establishing a pattern where credentials live in manifests. `k8s/service.yaml` also uses
`type: LoadBalancer`, which assigns a **public IP directly to the payment service**,
bypassing any WAF or gateway.

**Target control:** Key Vault + Secrets Store CSI driver, or External Secrets Operator.
Services are `ClusterIP` only; the sole ingress path is Front Door → Private Link → APIM.

---

## F-13 — No rate limiting, fraud controls, or AML hooks  🟡 MEDIUM

`/pay` and `/login` accept unlimited attempts. There is no velocity checking, no device
fingerprinting, no anomaly scoring, no sanctions/PEP screening, and no covered- or
suspicious-transaction reporting.

For a BSP-supervised institution this is not merely a hardening gap — AMLA covered
transaction reporting and the customer-protection duties under the Anti-Financial
Account Scamming Act are statutory obligations.

**Target control:** Front Door WAF rate limiting at the edge, APIM `rate-limit-by-key`
per subject, plus dedicated `fraud-service` and `aml-service` in the payment path. See
[bsp-compliance-matrix.md](bsp-compliance-matrix.md).

---

## F-14 — No observability  🟡 MEDIUM

Diagnostics are `print()` to stdout. There is no structured logging, no correlation ID
propagated across the two services, no metrics, no tracing, and no audit trail beyond
the `transactions` table — which is mutable.

An examiner asking "show me everything that happened to this account on this date"
cannot be answered.

**Target control:** OpenTelemetry → Azure Monitor / App Insights, hash-chained audit
events to immutable WORM storage with a 7-year retention policy, receipts anchored in
Azure Confidential Ledger, and Microsoft Sentinel as SIEM.

---

## Severity summary

| ID | Finding | Severity | Impact |
|---|---|---|---|
| F-01 | Unauthenticated `/paid` endpoint | 🔴 Critical | Free goods, no payment |
| F-02 | Client-supplied payment amount | 🔴 Critical | Pay ₱0.01 for any order |
| F-03 | Unsigned QR payload | 🔴 Critical | Redirect funds, revive expired QR |
| F-04 | Callback before debit | 🔴 Critical | Paid orders with no funds moved |
| F-05 | Double-spend race | 🟠 High | Negative balances, duplicate tx |
| F-06 | Float money columns | 🟠 High | Ledger will not reconcile |
| F-07 | Plaintext passwords | 🟠 High | Full credential compromise |
| F-08 | Hardcoded secret keys | 🟠 High | Forge admin session, mint funds |
| F-09 | Live DB creds in public git | 🟠 High | Direct production DB access |
| F-10 | Containers as root | 🟡 Medium | Escalated container breakout |
| F-11 | Silent SQLite fallback | 🟡 Medium | Silent ledger divergence |
| F-12 | Plaintext K8s Secret, public LB | 🟡 Medium | Secret sprawl, WAF bypass |
| F-13 | No rate limit / fraud / AML | 🟡 Medium | Statutory non-compliance |
| F-14 | No observability | 🟡 Medium | Cannot answer an audit |

**F-01 through F-04 are chainable.** An attacker combining them acquires merchandise for
free while redirecting any payment that does occur to an account they control, and the
merchant's ledger will not reveal the discrepancy because it never reconciled to begin
with.
