# QR Payment Prototype

A two-app Flask system demonstrating a QR-code-based payment flow, containerised with Docker and deployed behind Nginx.

## Architecture

```
                     ┌──────────────────────┐
  Customer ────80───►│   Nginx (port 80)    │
                     │   reverse proxy      │
                     └──┬──────────────┬────┘
          shop.*        │              │        bank.*
              ┌─────────┘              └─────────┐
              ▼                                  ▼
    ┌──────────────────┐              ┌──────────────────┐
    │ E-commerce :5000 │              │  Banking  :5001  │
    │ (grocery app     │   callback   │  (SQLAlchemy +   │
    │           shop)  │◄─────────────│   MySQL)         │
    └──────────────────┘              └────────┬─────────┘
                                               │
                                        ┌──────┴──────┐
                                        │ MySQL :3306 │
                                        └─────────────┘
```

### Flow
1. Customer clicks **Buy** on the e-commerce shop.
2. A QR code is displayed containing a payment URL.
3. Customer scans the QR code (or clicks **Simulate Scanning**).
4. Banking app shows a payment confirmation page; customer selects an account and confirms.
5. Banking app debits the consumer, credits the merchant, and calls back e-commerce.
6. Checkout page updates to **PAID** via AJAX (no page reload).

## Quick Start (Local Dev)

```bash
# 1. Copy the environment template
cp .env.example .env      # edit VM_IP if deploying on a remote VM

# 2. Start everything
docker compose up -d --build

# 3. Verify
docker compose ps          # all containers should be running/healthy
```

### Access the Apps

| App | Local URL |
|-----|-----------|
| Shop | [http://shop.127-0-0-1.nip.io](http://shop.127-0-0-1.nip.io) |
| Bank Dashboard | [http://bank.127-0-0-1.nip.io/accounts](http://bank.127-0-0-1.nip.io/accounts) |
| Adminer (dev only) | [http://localhost:8080](http://localhost:8080) (via SSH tunnel) |

> **Deploying on a VM?** Replace `127-0-0-1` with your VM's IP (dashes, not dots).  
> For example: `shop.20-51-32-10.nip.io`. Set `VM_IP=20-51-32-10` in `.env`.

## Project Structure

```
├── banking-app/           # Flask banking API + dashboard
│   ├── app.py             # Routes: /accounts, /pay, /health
│   ├── models.py          # SQLAlchemy models (Account, Transaction)
│   ├── seed.py            # Idempotent DB seeding
│   ├── templates/         # Jinja2 HTML templates
│   ├── Dockerfile
│   ├── Jenkinsfile        # CI/CD pipeline definition
│   ├── k8s/               # Kubernetes manifests (prod)
│   └── requirements.txt
├── ecommerce-app/         # Flask e-commerce storefront
│   ├── app.py             # Routes: /, /buy, /checkout, /qr, /api
│   ├── templates/         # Jinja2 HTML templates
│   ├── Dockerfile
│   ├── Jenkinsfile
│   ├── k8s/               # Kubernetes manifests (prod)
│   └── requirements.txt
├── nginx/
│   └── nginx.conf         # Reverse proxy config (shop.* → ecom, bank.* → banking)
├── docker-compose.yml     # Dev environment orchestration
├── .env.example           # Environment variable template
└── .gitignore
```

## Environment Variables

All configuration is via environment variables (no hardcoded secrets).  
See [`.env.example`](.env.example) for the full list.

| Variable | Used By | Default | Description |
|----------|---------|---------|-------------|
| `VM_IP` | docker-compose | `127-0-0-1` | VM public IP with dashes for nip.io routing |
| `DB_HOST` | banking-app | `mysql` | MySQL hostname (Docker service name) |
| `DB_NAME` | banking-app, mysql | `bankdb` | Database name |
| `DB_USER` | banking-app, mysql | `bankuser` | Database user |
| `DB_PASSWORD` | banking-app, mysql | `devpass` | Database password |

## CI/CD & Deployment

See the per-app `Jenkinsfile` for the pipeline stages:
1. **Build & Unit Test** → 2. **Docker Build & Push** → 3. **Deploy to Test (ACI)** → 4. **Smoke Test** → 5. **Approve** → 6. **Deploy to Prod (K8s)**

## Ground Rules

- **Keep app code minimal** — focus is on DevOps, not features.
- **Commit small and often** — every push to `main` runs the pipeline.
- **No secrets in Git** — use `.env`, Jenkins Credentials, or K8s Secrets.
- **No manual DB steps** — all schema/data from `seed.py`.
- **Adminer is dev-only** — never in Test or Prod.
