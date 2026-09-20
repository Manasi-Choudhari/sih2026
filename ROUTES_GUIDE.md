# VAJRA (SIH 26183) — Routes, Links & 404 Diagnosis Guide

A quick-reference guide for all frontend pages, scenario URLs, backend endpoints, and verified routing status.

---

## 1. Route Diagnostics & Prevention of 404 Errors

All core routes and fallback redirects are fully active:

| Path | Behavior & Resolution | Status |
| :--- | :--- | :--- |
| **Direct Case Access** (`/cases/case_s1`) | Automatically redirects to `/cases/case_s1/overview` via `frontend/app/cases/[id]/page.tsx`. | 🟢 Fixed (Redirects 200) |
| **Cases Root** (`/cases`) | Automatically redirects to `/queue` via `frontend/app/cases/page.tsx`. | 🟢 Fixed (Redirects 200) |
| **Case Report Page** (`/cases/[id]/report`) | Fully rendered Section 65B-compliant printable institutional dossier with cryptographic verification seal. | 🟢 Working (200 OK) |
| **Backend Report API** (`/cases/{id}/report`) | Supports both `GET` (direct browser/inspection query) and `POST` (report generation with hash). | 🟢 Working (200 OK) |
| **Sidebar "Reports" Link** | Dynamically resolves to `/cases/{firstCaseId}/report` (or `/queue` if empty). | 🟢 Working (200 OK) |

---

## 2. Core Frontend Route Architecture (`http://localhost:3000`)

### Global Pages
* **Main Portal / Root:** `http://localhost:3000/` *(Redirects to `/login` if unauthenticated, `/queue` if authenticated)*
* **Login Terminal:** `http://localhost:3000/login`
* **Investigation Master Queue:** `http://localhost:3000/queue`
* **Direct Case Fallback:** `http://localhost:3000/cases/[id]` *(Auto-redirects to `/cases/[id]/overview`)*

### The 8 Functional Sub-Routes per Case (`/cases/[id]/...`)
Each case ID (e.g., `case_s1`, `case_s2`, `case_s3`, `case_s4`, `case_s5`) provides 8 distinct sub-pages:

1. **Overview:** `/cases/[id]/overview` — Executive summary, Three-Number Confidence Strip (Rule Risk, Attribution, ML Anomaly), victim details.
2. **Standardized Legal Report:** `/cases/[id]/report` — Section 65B Indian Evidence Act compliant report generator, printable institutional dossier, cryptographic hash seal.
3. **Trace Graph:** `/cases/[id]/graph` — Interactive multi-hop transaction graph canvas (ReactFlow).
4. **VASP Attribution:** `/cases/[id]/attribution` — 4-tier evidence candidate cards, corroboration scores, money-laundering pattern classifications.
5. **ATLAS Challenge Engine:** `/cases/[id]/atlas` — Adversarial counterfactual testing disproving false attribution leads.
6. **Evidence Ledger:** `/cases/[id]/evidence` — Tamper-evident SHA-256 hash-chained log with live cryptographic verification.
7. **Action Recommendations:** `/cases/[id]/recommendations` — Prioritized next investigation steps with supervisor approval gate.
8. **Audit Trail:** `/cases/[id]/audit` — Chronological record of user queries, approvals, and legal notices issued.

---

## 3. Complete Test Scenario URL Matrix

All 40 sub-routes across the 5 synthetic scenarios have been tested and verified:

