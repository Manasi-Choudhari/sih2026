# DEMO_SCRIPT.md — Project VAJRA

> **Context**: Smart India Hackathon (SIH 2026) / Law Enforcement Demo Day  
> **Arc**: Problem (Helpline 1930 / Golden 24 Hours) → Zero-Second NCRP Ingestion → Multi-Hop Graph Tracing & Live Etherscan Sync → 3-Tier Confidence Framework → ATLAS Counter-Hypotheses → 1-Click Section 91 CrPC Freeze Order & Verified PDF  
> **Duration**: ~2 minutes 45 seconds (165s) | **Platform**: 1080p 60fps Full HD (16:9) | **Hook**: "When an Indian citizen loses their life savings to a cryptocurrency scam and calls Helpline 1930, investigators have less than 24 hours before those funds cross an exchange threshold and vanish forever."

---

## One Thing This Video Proves

> "After watching this, an evaluator will understand how **Project VAJRA** eliminates the 48-hour manual investigation lag, autonomously tracing suspect wallets across blockchain hops to identify actionable exchanges and generate legally compliant Section 91 CrPC freeze orders in seconds."

---

## Viewer

- **Who they are**: Smart India Hackathon Evaluators, Cyber Police Officers, and Ministry of Home Affairs / I4C Cyber Crime Analysts.
- **Frustration resolved**: Manual blockchain explorers are too slow, cross-chain and peel chains break officer workflows, and generic AI scores lack the legal evidentiary backing required by Indian courts.
- **Decision after watching**: Award top honors for technical excellence, institutional realism, and deployment readiness under the CFCFRMS framework.

---

## Proof Spine

| Element | Description |
|---|---|
| **Starting state** | Browser on `/ncrp` (National Cybercrime Reporting Portal demo gateway) showing a clean citizen complaint filing form. |
| **Action** | Officer/citizen selects **Scenario 1 (Phishing / Seed Drain)** with suspect wallet `0x71C6...` and clicks **"Lodge Complaint & Auto-Triage on VAJRA"**. |
| **Response** | Instant sub-second ingestion, reverse callback generation, and automated assignment into the `/queue` officer triage table. |
| **Outcome** | Multi-hop BFS graph is rendered in `/cases/case_s1/overview` with live Etherscan node synchronization, attributing custody to **Binance (Hot Wallet 14)** with Tier 1 (Strong) confidence. |
| **Verification** | 3-Number Confidence Framework (`0.88` Rule Risk, `95%` Attribution, `0.63` GPU XGBoost ML), **ATLAS** counter-hypotheses evaluation, and instant download of the SHA-256 sealed **Section 91 CrPC PDF Dossier**. |

---

## Truth Map

| Claim | Status | Source / Condition |
|---|---|---|
| Auto-ingestion from NCRP webhook (`POST /api/v1/external/ncrp/webhook`) | ✅ Verified | Tested live in `backend/external/ncrp_sync.py` and `frontend/app/ncrp/page.tsx` |
| Bounded BFS multi-hop graph exploration | ✅ Verified | Rendered via React Flow in `frontend/components/graph/GraphView.tsx` |
| Live Ethereum Mainnet query via API Key | ✅ Verified | Etherscan V2 API adapter with `EXPLORER_API_KEY_ETH` in `blockchain/adapters/eth/client.py` |
| 3-Number Metric Framework (Rules, Attribution, ML) | ✅ Verified | XGBoost CUDA model + deterministic rule engine in `backend/case_management/case.py` |
| ATLAS Counter-Hypothesis Analysis | ✅ Verified | Evaluates alternative scenarios (Permit2 drainer vs OTC settlement) in `backend/atlas/engine.py` |
| Tamper-Evident SHA-256 Evidence Ledger | ✅ Verified | Cryptographic chain verification in `backend/attribution/evidence_ledger.py` |
| Section 91 CrPC Institutional PDF Export | ✅ Verified | Pure client-side PDF 1.4 binary engine in `frontend/lib/pdf/generateDossierPdf.ts` |

---

## What's In / What's Cut

| Element | Decision | Reason |
|---|---|---|
| Mock NCRP Portal (`/ncrp`) & Acknowledgment Slip | ✅ In | Establishes immediate real-world connection to Indian Helpline 1930 / CFCFRMS. |
| Live Auto-refreshing Queue (`/queue`) | ✅ In | Proves zero-second automated pipeline between citizen intake and officer console. |
| Multi-Hop Forensic Graph (`/cases/[id]/overview`) | ✅ In | The primary visual "wow moment" showing suspect path to exchange custody. |
| 3-Number Metric Cards (Rules / Attr / ML) | ✅ In | Demonstrates explainable AI where ML prioritizes but deterministic rules govern legal baseline. |
| ATLAS Counter-Hypotheses Tab | ✅ In | Proves scientific rigor against defense attorney challenges in court. |
| Verified PDF Dossier Download | ✅ In | Tangible legal deliverable required under CrPC Section 91 / IT Act 2000. |
| Deep code-level walk through 40+ python files | ❌ Cut | Distracts from the user journey; mentioned verbally while showing UI. |
| Lengthy terminal build logs | ❌ Cut | Keep the visual focus on the polished product interface. |

---

## Full Narration Script & Visual Beats

### [BEAT 1: THE HIGH-STAKES PROBLEM — 0:00 to 0:22]
- **Visual**: Screen opens on the **National Cybercrime Reporting Portal (`/ncrp`)**, showing the official MHA/I4C tricolor banner and Citizen Financial Cyber Fraud Reporting System badge.
- **Narration**:  
  > *"Over one thousand crore rupees are siphoned into cryptocurrency fraud schemes reported on the National Cybercrime Reporting Portal every year. When a victim dials Helpline 1930, investigating officers face an impossible race against time. Criminals peel, hop, and bridge assets across multiple wallets. By the time an officer manually decodes transactions on a public explorer, the golden twenty-four-hour recovery window is lost. We built Project VAJRA to compress that forty-eight-hour investigation into less than ten seconds."*

