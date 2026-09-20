# VAJRA Demo & Testing Wallet Directory

This document provides verified blockchain coordinates (Suspect Wallets, Victim Wallets, Transaction Hashes, and VASP Targets) to use while testing the **VAJRA Platform** and lodging complaints in the **NCRP / 1930 Portal** (`/ncrp`).

---

## Quick Reference Table

| Typology / Scenario | Asset | Suspect Wallet | Victim Wallet | Initial Tx Hash | Expected Attribution Target |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **1. Direct Phishing & Seed Drain** | `ETH` | `0x71C67930752b516538b1d97767F296aD55836882` | `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` | `0xd81ea91807e318f5c50040524799cec1174a284266e43b2247ac58976d00195b` | **Binance (Hot Wallet 14)** |
| **2. Live Ethereum Etherscan API** | `ETH` | `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` | `0xc8ae53a5c18ad8557b4dc6f827ad2da8fcf30f5b` | *(Queries live Mainnet)* | **Vitalik.eth / Multi-Hop EOA** |
| **3. Indian VASP Deposit (FIU Jurisdiction)** | `ETH` | `0x503828976d22510aad0201ac7ec88293211d23da` | `0x71C67930752b516538b1d97767F296aD55836882` | `0x5c8e2b81498b3941a12a529e39433e14674170364d9f96b528b9d311894d0781` | **CoinDCX India / WazirX** |
| **4. Bitcoin Peel Chain (Multi-Hop)** | `BTC` | `bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh` | `bc1q9victimfakeaddress00188924018241` | `9b7d8c01f3e76a4b5d2c1e0f8a9b6c4d2e1f0a8b7c5d3e2f1a0b9c8d7e6f5a4b` | **Peel Change Heuristic (3 Hops)** |
| **5. Cross-Chain Bridge Evasion** | `BTC` | `bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksns5` | `bc1qvictimtask9948281047192` | `4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b` | **WBTC Liquidity Bridge Gateway** |
| **6. Mixer & Privacy Boundary (Tornado)** | `BTC` | `bc1q5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge` | `bc1qextortvictimwallet11029` | `1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d` | **Mixing Pool Obstruction (ATLAS Alert)** |

---

## Detailed Copy-Paste Test Cases for NCRP Manual Complaint Lodging

### Test Case 1: Ethereum Phishing Seed Drain (Direct Binance Off-Ramp)
> **Recommended for**: Demonstrating end-to-end multi-hop graph generation, rapid VASP attribution, and automated Section 91 CrPC freeze order drafting.

- **Complainant Name**: `Vikramaditya Rao`
- **Contact Number**: `+91-9871043214`
- **Police Station**: `Cyber Police Station New Delhi`
- **Typology / Category**: `Phishing / Seed Drain`
- **Crypto Asset**: `ETH`
- **Crypto Loss Quantity**: `2.5`
- **Reported Loss (INR)**: `650000`
- **Suspect Wallet**:
  ```text
  0x71C67930752b516538b1d97767F296aD55836882
  ```
- **Victim Wallet**:
  ```text
  0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
  ```
- **Initial Transaction Hash**:
  ```text
  0xd81ea91807e318f5c50040524799cec1174a284266e43b2247ac58976d00195b
  ```
- **Incident Brief**:
  ```text
  Complainant clicked a deceptive Telegram staking link. Private keys were drained via Permit2 approval and transferred into a suspect intermediary before landing in Binance Hot Wallet 14.
  ```
- **Expected Results in VAJRA**:
  - **Rule Risk Score**: `0.88`
  - **Attribution Confidence**: `95% (Strong)`
  - **ML Anomaly Probability**: `0.63`
  - **Actionable Custodian**: `Binance (Hot Wallet 14)`

---

### Test Case 2: Live Ethereum Mainnet Wallet (Using `.env` Etherscan API Key)
> **Recommended for**: Demonstrating real-time API integration with Etherscan V2 (`EXPLORER_API_KEY_ETH`) fetching genuine on-chain transaction history.

- **Complainant Name**: `Aarav Mehta`
- **Contact Number**: `+91-9820198765`
- **Police Station**: `Cyber Crime Branch Mumbai`
- **Typology / Category**: `Investment / Ponzi Fraud`
- **Crypto Asset**: `ETH`
- **Crypto Loss Quantity**: `1.0`
- **Reported Loss (INR)**: `260000`
- **Suspect Wallet**:
  ```text
  0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
  ```
- **Victim Wallet**:
  ```text
  0xc8ae53a5c18ad8557b4dc6f827ad2da8fcf30f5b
  ```
- **Initial Transaction Hash**: *(Leave blank or use any Ethereum mainnet tx hash)*
  ```text
  0x5c8e2b81498b3941a12a529e39433e14674170364d9f96b528b9d311894d0781
  ```
- **Incident Brief**:
  ```text
  Victim transferred Ethereum to suspect address after being promised 15% weekly returns in algorithmic arbitrage pool.
  ```
- **Expected Results in VAJRA**:
  - Live query to `https://api.etherscan.io/v2/api?chainid=1`
  - Fetches recent normal transactions and plots real on-chain nodes.

---

### Test Case 3: Indian Domestic Exchange Deposit (FIU-IND Domestic Jurisdiction)
> **Recommended for**: Demonstrating statutory freeze recommendations tailored for domestic registered entities (CoinDCX / WazirX).

- **Complainant Name**: `Rohan Sharma`
- **Contact Number**: `+91-9988776655`
- **Police Station**: `Bengaluru City Cyber Cell`
- **Typology / Category**: `Fake Crypto Exchange`
- **Crypto Asset**: `ETH`
- **Crypto Loss Quantity**: `1.8`
- **Reported Loss (INR)**: `470000`
- **Suspect Wallet (CoinDCX Gateway)**:
  ```text
  0x503828976d22510aad0201ac7ec88293211d23da
  ```