| Scenario | Overview | Legal Report | Trace Graph | Attribution | ATLAS | Evidence | Recommendations | Audit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Scenario 1: Direct VASP** (`case_s1`) | [/overview](http://localhost:3000/cases/case_s1/overview) | [/report](http://localhost:3000/cases/case_s1/report) | [/graph](http://localhost:3000/cases/case_s1/graph) | [/attribution](http://localhost:3000/cases/case_s1/attribution) | [/atlas](http://localhost:3000/cases/case_s1/atlas) | [/evidence](http://localhost:3000/cases/case_s1/evidence) | [/recommendations](http://localhost:3000/cases/case_s1/recommendations) | [/audit](http://localhost:3000/cases/case_s1/audit) |
| **Scenario 2: Peel Chain** (`case_s2`) | [/overview](http://localhost:3000/cases/case_s2/overview) | [/report](http://localhost:3000/cases/case_s2/report) | [/graph](http://localhost:3000/cases/case_s2/graph) | [/attribution](http://localhost:3000/cases/case_s2/attribution) | [/atlas](http://localhost:3000/cases/case_s2/atlas) | [/evidence](http://localhost:3000/cases/case_s2/evidence) | [/recommendations](http://localhost:3000/cases/case_s2/recommendations) | [/audit](http://localhost:3000/cases/case_s2/audit) |
| **Scenario 3: Cross-Chain** (`case_s3`) | [/overview](http://localhost:3000/cases/case_s3/overview) | [/report](http://localhost:3000/cases/case_s3/report) | [/graph](http://localhost:3000/cases/case_s3/graph) | [/attribution](http://localhost:3000/cases/case_s3/attribution) | [/atlas](http://localhost:3000/cases/case_s3/atlas) | [/evidence](http://localhost:3000/cases/case_s3/evidence) | [/recommendations](http://localhost:3000/cases/case_s3/recommendations) | [/audit](http://localhost:3000/cases/case_s3/audit) |
| **Scenario 4: Mixer Hop** (`case_s4`) | [/overview](http://localhost:3000/cases/case_s4/overview) | [/report](http://localhost:3000/cases/case_s4/report) | [/graph](http://localhost:3000/cases/case_s4/graph) | [/attribution](http://localhost:3000/cases/case_s4/attribution) | [/atlas](http://localhost:3000/cases/case_s4/atlas) | [/evidence](http://localhost:3000/cases/case_s4/evidence) | [/recommendations](http://localhost:3000/cases/case_s4/recommendations) | [/audit](http://localhost:3000/cases/case_s4/audit) |
| **Scenario 5: Conflicting Labels** (`case_s5`) | [/overview](http://localhost:3000/cases/case_s5/overview) | [/report](http://localhost:3000/cases/case_s5/report) | [/graph](http://localhost:3000/cases/case_s5/graph) | [/attribution](http://localhost:3000/cases/case_s5/attribution) | [/atlas](http://localhost:3000/cases/case_s5/atlas) | [/evidence](http://localhost:3000/cases/case_s5/evidence) | [/recommendations](http://localhost:3000/cases/case_s5/recommendations) | [/audit](http://localhost:3000/cases/case_s5/audit) |

---

## 4. Backend API Endpoints Reference (`http://localhost:8000`)

* **Interactive OpenAPI Swagger Docs:** `http://localhost:8000/docs`
* **ReDoc Documentation:** `http://localhost:8000/redoc`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Operational status check |
| `POST` | `/auth/login` | Issues investigator/supervisor JWT |
| `GET` | `/cases` | Lists cases in queue |
| `POST` | `/cases` | Ingests new victim complaint |
| `GET` | `/cases/{id}` | Fetches individual case details |
| `GET` | `/cases/{id}/graph` | Returns multi-hop trace graph nodes & edges |
| `GET` | `/cases/{id}/attribution` | Returns VASP candidates and detected patterns |
| `GET` | `/cases/{id}/atlas` | Runs adversarial counterfactual challenges |
| `GET` | `/cases/{id}/evidence` | Returns evidence ledger records |
| `GET` | `/cases/{id}/verify` | Cryptographically validates SHA-256 hash chain integrity |
| `GET` | `/cases/{id}/recommendations` | Returns prioritized investigation recommendations |
| `POST` | `/cases/{id}/recommendations` | Approves or rejects a recommendation |
| `GET` | `/cases/{id}/actions` | Ranks actionable next steps |
| `GET` / `POST` | `/cases/{id}/report` | Generates standardized legal report & content hash |
| `GET` | `/cases/{id}/audit` | Returns chronological audit log events |
| `POST` | `/external/case-update` | Ingests simulated NCRP/Sahyog external callbacks |
| `POST` | `/cases/simulate/ncrp-intake` | Simulates live 1930 / NCRP cyber fraud complaint webhook |
| `POST` | `/external/ncrp/webhook` | Receives live NCRP complaint payloads |
