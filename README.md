# 🛡️ PROJECT VAJRA — Real-Time Cryptocurrency Cyber Fraud Attribution Platform

> **Smart India Hackathon (SIH 2026 / Problem Statement ID: 26183)**  
> **Target Problem**: Automated tracing of illicit cryptocurrency fund flows from Citizen Complaints (NCRP Helpline 1930 / CFCFRMS), multi-hop VASP attribution, counter-hypothesis stress-testing, and statutory Section 91 Cr.P.C. enforcement dossier generation within the Golden 24-Hour recovery window.

---

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [System Architecture & Data Flow](#-system-architecture--data-flow)
- [Visual Product Tour & Screenshots](#-visual-product-tour--screenshots)
- [Core Innovation & 3-Number Framework](#-core-innovation--the-3-number-confidence-framework)
- [Quickstart & Local Setup Guide](#-quickstart--local-setup-guide)
- [Demo Scenarios & Testing Wallets](#-demo-scenarios--testing-wallets)
- [Demo Video & Recording Playbook](#-demo-video--recording-playbook)
- [Repository Structure](#-repository-structure)
- [API Reference & Route Map](#-api-reference--route-map)
- [Compliance & Legal Framework](#-compliance--legal-framework)

---

## 🏛️ Executive Overview

Every year, over **₹1,000 Crore** is siphoned away in cryptocurrency scams reported to India's **National Cybercrime Reporting Portal (NCRP) / Helpline 1930**. When victims report a wallet drain, cyber investigators face an uphill battle:
- Fraudsters use **peel chains**, **cross-chain bridges**, and **mixing protocols** to obfuscate transactions across multiple hops.
- Manual tracing on disparate public explorers takes **24 to 48 hours**, allowing criminals to liquidate stolen funds on off-shore exchanges before freeze notices can be dispatched.
- Generic AI scores are often rejected by Indian courts because they fail to meet the strict evidentiary standards of the **Indian Evidence Act** and **Section 91 Cr.P.C.**.

**Project VAJRA** solves this by compressing the 48-hour manual investigation cycle into **under 10 seconds**:
1. **Zero-Second Intake**: Ingests citizen fraud complaints via bi-directional webhook synchronization with NCRP / CFCFRMS.
2. **Autonomous Multi-Hop Tracing**: Bounded BFS graph exploration with live **Etherscan V2 API** streaming (`EXPLORER_API_KEY_ETH`) and UTXO Bitcoin support.
3. **Three-Number Confidence Model**: Separates deterministic rule risk, corroboration-weighted attribution, and GPU XGBoost ML velocity anomaly signals.
4. **ATLAS Counter-Hypothesis Engine**: Automatically stress-tests attribution against competing explanations (Permit2 drainers, internal exchange sweeps, OTC settlements) to prepare for court cross-examination.
5. **Tamper-Evident Ledger**: Appends each forensic artifact to a cryptographically sealed SHA-256 hash chain.
6. **1-Click Statutory Freeze Packet**: Auto-drafts Section 91 Cr.P.C. production and freeze notices and exports an institutional, court-ready PDF dossier.

---

## 🔄 System Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CITIZEN & POLICE INTAKE GATEWAY (/ncrp)                                   │
│    • 1930 CFCFRMS Complaint Registration (ETH / BTC / USDT)                 │
│    • 1-Click Typology Presets (Phishing, Peel Chain, Bridge, Mixer)         │
│    • Custom Manual Filing Mode (Arbitrary live wallets)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ POST /api/v1/external/ncrp/webhook
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. VAJRA INGESTION & TRIAGE GATEWAY (backend/external/ncrp_sync.py)          │
│    • Payload normalization & reverse callback generation                    │
│    • Immediate Complaint Acknowledgment Slip issuance (2026/NCRP/DL/xxxxxx)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Auto-poll sync
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. REAL-TIME INVESTIGATION QUEUE (/queue)                                   │
│    • Live auto-polling intake without page reloads                          │
│    • Priority sorting by fraud amount and drain velocity                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ 1-Click Case Opening
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. FORENSIC TRACING & MULTI-TIER REASONING (/cases/[id]/overview)           │
│    • Live Blockchain Adapters: Etherscan V2 API (ETH) & Blockchair (BTC)   │
│    • Bounded BFS Graph Engine + Neo4j Cypher Traversal                      │
│    • 3-Number Metric Framework:                                             │
│      ├── Deterministic Rule Risk Score (0.00 – 1.00)                        │
│      ├── Corroboration-Weighted Attribution Confidence (0 – 100%)           │
│      └── GPU XGBoost ML Anomaly Probability (CUDA Accelerated)              │
│    • ATLAS Counter-Hypothesis Stress-Testing (Permit2 vs Sweep vs OTC)      │
│    • SHA-256 Tamper-Evident Evidence Ledger                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Generate Dossier
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. STATUTORY ENFORCEMENT & DOSSIER GENERATION (/cases/[id]/report)          │
│    • Instant Section 91 Cr.P.C. Statutory Notice Draft                      │
│    • Pure Client-Side PDF 1.4 Binary Generator                              │
│    • Instant Download: VAJRA_Investigation_Dossier_[case_id].pdf            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📸 Visual Product Tour & Screenshots

### 1. National Cybercrime Reporting Portal (NCRP / 1930) Integration
High-fidelity Indian Government portal UI styled to match the Ministry of Home Affairs (MHA), Indian Cybercrime Coordination Centre (I4C), and the 1930 National Helpline. Includes 1-click test typology presets and manual custom filing.
![NCRP Portal](docs/screenshots/01_ncrp_portal.png)

---

### 2. Zero-Second Triage & Official CFCFRMS Acknowledgment Receipt
Upon submitting a suspect wallet, the webhook executes live multi-hop tracing, computes initial risk metrics, and returns the official acknowledgment slip with Complaint Ack Number.
![NCRP Acknowledgment Receipt](docs/screenshots/02_ncrp_acknowledgment.png)

---

### 3. Real-Time Auto-Refreshing Officer Queue (`/queue`)
Newly lodged complaints automatically populate into the officer's queue without manual page reload, labeled with **NCRP Gateway Live** and priority tags.
![Investigation Queue](docs/screenshots/03_investigation_queue.png)

---

### 4. Interactive Multi-Hop Forensics Graph & Exchange Attribution
The core visual forensics suite. Shows the complete path from the Victim Origin Node through intermediary layering hops into **Binance (Hot Wallet 14)** with live Etherscan node synchronization.
![Case Overview Graph](docs/screenshots/04_case_overview_graph.png)

---

### 5. Mixer Boundary Obstruction & ATLAS Legal Stress-Testing
When illicit funds hit a zero-knowledge mixing protocol (e.g. Tornado Cash), the ATLAS engine evaluates competing hypotheses (anonymity set dilution, gas relayer skimming, corporate privacy) and calculates evidentiary robustness.
![Mixer Boundary ATLAS](docs/screenshots/05_mixer_boundary_atlas.png)

---

### 6. Standardized Investigation Report & Section 91 Cr.P.C. PDF Dossier
Transforms complex graph data into an institutional legal packet. Includes an integrated client-side PDF generator that exports court-ready dossiers with cryptographic hashes and signature blocks.
![Investigation Report](docs/screenshots/06_investigation_report_dossier.png)

---

### 7. Custom Manual Complaint Lodging Mode
Allows cyber cell investigators to clear presets and enter arbitrary suspect wallets (e.g., live Ethereum mainnet addresses to query via Etherscan API key).
![Manual Complaint Entry](docs/screenshots/07_ncrp_manual_entry.png)

---

## 🎯 Core Innovation — The 3-Number Confidence Framework

Standard black-box AI tools output a single arbitrary percentage (e.g. *"91% Fraud"*), which defense attorneys easily dispute in court. VAJRA enforces a strict **Three-Number Confidence Architecture**:

| Metric | Type | Purpose | Judicial Role |
|---|---|---|---|
| **1. Rule Risk Score** | Deterministic | Evaluates topological graph rules (hop count, flow preservation, rapid dispersal). | **Legal Baseline** — Always repeatable, verifiable under Section 65B of the Evidence Act. |
| **2. Attribution Confidence** | Corroboration-based | Measures path directness and known VASP cluster registry certainty. | **Custodian Actionability** — Determines whether a Section 91 CrPC notice can be legally served. |
| **3. ML Anomaly Probability** | Statistical (XGBoost GPU) | Evaluates transaction velocity, dormant activation, and degree metrics. | **Investigator Prioritization** — Ranks queue triage without dictating the legal outcome. |

---

## 🚀 Quickstart & Local Setup Guide

### System Prerequisites
- **Node.js**: `v18.x` or `v20.x` (`npm` included)
- **Python**: `3.10+`
- **Neo4j Database**: Desktop or Docker running with Bolt port `7687` open
- **API Keys**: Etherscan API Key (Free tier at [etherscan.io](https://etherscan.io))

---

### Step 1: Clone Repository & Configure Environment

```bash
git clone https://github.com/Manasi-Choudhari/sih2026.git
cd sih2026
```

Copy the environment template to create `.env`:
```bash
copy .env.example .env
```

Ensure `.env` contains your database and API credentials:
```env
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=sih2026
NEO4J_INSTANCE=sih2026

MODEL_ARTIFACT_PATH=ml/artifacts
ML_DEVICE=cpu

# Live Ethereum Explorer API Key (Etherscan V2)
EXPLORER_API_KEY_ETH=BBCDM1DZ3UECMSKX7JXD3FJNEG1DXKR2FH
EXPLORER_API_KEY_BTC=
```

---

### Step 2: Set Up & Launch the Backend Server

Open a terminal at the project root:

```powershell
# 1. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
pip install -r blockchain/requirements.txt

# 3. Seed Neo4j graph fixtures (Optional if already seeded)
python seed_neo4j_only.py

# 4. Launch backend daemon (FastAPI on Port 8000)
cmd /c run_backend.cmd
```
*Backend runs on `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

---

### Step 3: Set Up & Launch the Frontend Console

Open a second terminal at the project root:

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Launch Next.js dev server
npm run dev
```
*Frontend runs on `http://localhost:3000`.*

---

### Step 4: Access VAJRA

- **Citizen & Helpline 1930 Portal**: [`http://localhost:3000/ncrp`](http://localhost:3000/ncrp)
- **Officer Investigation Queue**: [`http://localhost:3000/queue`](http://localhost:3000/queue)
- **Interactive Forensics Case Overview**: [`http://localhost:3000/cases/case_s1/overview`](http://localhost:3000/cases/case_s1/overview)
- **Investigation Report & PDF Dossier**: [`http://localhost:3000/cases/case_s1/report`](http://localhost:3000/cases/case_s1/report)

---

## 🧪 Demo Scenarios & Testing Wallets

For live demonstrations and evaluators, use the verified blockchain coordinates in [`TESTING_WALLETS.md`](TESTING_WALLETS.md):

| Scenario | Protocol | Suspect Wallet | Victim Wallet | Attribution Target |
|---|:---:|---|---|---|
| **S1: Phishing & Seed Drain** | `ETH` | `0x71C67930752b516538b1d97767F296aD55836882` | `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` | **Binance (Hot Wallet 14)** (95% Conf) |
| **S2: Bitcoin Peel Chain** | `BTC` | `bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh` | `bc1q9victimfakeaddress00188924018241` | **3-Hop Change Peeling** (72% Conf) |
| **S3: Cross-Chain Bridge** | `BTC/ETH` | `bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksns5` | `bc1qvictimtask9948281047192` | **WBTC Liquidity Bridge Gateway** |
| **S4: Mixer Boundary Obstruction**| `BTC` | `bc1q5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge` | `bc1qextortvictimwallet11029` | **Tornado Cash / Mixer Boundary** |
| **S5: Indian VASP Direct Freeze** | `ETH` | `0x503828976d22510aad0201ac7ec88293211d23da` | `0x71C67930752b516538b1d97767F296aD55836882` | **CoinDCX India / WazirX (FIU-IND)** |

---

## 🎬 Demo Video & Recording Playbook

We have incorporated the **`demo-video-playbook`** skill to produce a complete recording package:
- 📹 **Full HD 1080p MP4 Video**: [`docs/demo_recording.mp4`](docs/demo_recording.mp4)
- 🎞️ **High-Res Animated WebP Capture**: [`docs/demo_recording.webp`](docs/demo_recording.webp)
- 📜 **Complete Narration Script**: [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) *(Hackathon 2m45s Proof Arc)*
- 🎬 **Side-by-Side Shot Matrix**: [`SHOT_PLAN.md`](SHOT_PLAN.md) *(13 visual beats, camera cues, and timings)*
- ✅ **Judge Rubric Checklist**: [`RECORDING_CHECKLIST.md`](RECORDING_CHECKLIST.md)

---

## 📂 Repository Structure

```text
sih2026/
├── backend/                             # Core FastAPI investigation backend
│   ├── api/routes/api_v1.py             # REST endpoints (cases, graph, atlas, ledger, audit)
│   ├── atlas/engine.py                  # ATLAS Counter-Hypothesis reasoning engine
│   ├── attribution/                     # 4-Tier VASP attribution & candidates
│   │   ├── candidates.py                # Known exchange registry (Binance, Coinbase, WazirX, CoinDCX)
│   │   └── evidence_ledger.py           # Cryptographic SHA-256 evidence chain
│   ├── case_management/case.py          # Dynamic per-case state & 3-number scoring
│   ├── external/ncrp_sync.py            # Section 5 NCRP Webhook & Helpline 1930 integration
│   ├── recommendation/engine.py         # Section 91 CrPC freeze action engine
│   ├── trace/engine.py                  # Bounded BFS multi-hop graph exploration
│   └── main.py                          # Application entrypoint & CORS configuration
│
├── blockchain/                          # Multi-chain explorer adapters & indexer
│   ├── adapters/
│   │   ├── eth/client.py                # Etherscan V2 API client with .env key support
│   │   └── btc/client.py                # Blockchair UTXO Bitcoin adapter
│   ├── chain_detection/detect.py        # Automatic BTC / ETH format detection
│   └── normalization/normalize.py       # NormalizedTransaction schemas
│
├── frontend/                            # Next.js 16 App Router UI Console
│   ├── app/
│   │   ├── cases/[id]/overview/         # Interactive React Flow graph & tabs
│   │   ├── cases/[id]/report/           # Institutional Investigation Report Dossier
│   │   ├── ncrp/page.tsx                # Official Indian Govt NCRP 1930 Portal Simulation
│   │   └── queue/QueueView.tsx          # Real-time auto-polling triage queue
│   ├── components/graph/GraphView.tsx   # Custom React Flow nodes & glowing edge canvas
│   └── lib/pdf/generateDossierPdf.ts    # Pure client-side PDF 1.4 binary stream generator
│
├── ml/                                  # Machine Learning Risk & Anomaly Subsystem
│   ├── risk_model/                      # XGBoost risk scoring model (CUDA GPU / CPU)
│   └── anomaly/                         # Isolation Forest transaction velocity anomaly detector
│
├── scenarios/fixtures/                  # 5 Deterministic evaluation scenarios (JSON fixtures)
├── docs/                                # Video recordings, screenshots, and setup handoffs
│   ├── demo_recording.mp4               # Full HD 1080p demo video
│   └── screenshots/                     # Core product UI captures
│
├── DEMO_SCRIPT.md                       # Official Hackathon demo narration script
├── SHOT_PLAN.md                         # Camera & shot-by-shot recording matrix
├── RECORDING_CHECKLIST.md               # Judge rubric & pre-recording checklist
├── TESTING_WALLETS.md                   # Complete test wallet & tx hash directory
├── run_backend.cmd                      # Windows daemon supervisor for FastAPI
└── seed_neo4j_only.py                   # Standalone Neo4j graph fixture seeder
```

---

## 📡 API Reference & Route Map

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/external/ncrp/webhook` | NCRP 1930 Complaint Intake & Zero-Second Automated Triage |
| `GET` | `/cases` | Retrieve all active cases with triage priority and risk metrics |
| `GET` | `/cases/{case_id}` | Detailed case metadata and 3-Number framework metrics |
| `GET` | `/cases/{case_id}/graph` | Nodes and edges for interactive multi-hop graph visualization |
| `GET` | `/cases/{case_id}/attribution` | Leading actionable VASP candidate and corroboration tier |
| `GET` | `/cases/{case_id}/atlas` | ATLAS counter-hypotheses, contradictions, and robustness score |
| `GET` | `/cases/{case_id}/evidence` | Tamper-evident SHA-256 chained evidence records |
| `GET` | `/cases/{case_id}/recommendations`| Section 91 CrPC statutory freeze actions and target custodians |
| `GET` | `/cases/{case_id}/audit` | Immutable forensic audit log of system and investigator actions |

---

## ⚖️ Compliance & Legal Framework

- **Section 91, Code of Criminal Procedure (Cr.P.C.), 1973**: Summons to produce documents or things to custodians of cryptocurrency assets.
- **Information Technology Act, 2000 (Section 69 & 79)**: Statutory compliance obligations for digital intermediaries.
- **Section 65B, Indian Evidence Act, 1872**: Electronic evidence admissibility guaranteed by deterministic rule baselines and SHA-256 cryptographic chain proofs.
- **FIU-IND Anti-Money Laundering (AML) Guidelines**: Verification of reporting entity status for domestic virtual asset service providers (VASP).

---

<div align="center">

**Project VAJRA** — *Built with precision for the Smart India Hackathon 2026*  
Developed by **Team VAJRA** for the **Ministry of Home Affairs / I4C**

</div>