---

### [BEAT 2: ZERO-SECOND INTAKE AT NCRP GATEWAY — 0:22 to 0:50]
- **Visual**: Cursor clicks **"Scenario 1: Phishing / Seed Drain"** preset card. Form auto-fills with Complainant Vikramaditya Rao, Suspect Wallet `0x71C6...`, and 2.5 ETH loss. Cursor hits **"Lodge Complaint & Auto-Triage on VAJRA"**. Green acknowledgment slip pops up with Acknowledgment Number `2026/NCRP/DL/...`.
- **Narration**:  
  > *"Here on the NCRP Gateway, citizen complaints enter the CFCFRMS pipeline. With one click, an incident involving a 2.5 Ethereum drain into suspect wallet 0x71C6 is lodged. Instantly, VAJRA's automated webhook activates. Notice the official acknowledgment slip: hops are already bounded, initial risk is scored, and an automated callback notifies the national helpline system."*

---

### [BEAT 3: OFFICER INVESTIGATION QUEUE — 0:50 to 1:12]
- **Visual**: Smooth transition to **`/queue`**. The top row reveals the newly lodged complaint tagged with **"NCRP Gateway Live"** and **"Action Required"**. Officer clicks **"Investigate"**.
- **Narration**:  
  > *"Switching to the VAJRA Officer Console, the complaint appears in real time without a page refresh. High-velocity drains are flagged with high priority. As an investigator, we simply click into the case to access the complete cyber forensics suite."*

---

### [BEAT 4: INTERACTIVE MULTI-HOP GRAPH & ETHERSCAN SYNC — 1:12 to 1:45]
- **Visual**: Screen transitions into `/cases/case_s1/overview`. The interactive React Flow canvas displays the **Victim Node**, the **Intermediary Layering Hop (vitalik.eth)**, and the **Actionable Terminal Node: Binance (Hot Wallet 14)** with glowing edges. Cursor pans and zooms into the terminal node.
- **Narration**:  
  > *"This is VAJRA's live forensics graph. In under a second, our bounded breadth-first search engine explored the transaction tree. For Ethereum wallets, VAJRA utilizes live Etherscan V2 API queries to stream on-chain transaction logs in real time. The stolen funds didn't disappear into thin air—they traversed an intermediary layering wallet and arrived directly at Binance Hot Wallet 14. We now have an actionable custodian."*

---

### [BEAT 5: THE 3-NUMBER CONFIDENCE FRAMEWORK — 1:45 to 2:05]
- **Visual**: Camera zooms gently on the 3 metric cards at the top of the screen:
  - **Rule Risk Score**: `0.88`
  - **Attribution Confidence**: `95% (Strong)`
  - **ML Anomaly Probability**: `0.63` (XGBoost GPU CUDA)
- **Narration**:  
  > *"Unlike black-box systems, VAJRA enforces a strict Three-Number Confidence Framework. First: a deterministic Rule Risk Score of 0.88, ensuring judicial repeatability. Second: an Attribution Confidence of ninety-five percent based on unfragmented flow corroboration. And third: our GPU-accelerated XGBoost ML model evaluates transaction velocity as an anomaly prioritization signal. The AI assists, but deterministic evidence rules the courtroom."*

---

### [BEAT 6: ATLAS COUNTER-HYPOTHESES & AUDIT TRAIL — 2:05 to 2:25]
- **Visual**: Click on the **ATLAS Counter-Hypotheses** tab below the graph. Show competing hypotheses: *Permit2 Signature Relay Drainer*, *Binance Internal Sweep*, and *P2P OTC Settlement*. Then switch to **Evidence Ledger** showing SHA-256 unbroken chain hashes.
- **Narration**:  
  > *"Defense attorneys will always challenge blockchain evidence. That's why we developed ATLAS—our Automated Typology & Legal Argumentation System. ATLAS stress-tests the leading hypothesis against alternative explanations like gasless Permit2 approvals and OTC settlements, proving evidentiary robustness. Every transaction is appended to a cryptographic, tamper-evident SHA-256 ledger."*

---

### [BEAT 7: 1-CLICK SECTION 91 CrPC FREEZE ORDER & PDF DOSSIER — 2:25 to 2:45]
- **Visual**: Click **"Generate Formal Report"** ➔ `/cases/case_s1/report`. Show the institutional legal dossier. Click **"Export Verified PDF"**. The browser instantly downloads `VAJRA_Investigation_Dossier_case_s1.pdf`. Show the downloaded PDF opening with official emblem, stamps, and Section 91 CrPC statutory demand.
- **Narration**:  
  > *"Finally, the operational payoff. With one click on 'Export Verified PDF', VAJRA generates a legally authenticated Investigation Dossier complete with statutory Section 91 CrPC freeze notices for the exchange's legal compliance desk. Project VAJRA transforms fragmented blockchain data into actionable law enforcement outcomes—protecting Indian citizens in the golden hour."*

---

## Alternative Hooks

- **Hook B (Technical / AI angle)**:  
  *"Every crypto tracing tool can show you a transaction tree. But when a case goes to an Indian Sessions Court, statistical AI probabilities get thrown out. Here is how Project VAJRA bridges bleeding-edge graph analytics with Section 91 of the Code of Criminal Procedure."*
- **Hook C (Citizen / MHA angle)**:  
  *"In 2026, cyber fraudsters don't wait for banks to open—they drain wallets in seconds. This is Project VAJRA: India's first real-time crypto fraud attribution core built natively for Helpline 1930."*
