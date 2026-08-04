# Compliance Traceability — Philippines

> **Read this first.** The regulatory references below were checked against BSP's public
> issuance site while writing this document, but BSP amends these instruments frequently
> — several relevant circulars were issued or amended during 2025–2026. **Treat this as an
> engineering-side mapping, not a legal opinion.** Every citation must be confirmed with
> the institution's compliance office and legal counsel before it is relied on in a
> regulatory filing or examination response.
>
> Where I could not verify an instrument's exact subject matter, I have said so rather
> than guessed. In particular, my first pass at this review cited "Circular 1085" as the
> cloud computing circular; I was not able to verify that attribution, so it has been
> removed and replaced with the outsourcing and information-security instruments I could
> confirm.

---

## Verified regulatory instruments

| Instrument | Subject | Verified |
|---|---|---|
| [Circular 1055 (2019)](http://www.bsp.gov.ph/Regulations/Issuances/2019/c1055.pdf) | National QR Code Standard — QR Ph, EMVCo-based; adoption required of participating PSPs | ✅ |
| [Circular 1198 (2024)](https://www.bsp.gov.ph/Regulations/Issuances/2024/1198.pdf) | Regulatory framework for Merchant Payment Acceptance Activities; licensing/registration for Operators of Payment Systems, settlement, IT, AML/CTF/CPF, end-user protection | ✅ |
| [Circular 1140 (2022)](https://www.bsp.gov.ph/Regulations/Issuances/2022/1140.pdf) + [M-2022-046](https://www.bsp.gov.ph/Regulations/Issuances/2022/M-2022-046.pdf) | Risk-based approach to technology outsourcing, aligned to international practice | ✅ |
| [Circular 1213 (2025)](https://www.bsp.gov.ph/Regulations/Issuances/2025/1213.pdf) | Implements RA 12010, the Anti-Financial Account Scamming Act (AFASA) | ✅ |
| [Circular 1232 (2026)](https://www.bsp.gov.ph/Regulations/Issuances/2026/1232%20(corrected%20copy).pdf) | Periodic, rigorous information-security risk self-assessment using robust data sets | ✅ |
| [MORB Appendix 75](https://www.bsp.gov.ph/Regulations/MORB/2023_MORB/2023_MORB_Appendices/2023%20App%20075.pdf) | Information security risk management; integration with enterprise-wide risk management | ✅ |
| [M-2026-034](https://www.bsp.gov.ph/Regulations/Issuances/2026/M-2026-034.pdf) | Managing emerging risks from frontier AI systems; cyber-hygiene resilience against AI-enabled threats | ✅ |
| Circular 808 (2013) | IT Risk Management framework | Widely cited; confirm current amended text |
| Circular 982 (2017) | Enhanced information security management guidelines | Widely cited; confirm current amended text |

Statutes: RA 11127 (National Payment Systems Act), RA 10173 (Data Privacy Act),
RA 9160 as amended (AMLA), RA 12010 (AFASA), RA 8792 (E-Commerce Act).
Industry: PCI DSS 4.0 where card data is in scope.

---

## Control mapping

### Information security risk management — Appendix 75, C808, C982, C1232

| Requirement | Current | Target | Azure control |
|---|---|---|---|
| Encryption in transit | ❌ HTTP :80 throughout; QR payload is an `http://` URL | ✅ | TLS 1.3 at Front Door; Istio mTLS STRICT in-mesh; private endpoints for all data services |
| Encryption at rest | ❌ Not configured | ✅ | Platform encryption + customer-managed keys from Key Vault Managed HSM (FIPS 140-3 L3) |
| Key management | ❌ Signing keys hardcoded in source (F-08) | ✅ | Managed HSM, non-exportable keys, automated rotation, no key material in application config |
| Authentication | ❌ Plaintext password `==` compare, no MFA, no lockout (F-07) | ✅ | Entra External ID, MFA, passkeys/FIDO2, Conditional Access, risk-based step-up |
| Privileged access | ❌ `is_admin` boolean on a user row; forgeable session (F-08) | ✅ | Entra PIM just-in-time elevation, Azure Bastion, no standing admin, no SSH keys |
| Network segmentation | ❌ Flat; `type: LoadBalancer` gives the payment service a public IP (F-12) | ✅ | Hub-and-spoke, private AKS, Cilium default-deny NetworkPolicy, Azure Firewall Premium egress IDPS |
| Audit logging | ❌ `print()` to stdout; `transactions` table is mutable (F-14) | ✅ | OpenTelemetry → Azure Monitor; hash-chained audit events; ADLS WORM + legal hold, 7 years; Confidential Ledger anchor |
| Vulnerability management | ❌ No scanning; unsigned Docker Hub `:latest` | ✅ | Trivy + Defender for Containers, quarantine-until-scanned ACR, Notation signing, Ratify admission enforcement |
| Secure SDLC | ❌ No SAST/DAST/SCA | ✅ | CodeQL, Dependabot, OWASP ZAP in SIT, annual VAPT, OPA policy-as-code on IaC |
| Periodic self-assessment (C1232) | ❌ None | ✅ | Defender for Cloud secure score + Azure Policy compliance as the evidence data set; scheduled attestation reporting |
| AI-enabled threat resilience (M-2026-034) | ❌ None | ✅ | Sentinel UEBA, Defender for APIs anomaly detection, WAF bot manager, Chaos Studio validation |

### Technology outsourcing and cloud — C1140, M-2022-046

| Requirement | Design response |
|---|---|
| Business case and risk assessment before outsourcing | Documented in this architecture set; per-service data classification via Microsoft Purview |
| Provider due diligence | Azure SOC 1/2/3, ISO 27001/27017/27018, PCI DSS attestations; Microsoft's [PH FSI compliance checklist](https://download.microsoft.com/download/F/1/1/F11BF195-2233-479C-8AAD-868EBF328E33/Microsoft.FSI.Checklist.O365.Philippines.pdf) |
| BSP right to examine | In-country WORM archival copy in PH co-location; Azure Monitor/Sentinel export for examiner access |
| Exit strategy / avoid lock-in | Kubernetes + PostgreSQL + Terraform. Portable by construction. Contrast with the current ACI + `az` CLI imperative deployment, which is not. |
| Sub-contractor transparency | Azure sub-processor list; Purview data map records residency lineage |
| Business continuity | Multi-region warm standby, RPO ≤ 60 s / RTO ≤ 15 min, quarterly drills evidenced via Chaos Studio |
| Concentration risk | Explicitly accepted single-cloud, mitigated by multi-region + portable stack + in-country archive. Note this is a **reduction** in provider count from the current AWS + Azure + Docker Hub spread. |

### QR Ph — Circular 1055

| Requirement | Current | Target |
|---|---|---|
| EMVCo-based QR Ph standard | ❌ Encodes an arbitrary HTTP URL — not QR Ph, not interoperable with any other PH wallet | ✅ EMVCo TLV with CRC16, registered merchant identifiers |
| Payload integrity | ❌ `amount`, `merchant_account`, `expires` are unsigned, editable query parameters (F-02, F-03) | ✅ Detached JWS signed by non-exportable Managed HSM key; QR carries an order reference only |
| Interoperability | ❌ Only this bank's own app can read it | ✅ Conformant to the national standard |

### Merchant payment acceptance — Circular 1198

| Requirement | Current | Target |
|---|---|---|
| Merchant onboarding and due diligence | ❌ Merchants are rows created by `seed.py`; unknown merchant IDs silently fall back to `jmb-grocery` | ✅ `account-service` merchant registry with KYC tier and limits; unknown merchant is a hard reject |
| Settlement discipline | ❌ Balance columns mutated in place; no settlement concept | ✅ `settlement-service` with InstaPay/PESONet netting; `reconciliation-service` EOD sweep |
| End-user protection / dispute handling | ❌ None | ✅ `reversal-service` for compensating entries and chargebacks; notification trail |
| Transaction record integrity | ❌ Float amounts that will not reconcile (F-06) | ✅ Double-entry `NUMERIC(19,4)` append-only journal with a zero-sum constraint |

### AML/CTF — RA 9160 as amended, C1198

| Requirement | Current | Target |
|---|---|---|
| Covered transaction reporting | ❌ None | ✅ `aml-service` auto-generates CTR at the statutory threshold; confirm current threshold and filing window with compliance |
| Suspicious transaction reporting | ❌ None | ✅ Rule + ML detection, STR workflow, AMLC submission via `reporting-service` |
| Sanctions / PEP screening | ❌ None | ✅ Screening on both parties before the ledger posting |
| Record keeping | ❌ Mutable table, no retention policy | ✅ WORM immutable, 7 years, legal hold |

### AFASA — RA 12010, Circular 1213

| Requirement | Current | Target |
|---|---|---|
| Fraud monitoring and detection | ❌ None | ✅ `fraud-service`: velocity limits, device fingerprint, anomaly scoring, step-up auth |
| Mule account detection | ❌ None | ✅ Graph-based counterparty analysis, Sentinel UEBA |
| Customer notification | ❌ None | ✅ `notification-service` real-time transaction alerts |
| Ability to restrict accounts | ❌ None | ✅ `account-service` hold/freeze states honoured by the ledger before posting |

### Data Privacy Act — RA 10173

| Requirement | Current | Target |
|---|---|---|
| Lawful cross-border transfer | ❌ Data in `centralindia` with no documented basis | ⚠️ **Open item.** Azure has no PH region, so a cross-border basis is mandatory. Requires NPC-compliant transfer mechanism + documented processing agreement. Must be resolved before go-live. |
| Data classification and inventory | ❌ None | ✅ Microsoft Purview classification, data map, residency lineage |
| Consent management | ❌ None | ✅ `consent-service` consent ledger |
| Breach notification (72 h) | ❌ No detection capability at all | ✅ Sentinel SOAR playbooks with NPC notification workflow |
| Privacy by design | ❌ Full PII in logs via `print()` | ✅ Structured logging with PII redaction; tokenisation of identifiers |

### PCI DSS 4.0 — if and when card data enters scope

Not currently in scope: the prototype handles account-to-account transfers, not cards. If
card funding is added, Requirements 1–12 map to the Azure controls already described,
and the recommended posture is to keep the cardholder data environment out of scope
entirely by using a tokenising acquirer rather than storing PANs.

---

## Blocking items before any production consideration

1. **Rotate and purge the credential in `Jenkinsfile`** (F-09). It is in public git
   history. Rotation alone is insufficient — history must be rewritten.
2. **Fix F-01 through F-04.** These are exploitable for direct financial loss and are
   independent of any cloud migration.
3. **Establish the cross-border data transfer basis** under the DPA. Azure has no PH
   region; this cannot be engineered around and must be resolved on the legal side.
4. **Confirm the licensing position under Circular 1198.** Operating merchant payment
   acceptance may require registration or licensing as an Operator of Payment System.
   This is a prerequisite to launch, not a technical control.