- **Victim Wallet**:
  ```text
  0x71C67930752b516538b1d97767F296aD55836882
  ```
- **Initial Transaction Hash**:
  ```text
  0x5c8e2b81498b3941a12a529e39433e14674170364d9f96b528b9d311894d0781
  ```
- **Incident Brief**:
  ```text
  Funds deposited into an Indian domestic exchange gateway following a social engineering scam.
  ```
- **Expected Results in VAJRA**:
  - **Identified Custodian**: `CoinDCX India Deposit Gateway` (Tier 1 - Strong)
  - **Statutory Notice**: Section 91 CrPC Domestic Production & Freeze Order.

---

### Test Case 4: Bitcoin Peel Chain (UTXO Multi-Hop Layering)
> **Recommended for**: Demonstrating Bitcoin UTXO change output peeling heuristics.

- **Complainant Name**: `Deepak Patel`
- **Contact Number**: `+91-9876501234`
- **Police Station**: `Cyber Police Station Ahmedabad`
- **Typology / Category**: `Investment / Ponzi Fraud`
- **Crypto Asset**: `BTC`
- **Crypto Loss Quantity**: `3.0`
- **Reported Loss (INR)**: `21500000`
- **Suspect Wallet**:
  ```text
  bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
  ```
- **Victim Wallet**:
  ```text
  bc1q9victimfakeaddress00188924018241
  ```
- **Initial Transaction Hash**:
  ```text
  9b7d8c01f3e76a4b5d2c1e0f8a9b6c4d2e1f0a8b7c5d3e2f1a0b9c8d7e6f5a4b
  ```
- **Incident Brief**:
  ```text
  Fake WhatsApp algorithmic trading scheme. Bitcoin peeled into multiple small unspent change outputs across 3 hops to evade single-threshold exchange KYC triggers.
  ```
- **Expected Results in VAJRA**:
  - **Rule Risk Score**: `0.79`
  - **Attribution Confidence**: `72% (Moderate)`
  - **ML Anomaly Probability**: `0.63`

---

### Test Case 5: Mixer / Privacy Protocol Boundary (Tornado Cash / Blender)
> **Recommended for**: Demonstrating the **ATLAS Counter-Hypothesis Engine** and showing how VAJRA handles zero-knowledge mixing boundaries.

- **Complainant Name**: `Ananya Gupta`
- **Contact Number**: `+91-9711223344`
- **Police Station**: `Cyberabad Police Station Hyderabad`
- **Typology / Category**: `Ransomware / Extortion`
- **Crypto Asset**: `BTC`
- **Crypto Loss Quantity**: `4.0`
- **Reported Loss (INR)**: `28800000`
- **Suspect Wallet**:
  ```text
  bc1q5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge
  ```
- **Victim Wallet**:
  ```text
  bc1qextortvictimwallet11029
  ```
- **Initial Transaction Hash**:
  ```text
  1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d
  ```
- **Incident Brief**:
  ```text
  Enterprise ransomware extortion payment. Suspect funds entered zero-knowledge mixing protocol boundary with counter-hypothesis ambiguity.
  ```
- **Expected Results in VAJRA**:
  - **Rule Risk Score**: `0.94` (High Risk)
  - **Attribution Confidence**: `35% (Obstructed Boundary)`
  - **ML Anomaly Probability**: `0.66`
  - **ATLAS Counter-Hypotheses**: Evaluates anonymity set dilution, gas skimming relayers, and corporate treasury operations.

---

## Known Actionable Exchange Wallets Directory

These addresses are hard-coded in the VAJRA Custodial Registry ([`backend/attribution/candidates.py`](backend/attribution/candidates.py)). Any incoming flow to these addresses will be immediately attributed with **Strong (Tier 1)** confidence:

| Entity Name | Chain | Address | Tier | Jurisdiction |
| :--- | :---: | :--- | :---: | :--- |
| **Binance (Hot Wallet 14)** | ETH | `0x28c6c06298d514db089934071355e5743bf21d60` | Strong | Global / Cayman / MLAT |
| **Binance Cold Storage** | ETH | `0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503` | Strong | Global |
| **Coinbase Gateway** | ETH | `0xdfd5293d8e347dff59e4571400a586d1a6ff70a` | Strong | USA / FinCEN |
| **WazirX India Custody** | ETH | `0xa7efae728d2936e78bda97dc267687568dd593f3` | Strong | **India (FIU-IND)** |
| **CoinDCX India Gateway** | ETH | `0x503828976d22510aad0201ac7ec88293211d23da` | Strong | **India (FIU-IND)** |

---

## Demo Step-by-Step Flow

1. **Open NCRP Portal**: Navigate to `http://localhost:3000/ncrp`.
2. **Choose Mode**:
   - For **1-Click Demo**: Click any of the 4 typology cards on top.
   - For **Custom Demo**: Click **`➕ New Complaint / Manual Entry`** and copy-paste values from any Test Case above.
3. **Lodge Complaint**: Click **"Lodge Complaint & Auto-Triage on VAJRA"**.
4. **View Receipt**: Review the official CFCFRMS 1930 Acknowledgment receipt with Complaint Ack No.
5. **Open Case in VAJRA**:
   - Click **"Open Case in VAJRA"** or go to `http://localhost:3000/queue`.
   - Observe the real-time intake in the queue.
   - Click the case row to open `/cases/[case_id]/overview`.
   - Inspect the **Interactive Graph**, **ATLAS Counter-Hypotheses**, **Evidence Ledger**, and **Audit Trail**.
   - Navigate to `/cases/[case_id]/report` and click **"Export Verified PDF"** to download the institutional dossier.
